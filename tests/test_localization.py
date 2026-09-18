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


class TranslationTests(unittest.TestCase):
    def setUp(self):
        self.app = localization.BZ98GuiApp.__new__(localization.BZ98GuiApp)
        self.app.languages = ["French", "German"]
        self.app.lang_codes = {"French": "fr", "German": "de"}
        self.messages = []
        self.app.log = self.messages.append

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


if __name__ == "__main__":
    unittest.main()
