# Detective Game — Crime Scene Detective

> A Windows 95–styled crime-scene guessing game in pygame-ce, plus a terminal variant and a character-sketch generator minigame — early-stage hobby project.

Pick the guilty suspect by matching the trait clue to one of four suspect cards, rendered in a retro Windows GUI. The repo also contains an alternate text-based "Detective OS" terminal version and a minigame that shells out to a PSD character generator script and displays the result.

---

## 📜 Table of Contents

- [✨ Features](#-features)
- [🚀 Installation](#-installation)
- [📖 Usage](#-usage)
- [🏗️ Architecture](#-architecture)
- [🛠️ Technologies Used](#-technologies-used)
- [⚠️ Limitations](#-limitations)
- [📜 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📧 Contact](#-contact)

---

## ✨ Features

### GUI game (`backend/game.py`)
- **Retro Windows 95 interface** — classic grey palette, raised bevel buttons with real-time press animation, title-bar windows, all drawn in pygame.
- **Suspect deduction** — each new case picks a random guilty suspect and shows a case brief listing that suspect's traits; click the matching card to solve or fail the case.
- **Settings screen** — sound toggle persisted to `data/settings.json`.
- **Composite Sketch Laboratory** — a minigame screen that runs `src/test_character_generator.py` via `subprocess`, loads the newest PNG it writes to `src/output/`, and displays it next to a metadata panel.
- **Logging** — runtime diagnostics written to `logs/game_errors.txt`.

### Terminal variant (`backend/main_menu.py`)
- **Detective OS console** — menu-driven text interface: open case files, view generated suspect profiles (name, occupation, likes/dislikes, alibi, inventory), advance turns (with random events), and launch the same generator minigame.

### Packaging
- **PyInstaller build** — `backend/build_exe.py` produces a one-file, no-console `game.py` executable with `src/` bundled as data.

---

## 🚀 Installation

### Prerequisites
- Windows (the launcher and paths assume Windows; pygame-ce works elsewhere but `launch_game.bat` does not)
- Python 3.x

### Steps
1. Install dependencies: `pip install -r backend/requirements.txt` (pins: `pygame-ce>=2.5.0`, `pyinstaller>=6.0.0`, `pillow>=10.0.0`, `arabic-reshaper>=3.0.0`, `python-bidi>=0.4.2`).
2. Run `launch_game.bat` from the repo root, or `python backend/game.py` for the GUI / `python backend/main_menu.py` for the terminal version.
3. For the minigame, `src/test_character_generator.py` must exist (it is referenced but is not present in this snapshot — see Limitations).

---

## 📖 Usage

### Play the GUI game
- **START INVESTIGATION** — generates a new case: four suspects with portrait images and trait lists; the case brief reveals the guilty suspect's traits.
- **LAUNCH COMPOSITE GEN** — opens the generator lab; **REGENERATE CHARACTER Sketch** reruns the script.
- **AUDIO CONFIGURATION** — toggles the sound flag stored in `data/settings.json`.

### Play the terminal version
- Run `python backend/main_menu.py` and choose 1–5 from the menu; options 1–3 drive the `engine` package's case/profile/event logic.

### Build an executable
- `python backend/build_exe.py` → PyInstaller onefile build of `game.py` with `src/` as bundled data.

---

## 🏗️ Architecture

```
detective_game/
├── launch_game.bat          # Windows launcher → python backend/game.py
├── detective_game.json      # empty GDevelop project descriptor (unused remnant)
├── data/settings.json       # persisted sound toggle
├── logs/game_errors.txt     # runtime diagnostics
├── src/                     # all art assets + generator script target
│   ├── Male.psd, Female.psd
│   ├── Noir_Men_Portraits/  # suspect portrait PNGs (+ png_1024 variants)
│   ├── RetroWindowsGUI/     # Windows-95-style UI sprites + license/readme
│   ├── Sprites/             # background/icon sprites
│   └── test_character_generator.py   # referenced by the minigame (absent here)
└── backend/
    ├── game.py              # main pygame GUI loop (1000×700 @ 60 FPS)
    ├── main_menu.py         # terminal "Detective OS" variant
    ├── build_exe.py         # PyInstaller build script
    ├── requirements.txt
    └── engine/
        ├── game_controller.py    # DetectiveGameController / NarrativeGameController
        ├── profile_gen.py        # suspect profile generation
        ├── inventory_gen.py      # per-suspect inventory generation
        ├── event_system.py       # random turn events
        └── anime_minigame.py     # generator minigame entry point
```

### Data Flow
1. `game.py` loads GUI textures and portraits from `src/`, reads `data/settings.json`.
2. "START INVESTIGATION" builds four suspect cards (portrait + trait combo), picks a guilty one at random, and shows the trait clue.
3. Clicking a suspect compares IDs → "CASE SOLVED" / "CASE LOST" → game-over screen.
4. The minigame button shells out to `src/test_character_generator.py` and displays the newest PNG in `src/output/`.

---

## 🛠️ Technologies Used

### Core
- **Python** - game logic and engine
- **pygame-ce** (`pygame`) - rendering, input, windowing, mixer
- **Pillow** - image handling dependency
- **arabic-reshaper / python-bidi** - declared in requirements (text shaping support)

### Packaging / Tooling
- **PyInstaller** - one-file executable build (`build_exe.py`)
- **GDevelop** - `detective_game.json` is an empty leftover project descriptor, not part of the runtime

---

## ⚠️ Limitations

### Feature gaps
- **Minimal gameplay loop** — one case = four suspects, one clue, one click; there is no evidence inventory UI, interrogation, or multi-step deduction in the GUI path (the terminal variant has richer profile/event scaffolding via `engine/`, but it is text-only).
- **Clue is self-revealing** — the case brief literally lists the guilty suspect's traits, so matching is trivial by design.
- **Suspect assignment is superficial** — `game.py`'s GUI suspects use fixed trait combos cycled across four cards; the richer `engine/` generation (profiles, inventories, guilty index) is used by the terminal controller, not wired into the GUI cards.

### Technical
- **`test_character_generator.py` absent** — both `game.py` and `game_controller.py` reference `src/test_character_generator.py`, which is not in this snapshot; the minigame button will log an error and show "No character file initialized".
- **`main_menu.py` may not import cleanly** — it imports `NarrativeGameController`, while `game_controller.py` defines `DetectiveGameController` (verify before use).
- **Windows-oriented** - `launch_game.bat` and several path assumptions target Windows.
- **`detective_game.json` is an empty GDevelop stub** — no scenes/layouts; safe to ignore.

### Testing Limitations
- **What a clone can re-check**: `python backend/game.py` launches the GUI on a machine with the requirements installed; menu/settings/game-over flow is self-contained.
- **What a clone cannot re-check**: the generator minigame (missing script), the PyInstaller build output, and any audio behavior depend on assets/hardware not fully verifiable from the repo.

---

## 📜 License

Detective Game is proprietary software — see [LICENSE](LICENSE) for the full terms.

**Copyright © 2026 AliesterEroan. All rights reserved.**

This software is provided for personal, non-commercial use only. Commercial use, redistribution, modification, and sublicensing are prohibited without explicit written permission. The copyright holder may distribute copies through the project's official GitHub Releases page; third parties may not host, mirror, or redistribute this software.

For licensing inquiries, open an issue at <https://github.com/AliesterEroan/detective_game/issues>.

---

## 🙏 Acknowledgments

- **Noir Men Portraits** (`src/Noir_Men_Portraits/`) — third-party character portrait pack; includes its own `LICENSE.txt`/`README.txt`.
- **RetroWindowsGUI** (`src/RetroWindowsGUI/`) — Windows-95-style UI sprite kit with `ExampleProject.unitypackage` and license/readme files.
- **Free Game Menu Music Pack** — license PDF included under `src/`.

---

## 📧 Contact

- **GitHub**: [AliesterEroan/detective_game](https://github.com/AliesterEroan/detective_game)
- **Issues**: [Create an issue](https://github.com/AliesterEroan/detective_game/issues)

---

*Built with ❤️ by AliesterEroan*
