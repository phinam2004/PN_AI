# 🤖 Maya AI 1.2 (Cross-Platform Next-Gen Edition)

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)](https://github.com/phinam2004/PN_AI)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-brightgreen?style=flat-square)](https://python.org)
[![Design](https://img.shields.io/badge/Design%20Standard-Google%20Labs%20Stitch-orange?style=flat-square)](file:///c:/Users/PC/Documents/GitHub/PN_AI/DESIGN.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)

**Maya AI** is an advanced, ultra-responsive personal AI voice assistant with an event-driven architecture, cross-platform hardware abstraction, smart conversational memory, and a modern Cockpit HUD interface.

---

## 🌟 10 Major Feature Upgrades in v1.2

### 1. 🌍 Windows Support
- Native Windows support using PowerShell and OS API abstraction (`core/platform_adapter.py`).
- Windows-compatible TTS via Microsoft Edge Neural Voices or SAPI5 fallback.
- Application launching for VS Code, Google Chrome, Edge, WhatsApp, Notepad, etc.
- Smart folder search and workstation screen locking (`LockWorkStation`).

### 2. 🍎 macOS Support
- Clean macOS abstraction preserving native `say` TTS, Spotlight folder search (`mdfind`), and bundle app execution (`open -a`).
- Non-blocking execution prevents audio freezing and thread locks.

### 3. 🐧 Linux Support
- Full Linux desktop compatibility (Ubuntu, Debian, Fedora, Arch).
- TTS fallback to `spd-say` or `espeak-ng`.
- System opening via `xdg-open` and desktop application launchers.

### 4. 🧠 Smarter AI Engine (`core/ai_engine.py`)
- Hybrid Multi-Tier AI Routing: Instant keyword parsing (< 5ms) + Local Ollama LLM (Llama 3, Phi-3, Mistral, Qwen 2.5) + Heuristic Fallback.
- **Conversational Memory:** Context buffer preserves past dialogue history for contextual follow-up questions.
- **Custom System Personas:** Maya Default, Jarvis, Cyberpunk Terminal, and Vietnamese Studio Assistant.

### 5. ⚡ Faster Performance
- Multi-threaded non-blocking TTS audio queue (`core/voice_engine.py`).
- Ambient noise dynamic energy threshold calibration prevents 500ms repeated lag.
- Parallel background listening and decoupled command processing.

### 6. 🎨 Modern User Interface (`web_hud/`)
- **Google Labs Stitch Spec:** High-end dark glassmorphism cockpit HUD (`DESIGN.md`).
- **Kinetic Audio Visualizer:** Real-time animated audio wave reactive to speech states (`IDLE`, `LISTENING`, `THINKING`, `SPEAKING`).
- **Telemetry Widget:** Live tracking of CPU load, RAM usage, and battery percentages.
- **Interactive Transcript Feed:** Real-time chat stream with quick-action shortcuts.

### 7. 🎙️ Improved Voice Recognition
- Multi-language configuration (`en-US`, `en-IN`, `vi-VN`).
- Resilient microphone handling with automatic exception recovery.

### 8. 🤖 Advanced AI Automation (`core/system_automation.py`)
- Hardware volume management: Volume Up, Volume Down, Mute, and Unmute.
- Display & Privacy: Instant "Boss Key" (minimize all windows) and screen locking.
- Battery diagnostics and charging status tracking.
- Clipboard reader and text analysis.

### 9. 🔥 More Powerful Voice Commands (`core/command_registry.py`)
- Extensible decorator-based command registry.
- Fuzzy keyword tolerance (handles pronunciation differences and minor speech recognition typos).
- Dynamic Google & YouTube web query generation.

### 10. 💎 Exclusive Premium Features (`core/premium_features.py`)
- **Persona Studio:** Switch personality and voice tone in one command.
- **Workflow Macros:**
  - `Focus Mode`: Launches VS Code, adjusts volume to 30%, and starts ambient Lofi music.
  - `Meeting Mode`: Sanitizes desktop, mutes microphone and system audio.
  - `Developer Mode`: Launches coding workspace and GitHub.
- **Studio Voices:** High-definition neural speech synthesis via Edge-TTS.

---

## 📂 Project Structure

```
PN_AI/
├── core/
│   ├── __init__.py
│   ├── platform_adapter.py    # Cross-platform OS abstraction (Win/Mac/Linux)
│   ├── ai_engine.py           # Hybrid AI, conversation buffer, personas
│   ├── voice_engine.py        # Non-blocking TTS (Edge-TTS/SAPI) & STT
│   ├── system_automation.py   # Volume, battery, windows, clipboard controls
│   ├── command_registry.py    # Extensible router, fuzzy matching, search
│   └── premium_features.py    # Persona Studio, Workflows (Focus/Meeting)
├── web_hud/
│   ├── index.html             # Google Labs compliant futuristic Cockpit HUD
│   ├── style.css              # Dark Glassmorphism CSS tokens
│   └── app.js                 # Kinetic waveform canvas & telemetry controller
├── .virtual-company/          # Virtual Company governance & audit records
├── DESIGN.md                  # Google Labs Stitch Single Source of Truth
├── maya_core.py               # Main modular coordinator
├── main.py                    # Backward-compatible executable entry point
├── requirements.txt           # Dependency manifest
└── README.md                  # Project documentation
```

---

## 🎙️ Available Voice Commands

| Voice Command | Action | Platform Support |
| :--- | :--- | :--- |
| **Maya** | Wake up assistant & activate prompt | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Open Visual Studio Code** | Launches VS Code | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Open Chrome** | Opens Google Chrome browser | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Volume Up / Down** | Adjusts system audio volume | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Mute / Unmute** | Toggles master audio mute | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Screenshot** | Captures and previews screen capture | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Battery Status** | Reports battery percentage and power source | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **System Status** | Reports real-time CPU & RAM utilization | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Boss Key / Minimize All** | Minimizes all active windows to show desktop | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Lock Screen** | Immediately locks the workstation | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Focus Mode** | Activates dev environment + ambient music | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Open Folder Downloads** | Opens user's Downloads folder | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Play [Song Name]** | Streams requested music on YouTube | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Search Google for [Query]**| Searches Google | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Tell me about yourself** | Maya introduces features & architecture | 🌍 Windows, 🍎 macOS, 🐧 Linux |
| **Stop Maya** | Safely terminates assistant session | 🌍 Windows, 🍎 macOS, 🐧 Linux |

---

## 🚀 Installation & Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/phinam2004/PN_AI.git
cd PN_AI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Maya AI
```bash
python main.py
```
*(Or run `python maya_core.py` for the direct modular orchestrator).*

---

## 📄 License
This project is licensed under the MIT License.