import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import localization


class OdfDisplayNameTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.app.log = lambda _message: None

    def _write_odf(self, text, filename="internal_unit_id.odf"):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / filename
        path.write_text(text, encoding="utf-8")
        return path

    def test_extracts_player_visible_unit_name(self):
        path = self._write_odf(
            """
            [GameObjectClass]
            classLabel = "wingman"
            aiName = "internal_ai_name"
            unitName = "Thunderbolt"
            """
        )

        self.assertEqual(self.app.extract_unit_name(path), "Thunderbolt")

    def test_does_not_fall_back_to_internal_odf_filename(self):
        path = self._write_odf(
            """
            [GameObjectClass]
            classLabel = "wingman"
            aiName = "internal_ai_name"
            """
        )

        self.assertIsNone(self.app.extract_unit_name(path))

    def test_ignores_commented_out_unit_name(self):
        path = self._write_odf(
            """
            // unitName = "Old Internal Name"
            classLabel = "wingman"
            """
        )

        self.assertIsNone(self.app.extract_unit_name(path))


class ExistingKeyEncodingTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.messages = []
        self.app.log = self.messages.append
        self.app._translator_cache = {}
        self.app._last_translation_request = 0.0
        self.app._translation_min_interval = 0.0

    def test_reads_keys_when_translated_columns_contain_legacy_bytes(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "localization_table.csv"
        path.write_bytes(
            b"names:eviscerator~Eviscerator~\xc8viscerateur\n"
            b"names:scout~Scout~Scout\n"
        )

        class CsvPath:
            def get(self_inner):
                return str(path)

        self.app.csv_path = CsvPath()

        self.assertEqual(
            self.app.get_existing_keys(),
            {"names:eviscerator", "names:scout"},
        )
        self.assertEqual(self.messages, [])


class TranslationTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.app.languages = ["French", "German"]
        self.app.lang_codes = {"French": "fr", "German": "de"}
        self.messages = []
        self.app.log = self.messages.append
        self.app._translator_cache = {}
        self.app._last_translation_request = 0.0
        self.app._translation_min_interval = 0.0

    def test_translate_text_returns_real_target_results(self):
        class FakeTranslator:
            def __init__(self, source, target):
                self.source = source
                self.target = target

            def translate(self, text):
                return f"{self.target}:{text}"

        with patch.object(localization, "GoogleTranslator", FakeTranslator), patch.object(
            localization.time, "sleep", lambda _seconds: None
        ):
            translated = self.app.translate_text("Scout")

        self.assertEqual(translated, ["fr:Scout", "de:Scout"])

    def test_translation_failure_raises_instead_of_returning_english(self):
        class FailingTranslator:
            def __init__(self, source, target):
                pass

            def translate(self, text):
                raise RuntimeError("translator unavailable")

        with patch.object(localization, "GoogleTranslator", FailingTranslator), patch.object(
            localization.time, "sleep", lambda _seconds: None
        ):
            with self.assertRaises(RuntimeError):
                self.app.translate_text("Scout", retries=2)

    def test_rate_limit_uses_longer_cooldown_before_retry(self):
        attempts = {"count": 0}
        sleeps = []

        class ThrottledTranslator:
            def __init__(self, source, target):
                pass

            def translate(self, text):
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise RuntimeError("429 Too many requests")
                return "translated"

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(localization, "GoogleTranslator", ThrottledTranslator), patch.object(
            localization.time, "sleep", sleeps.append
        ):
            translated = self.app.translate_text("Scout", retries=2)

        self.assertEqual(translated, ["translated"])
        self.assertIn(15, sleeps)

    def test_persistent_rate_limit_raises_circuit_breaker_error(self):
        class AlwaysThrottledTranslator:
            def __init__(self, source, target):
                pass

            def translate(self, text):
                raise RuntimeError("429 Too many requests")

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(
            localization, "GoogleTranslator", AlwaysThrottledTranslator
        ), patch.object(localization.time, "sleep", lambda _seconds: None):
            with self.assertRaises(localization.TranslationRateLimitError):
                self.app.translate_text("Scout", retries=2)

    def test_reuses_translator_instances_for_repeated_work(self):
        created = []

        class ReusedTranslator:
            def __init__(self, source, target):
                created.append(target)
                self.target = target

            def translate(self, text):
                return f"{self.target}:{text}"

        with patch.object(localization, "GoogleTranslator", ReusedTranslator), patch.object(
            localization.time, "sleep", lambda _seconds: None
        ):
            self.app.translate_text("Scout")
            self.app.translate_text("Tank")

        self.assertEqual(created, ["fr", "de"])


class CloudBatchTranslationTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.app.languages = ["French", "German"]
        self.app.lang_codes = {"French": "fr", "German": "de"}
        self.messages = []
        self.app.log = self.messages.append

    def test_321_names_use_one_request_per_language(self):
        texts = [f"Unit {index}" for index in range(321)]
        calls = []

        class DummyCredentials:
            token = "test-token"

        class FakeResponse:
            status_code = 200
            text = ""

            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        def fake_post(url, headers, json, timeout):
            calls.append(
                {
                    "url": url,
                    "headers": headers,
                    "json": json,
                    "timeout": timeout,
                }
            )
            target = json["targetLanguageCode"]
            return FakeResponse(
                {
                    "translations": [
                        {"translatedText": f"{target}:{text}"}
                        for text in json["contents"]
                    ]
                }
            )

        with patch.object(
            self.app,
            "_load_cloud_credentials",
            return_value=("battlezone-test", DummyCredentials()),
        ), patch.object(localization.requests, "post", side_effect=fake_post):
            translated = self.app.translate_batch_cloud(texts)

        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["json"]["contents"], texts)
        self.assertEqual(calls[1]["json"]["contents"], texts)
        self.assertEqual(
            [call["json"]["targetLanguageCode"] for call in calls],
            ["fr", "de"],
        )
        self.assertEqual(translated[0], ["fr:Unit 0", "de:Unit 0"])
        self.assertEqual(
            translated[-1],
            ["fr:Unit 320", "de:Unit 320"],
        )

    def test_cloud_response_count_must_match_source_count(self):
        class DummyCredentials:
            token = "test-token"

        class FakeResponse:
            status_code = 200
            text = ""

            def json(self):
                return {"translations": [{"translatedText": "only one"}]}

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(
            self.app,
            "_load_cloud_credentials",
            return_value=("battlezone-test", DummyCredentials()),
        ), patch.object(localization.requests, "post", return_value=FakeResponse()):
            with self.assertRaises(localization.CloudTranslationError):
                self.app.translate_batch_cloud(["Scout", "Tank"])

    def test_large_input_is_chunked_only_when_cloud_limits_require_it(self):
        texts = ["x" * 100 for _ in range(301)]
        chunks = self.app._chunk_cloud_contents(texts)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 300)
        self.assertEqual(len(chunks[1]), 1)


class FreeHttpBatchTranslationTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.app.languages = ["French", "German"]
        self.app.lang_codes = {"French": "fr", "German": "de"}
        self.messages = []
        self.app.log = self.messages.append

    def test_321_short_names_use_one_request_per_language(self):
        texts = [f"Unit {index}" for index in range(321)]
        calls = []

        class FakeResponse:
            status_code = 200
            text = ""

            def __init__(self, translated):
                self._translated = translated

            def json(self):
                return {"sentences": [{"trans": self._translated}]}

        def fake_post(url, params, data, headers, timeout):
            calls.append(
                {
                    "url": url,
                    "params": params,
                    "data": data,
                    "headers": headers,
                    "timeout": timeout,
                }
            )
            target = params["tl"]
            translated = "\n".join(
                f"{target}:{line}" for line in data["q"].split("\n")
            )
            return FakeResponse(translated)

        with patch.object(localization.requests, "post", side_effect=fake_post):
            translated = self.app.translate_batch_free_http(texts)

        self.assertEqual(len(calls), 2)
        self.assertEqual(
            [call["params"]["tl"] for call in calls],
            ["fr", "de"],
        )
        self.assertEqual(calls[0]["data"]["q"], "\n".join(texts))
        self.assertEqual(translated[0], ["fr:Unit 0", "de:Unit 0"])
        self.assertEqual(
            translated[-1],
            ["fr:Unit 320", "de:Unit 320"],
        )

    def test_free_http_uses_post_form_payload(self):
        class FakeResponse:
            status_code = 200
            text = ""

            def json(self):
                return {"sentences": [{"trans": "Char\nRéservoir"}]}

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(
            localization.requests, "post", return_value=FakeResponse()
        ) as post:
            translated = self.app.translate_batch_free_http(["Tank", "Reservoir"])

        self.assertEqual(translated, [["Char"], ["Réservoir"]])
        _, kwargs = post.call_args
        self.assertEqual(
            kwargs["url"] if "url" in kwargs else post.call_args.args[0],
            "https://translate.googleapis.com/translate_a/single",
        )
        self.assertEqual(kwargs["data"], {"q": "Tank\nReservoir"})
        self.assertEqual(kwargs["params"]["client"], "gtx")
        self.assertEqual(kwargs["params"]["dt"], "t")
        self.assertEqual(kwargs["params"]["dj"], "1")

    def test_line_boundary_mismatch_retries_with_markers(self):
        calls = []

        class FakeResponse:
            status_code = 200
            text = ""

            def __init__(self, translated):
                self._translated = translated

            def json(self):
                return {"sentences": [{"trans": self._translated}]}

        def fake_post(url, params, data, headers, timeout):
            calls.append(data["q"])
            if "[[BZ0]]" not in data["q"]:
                return FakeResponse("Char Réservoir")
            return FakeResponse("[[BZ0]] Char\n[[BZ1]] Réservoir")

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(localization.requests, "post", side_effect=fake_post):
            translated = self.app.translate_batch_free_http(["Tank", "Reservoir"])

        self.assertEqual(len(calls), 2)
        self.assertEqual(translated, [["Char"], ["Réservoir"]])

    def test_429_fails_closed_without_silent_fallback(self):
        class FakeResponse:
            status_code = 429
            text = "Too Many Requests"

            def json(self):
                return {}

        self.app.languages = ["French"]
        self.app.lang_codes = {"French": "fr"}

        with patch.object(
            localization.requests, "post", return_value=FakeResponse()
        ):
            with self.assertRaises(localization.FreeTranslationError):
                self.app.translate_batch_free_http(["Scout", "Tank"])


if __name__ == "__main__":
    unittest.main()
