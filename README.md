# BZ98 Localization Tool & ODF Scanner

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
    * Automatically extracts `unitName` from `.odf` files.
    * Uses file names as fallbacks if `unitName` is missing.
* **Smart De-duplication**: Automatically checks your existing CSV and skips any keys that are already present.
* **Smart Key Generation**: 
    * **Standard Words**: Converted to `names:your_word`.
    * **Mission Titles**: Detection for `.bzn` files to create `mission_title:` keys.
* **Multi-Language Support**: Translates into French, German, Spanish, Italian, Russian, and Portuguese using Google Translate.
* **Progress Tracking**: Visual feedback during large batch translations.

---

## 🛠 Getting Started

### Option 1: Running the Executable
Download the latest version from the [Releases](https://github.com/GrizzlyOne95/Battlezone98Redux_LocalizationTool/releases) page for Windows, Linux, or macOS.

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

When the user explicitly requests a translation, the text selected for translation is sent to Google Translate through the open-source `deep-translator` dependency. Google's privacy policy is available at https://policies.google.com/privacy. This project does not intentionally collect application telemetry.

Official Windows release binaries are built from this repository using GitHub Actions. Once SignPath Foundation signing is enabled for the project, version-tagged Windows releases are submitted from the GitHub-hosted build pipeline to SignPath for Authenticode signing and require release approval before publication.

---

## 📜 Credits
Built for the Battlezone 98 Redux modding community. Features inspired by the Workshop Uploader aesthetics.

`BZONE.ttf` was created by **ScrapPool** as a fan-made typeface inspired by the Battlezone visual style and was provided for free use. It is not presented as an extracted game font. See `THIRD_PARTY_NOTICES.md` for provenance and licensing notes.
