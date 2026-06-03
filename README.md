<p align="center">
  <img src="favicon/android-chrome-192x192.png" width="114" height="114" alt="Pyrics Logo" />
</p>

<h1 align="center">Pyrics</h1>
<p align="center">
  <b>Python Lyrics Player</b>
</p>

<p align="center">
  <a href="https://github.com/abdipr/pyrics/releases/latest/download/pyrics.exe">
    <img src="https://img.shields.io/badge/Download_Latest-pyrics.exe-blue?style=for-the-badge&logo=windows" alt="Download pyrics.exe" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/abdipr/pyrics/stargazers"><img src="https://img.shields.io/github/stars/abdipr/pyrics?style=flat-square&color=black" alt="Stars" /></a>
  <a href="https://github.com/abdipr/pyrics/network/members"><img src="https://img.shields.io/github/forks/abdipr/pyrics?style=flat-square&color=black" alt="Forks" /></a>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<p align="center">
  A minimalistic, modern, and monochrome floating desktop lyrics visualizer built in Python with PyQt6. Designed as an artistic desktop installation rather than a traditional media player, Pyrics parses synchronized TTML subtitle files and floats lyrics upward across the screen in dynamic, frameless 4:3 aspect ratio panels.
</p>

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🚀 Installation & Setup](#-installation--setup)
- [📦 Bundling to Standalone Executable (.exe)](#-bundling-to-standalone-executable-exe)
- [🌱 Contributing](#-contributing)
- [✨ Support](#-support)
- [⚖️ License](#%EF%B8%8F-license)

---

## ✨ Key Features

- **Word-by-word Highlight (Position-Preserving)**: Words emerge incrementally inside a 4:3 aligned panel. Future words remain colored to match the background to guarantee the visible text stays centered without shifts.
- **Alternating Floating Layout**: Successive lyric lines spawn alternately on the left and right sides of your desktop screens with organic offsets to avoid robotic repetition.
- **Smart Overlap Stacking**: A collision-preventing physics velocity calculator adjusts spawn positions dynamically, ensuring overlapping fast-paced lines never collide.
- **Contrast Themes & Custom Colors**: Supports a solid black theme, a white inverted theme, a random mix theme, or customizable text and background colors via hex inputs and color pickers.
- **Timeline Engine & Seek Controls**: Play, pause, stop, seek (slider scrubbing), and adjust playback speed scales (`0.5x`, `1.0x`, `1.25x`, `1.5x`, `2.0x`).
- **Import/Export Config**: Save your typography, side margins, colors, and speeds to a JSON file and import them back at any time.

---

## 🚀 Installation & Setup

### Prerequisites

Make sure you have **Python 3.11** or newer installed.

### 1. Clone the Repository

```bash
git clone https://github.com/abdipr/pyrics.git
cd pyrics
```

### 2. Install Dependencies

Install PyQt6:

```bash
pip install PyQt6
```

### 3. Run the Application

Start the lyrics controller:

```bash
python main.py
```

---

## 📦 Bundling to Standalone Executable (.exe)

You can easily compile Pyrics into a single portable `.exe` binary for Windows.

Double-click the **`build.bat`** script in the project root folder. It will:

1. Automatically install `PyInstaller`.
2. Compile and package the application files.
3. Bundle assets (`favicon` and `fonts`).
4. Generate the executable at `dist/main.exe`.

---

## 🌱 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

---

## ✨ Support

If you like this project, please star on this repository, thank you ⭐<br>
You can support me by:<br>
<a href="https://trakteer.id/abdipr" target="_blank"><img id="wse-buttons-preview" src="https://cdn.trakteer.id/images/embed/trbtn-red-1.png?date=18-11-2023" height="40" style="border: 0px; height: 40px;" alt="Trakteer Saya"></a>
<a href="https://saweria.co/abdipr" target="_blank"><img height="42" src="https://files.catbox.moe/fwpsve.png"></a>
<a href="https://www.buymeacoffee.com/abdipr" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: auto !important;" ></a>

---

## ⚖️ License

This project is licensed under the `MIT License`. See the [LICENSE](LICENSE) file for more information.
