<div align="center">

# Purr Pause 🐱

**A gentle desktop companion that nudges you to follow the 20-20-20 rule.**

[![Release](https://img.shields.io/github/v/release/DavidYuboZhang/purr-pause?include_prereleases&style=flat-square)](https://github.com/DavidYuboZhang/purr-pause/releases/latest)
[![License](https://img.shields.io/github/license/DavidYuboZhang/purr-pause?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/DavidYuboZhang/purr-pause/releases/latest)

**[⬇ Download for Windows](https://github.com/DavidYuboZhang/purr-pause/releases/latest)** · [中文 README](README.md)

</div>

![Demo](docs/demo.gif)

---

## Why

The **20-20-20 rule**: every 20 minutes, look at something 20 feet away for 20 seconds. It works — but willpower is unreliable, so Purr Pause sends a cat to walk gently across the center of your screen every 20 minutes to remind you.

Design principles:

- **Gentle**: the cat doesn't seize your screen. It walks in, sits a moment, walks out.
- **Quiet**: no network requests, no telemetry, no ads.
- **Dismissable**: quit from the tray any time. No "just five more minutes" guilt.

## Screenshots

| Tray menu | Settings window |
|---|---|
| ![Tray menu](docs/screenshots/tray-menu.png) | ![Settings window](docs/screenshots/settings-window.png) |

| Rest notification | First-run SmartScreen |
|---|---|
| ![Rest notification](docs/screenshots/rest-notification.png) | ![SmartScreen bypass](docs/screenshots/smartscreen-bypass.png) |

## Install (Windows 10 / 11)

1. Download `PurrPause-<version>-windows.exe` from the [Releases page](https://github.com/DavidYuboZhang/purr-pause/releases/latest).
2. Double-click to run.
3. On first launch, Windows shows a blue **"Windows protected your PC"** SmartScreen warning. This appears for any small unsigned app — Purr Pause isn't code-signed (a signing certificate costs $99–300/year, which is unjustifiable at this stage).
4. Click **"More info" → "Run anyway"** (see the annotated SmartScreen screenshot above for the exact buttons to click).
5. The app lives in your system tray as a 🐱 icon. That means it's running.

## macOS support

macOS builds are **not yet published**. They are planned for a v0.1.x patch. To run from source today:

```bash
git clone https://github.com/DavidYuboZhang/purr-pause.git
cd purr-pause
pip install -r requirements.txt
python main.py
```

## Customize

Right-click the 🐱 tray icon → "Settings" to adjust:

- **Work interval (minutes)** — default 20
- **Rest duration (seconds)** — default 20

The settings dialog does not edit image paths. Advanced users can quit the app and edit `cat_image_path` in the user configuration: leave it empty for the built-in thumbnail, or supply an absolute path to a PNG, JPG, JPEG, or WebP still image. This changes only the round thumbnail in the reminder card, not the separate walking-cat animation. A custom GIF does not replace the bundled still thumbnail while that thumbnail is present.

The Windows executable uses `%APPDATA%\PurrPause\config.json`; source runs use `config.json` in the repository root. These configurations are independent.

## Privacy & Security

Purr Pause is a plain, well-behaved local tool. The source is fully open; here's a quick rundown of common concerns:

- **No network**: v0.1.x makes zero network requests after launch — no telemetry, no update check, no crash reporting. Unplug the network and the app behaves identically.
- **No registry edits**: the runtime never reads or writes the Windows registry.
- **No autostart**: you launch it manually each time; uninstall is just deleting the `.exe`.
- **No file deletion**: the runtime never calls `os.remove` / `shutil.rmtree` or any file-removal API.
- **Explicit configuration locations**: the Windows executable writes `%APPDATA%\PurrPause\config.json`; source runs write `config.json` in the repository root.

Source is auditable on [GitHub](https://github.com/DavidYuboZhang/purr-pause). If you want extra reassurance, drop the .exe onto [VirusTotal](https://www.virustotal.com).

v0.2 will add an opt-in "check GitHub Releases for updates on launch" feature, with a settings toggle and the target domain (`api.github.com`) disclosed up-front.

## Feedback

- Bugs / feature requests: [GitHub Issues](https://github.com/DavidYuboZhang/purr-pause/issues)
- Email: yubo.david.zhang@gmail.com

## Development

```bash
git clone https://github.com/DavidYuboZhang/purr-pause.git
cd purr-pause
pip install -r requirements.txt
python -m pytest -v -ra  # unit and integration tests
python main.py     # run from source
```

You can also run `python -m purr_pause`. Runtime modules live in `purr_pause/`; Windows Conda setup, module responsibilities and configuration paths are described in [PROJECT.md](PROJECT.md) (Chinese). Actual validation results are tracked in [STATUS.md](STATUS.md).

Build a release locally:

```bash
python scripts/build_dist.py
# → dist/PurrPause-{VERSION}-windows.exe
```

## Roadmap

- ✅ **v0.1.0** — first public release (Windows single-file .exe)
- ⏳ **v0.1.x** — macOS .dmg build
- ⏳ **v0.2** — in-app update check (queries GitHub Releases on launch)
- 🤔 Later — autostart, sound notifications, rest-session statistics

Full history: [CHANGELOG.md](CHANGELOG.md).

## Credits

- Cat source video: generated with ByteDance 即梦AI (Jimeng / Dreamina)
- Chinese font: [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) (SIL OFL 1.1)

Full attribution in [ASSETS.md](ASSETS.md).

## License

[MIT](LICENSE) © 2026 Yubo Zhang
