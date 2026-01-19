# BZ98 Localization Bulk Translator

A specialized tool for **Battlezone 98 Redux** modders to quickly translate and format bulk English text into the game's `localization_table.csv` format.

---

## Features

* **Smart Key Generation**: Automatically creates keys based on the context.
    * **Standard Words**: Converted to `names:your_word` (e.g., "Heavy Tank" -> `names:heavy_tank`).
    * **Mission Titles**: Detection for `.bzn` files to create `mission_title:` keys.
* **Bulk Processing**: Paste 50+ lines at once and let the tool handle the rest.
* **Non-Destructive**: The tool only **appends** to your file. It will never delete your existing rows.
* **Quick Jump**: One-click buttons to find the default Steam or GOG installation directories.
* **Multi-Language Support**: Automatically translates into French, German, Spanish, Italian, Russian, and Portuguese using Google Translate.

  <img width="802" height="932" alt="image" src="https://github.com/user-attachments/assets/a9438abf-c575-4899-a53b-68941e0f4fe4" />


---

## Security & Internet Usage

This application requires an **active internet connection**. 

* **How it works**: It sends the English text you provide to the Google Translate API.
* **Privacy**: Only the words you type for translation are sent. No personal data, game files, or system information are ever uploaded.
* **Transparency**: All activity is logged in the "Activity Log" within the app so you can see exactly what is being sent and saved.

---

## Getting Started

### Option 1: Running the Executable (Windows)
If you have the standalone `.exe` version:
1.  Run `BZ98_Localization_Tool.exe`.
2.  Use the **Jump** buttons or **Browse** to select your `localization_table.csv`.
3.  Paste your English words and click **Translate**.

### Option 2: Running from Source (Python)
If you want to run the script directly, you need [Python 3.x](https://www.python.org/) installed.

1.  **Install dependencies**:
    ```bash
    pip install deep-translator
    ```
2.  **Run the script**:
    ```bash
    python bz98_app.py
    ```

---

## Input Formats

### Standard Items
Just paste the English names line-by-line:
```text
Heavy APC
Laser Turret
Repair Station
```
Result Key: names:heavy_apc

### Mission Titles
Use the ~ separator to map a filename to a human-readable title:

```text
play01.bzn~The Playground
mission05.bzn~The Dark Planet
```
Result Key: mission_title:play01.bzn

## Credits
Built for the Battlezone 98 Redux modding community. Special thanks to the creators of the deep-translator library.
