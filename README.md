# Battlezone Localization Tool

A premium, automated localization tool for **Battlezone 98 Redux** modders. Quickly translate bulk English text or scan your custom ODF folders to automatically collect and translate unit names into the game's `localization_table.csv`.

<img width="902" height="982" alt="image" src="https://github.com/user-attachments/assets/a97ed2b9-e43f-4524-94cf-8a669c7dc2cb" />

---

## 🎨 New Premium Aesthetics
The tool has been overhauled to match the **Battlezone Workshop Uploader** style, featuring:
* **Dark Mode**: Sleek black and neon green high-contrast UI.
* **Custom Font**: Uses the fan-made `BZONE` font by ScrapPool, provided for free use and inspired by the Battlezone visual style.
* **Tabbed Interface**: Cleanly separated tasks for manual entry and automated scanning.

---

## 🚀 Features

* **ODF Scanner (NEW)**: 
    * Point the tool at any mod folder.
    * Extracts only the player-visible `unitName` value from `.odf` files.
    * Skips ODFs without `unitName` instead of treating internal filenames or identifiers as localization text.
* **Smart De-duplication**: Automatically checks your existing CSV and skips any keys that are already present.
* **Smart Key Generation**: 
    * **Standard Words**: Converted to `names:your_word`.
    * **Mission Titles**: Detection for `.bzn` files to create `mission_title:` keys.
* **Multi-Language Support**: ODF bulk translation uses the official **Google Cloud Translation v3** `translateText` API with `contents[]` batching. A normal scan is sent as one request per target language (six API calls total for six languages), with automatic chunking only when Google's synchronous request limits require it. The Manual Translate tab keeps the credential-free `deep-translator` path as a fallback.
* **Progress Tracking**: Visual feedback during large batch translations.

---

## 🛠 Getting Started

### Option 1: Running the Executable
Download the latest platform archive from the [Releases](https://github.com/GrizzlyOne95/Battlezone98Redux_LocalizationTool/releases) page.

The executable name is intentionally stable and versionless:

- Windows: `BZLocalizationTool.exe`
- Linux/macOS: `BZLocalizationTool`

Release archives carry the version, for example `Battlezone98Redux_LocalizationTool-v2.1-windows.zip`.

### Windows application metadata

Official Windows builds use the shared **Battlezone Modding Tools** product identity:

```text
FileDescription: Battlezone Localization Tool
ProductName: Battlezone Modding Tools
CompanyName: GrizzlyOne95
OriginalFilename: BZLocalizationTool.exe
```

`FileVersion` and `ProductVersion` are derived from the release tag.

### Option 2: Running from Source
1. **Clone the repo**:
   ```bash
   git clone https://github.com/GrizzlyOne95/Battlezone98Redux_LocalizationTool.git
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the script**:
   ```bash
   python localization.py
   ```

### Google Cloud setup for ODF bulk translation

ODF bulk translation intentionally uses the official Cloud Translation v3 API instead of sending hundreds or thousands of anonymous web-translation requests.

1. Create or select a Google Cloud project, enable **Cloud Translation API**, and enable billing for that project.
2. Authenticate with either:
   - a service-account JSON file selected in the app, or
   - Google Application Default Credentials (ADC).
3. Enter the Google Cloud **Project ID** in the app. If the selected credentials file contains the project ID, the tool can detect it automatically.
4. Click **COLLECT & TRANSLATE ALL** after scanning ODFs.

The tool gathers all untranslated names first, then submits the names together in `contents[]` for each target language. For a 321-name scan that fits the synchronous size limit, French is one request, German is one request, and so on.

You can also preconfigure the executable with `GOOGLE_CLOUD_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS`.

**Do not commit service-account JSON credentials to this repository or to a mod project.**

---

## 📂 Input Formats

### ODF Scanning
Simply use the **ODF Scanner** tab, browse to your folder, and click **Scan**. The tool handles the extraction and formatting for you.

### Manual Mode
Paste English names line-by-line.
* **Normal**: `Heavy APC` -> `names:heavy_apc`
* **Missions**: `play01.bzn~The Playground` -> `mission_title:play01.bzn`

---

## Code signing policy

Free code signing is provided by [SignPath.io](https://signpath.io/), certificate by [SignPath Foundation](https://signpath.org/).

### Team roles

* **Author / committer:** [GrizzlyOne95](https://github.com/GrizzlyOne95)
* **Reviewer:** GrizzlyOne95 reviews changes submitted by external contributors before merge.
* **Approver:** GrizzlyOne95 approves official release signing requests.

### Privacy

This program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it.

When the user explicitly runs **ODF bulk translation**, the selected source names are sent to the official Google Cloud Translation v3 API using the Google Cloud credentials configured by the user. The **Manual Translate** tab uses the open-source `deep-translator` dependency as a credential-free fallback. This project does not intentionally collect application telemetry or store Google Cloud credential contents.

Official Windows release binaries are built from this repository using GitHub Actions. Once SignPath Foundation signing is enabled for the project, version-tagged Windows releases are submitted from the GitHub-hosted build pipeline to SignPath for Authenticode signing and require release approval before publication.

---

## 📜 Credits
Built for the Battlezone 98 Redux modding community. Features inspired by the Workshop Uploader aesthetics.

`BZONE.ttf` was created by **ScrapPool** as a fan-made typeface inspired by the Battlezone visual style and was provided for free use. It is not presented as an extracted game font. See `THIRD_PARTY_NOTICES.md` for provenance and licensing notes.
