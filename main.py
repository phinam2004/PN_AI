"""
Maya AI - Advanced Cross-Platform Personal Voice Assistant (v1.2 Next-Gen)
Fully upgraded with Windows, macOS, Linux support, Smarter AI Engine,
Modern Web HUD, and Autonomous System Automation.
"""

import os
import sys
import time
import webbrowser
from datetime import datetime

from core.platform_adapter import platform_adapter
from core.voice_engine import voice_engine
from core.ai_engine import ai_engine
from core.system_automation import system_automation
from core.command_registry import command_registry
from core.premium_features import premium_suite

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Backward-compatibility constants
GIF_PATH = "maya_animation.gif"

def show_startup_gif():
    """Show the modern Google Labs compliant Web HUD or fallback GIF."""
    hud_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "web_hud", "index.html"))
    if os.path.exists(hud_file):
        try:
            if sys.platform == "win32":
                os.startfile(hud_file)
            else:
                webbrowser.open(f"file://{hud_file}")
        except Exception:
            webbrowser.open(f"file://{hud_file}")
        print(f"[OK] Modern Maya Cockpit HUD opened at: {hud_file}", flush=True)
        return

    # Fallback GIF animation
    gif_absolute_path = os.path.abspath(GIF_PATH)
    if os.path.exists(gif_absolute_path):
        html_file = "maya_animation.html"
        html_path = os.path.abspath(html_file)
        try:
            if sys.platform == "win32":
                os.startfile(html_path)
            else:
                webbrowser.open(f"file://{html_path}")
        except Exception:
            webbrowser.open(f"file://{html_path}")
        print("[OK] Maya AI animation opened in browser", flush=True)

def speak(text):
    """Cross-platform text-to-speech."""
    voice_engine.speak(text)

def introduce_yourself():
    """Introduces Maya with persona context."""
    intro_text = (
        "Hello! I am Maya. Upgraded with cross-platform architecture for Windows, macOS, and Linux. "
        "I am smart, fast, and equipped with advanced system automation and local AI intelligence. "
        "What can I do for you, boss?"
    )
    speak(intro_text)

def open_folder_anywhere(foldername):
    """Cross-platform smart folder search & open."""
    if platform_adapter.find_and_open_folder(foldername):
        speak(f"Opening folder {foldername}")
    else:
        speak("Folder not found boss")

def ask_local_ai(prompt):
    """Queries the smart hybrid AI engine with conversational memory."""
    return ai_engine.ask(prompt)

def listen_command(timeout=5, phrase_time=6):
    """Listens for voice commands via cross-platform voice engine."""
    return voice_engine.listen(timeout=timeout, phrase_time=phrase_time)

def take_screenshot():
    """Captures and opens a system screenshot across platforms."""
    path = platform_adapter.take_screenshot("screenshots")
    if path:
        speak("Screenshot taken")
        return path
    else:
        speak("Failed to take screenshot")
        return None

def process_command(command):
    """Dispatches command to the central extensible router."""
    if not command:
        return
    response = command_registry.dispatch(command)
    if response == "TERMINATE_SESSION":
        speak("Goodbye boss")
        raise SystemExit
    elif response:
        speak(response)

def start_maya():
    """Starts Maya AI assistant with modern UI and responsive listening loop."""
    show_startup_gif()
    speak(f"Maya is activated on {platform_adapter.os_type}")

    print("\n" + "="*50)
    print(f" Maya AI v1.2 [{platform_adapter.os_type}] Ready")
    print("="*50 + "\n")

    while True:
        try:
            word = listen_command(timeout=4, phrase_time=3)
            if not word:
                time.sleep(0.5)
                continue

            if "maya" in word.lower():
                speak("Yes boss")
                command = listen_command(timeout=6, phrase_time=8)
                if command:
                    process_command(command)
            else:
                # Direct voice command execution
                process_command(word)

        except SystemExit:
            break
        except KeyboardInterrupt:
            print("\nMaya AI stopped by user")
            break
        except Exception as e:
            print(f"[Maya Error]: {e}")

if __name__ == "__main__":
    try:
        start_maya()
    except KeyboardInterrupt:
        print("\nMaya AI stopped by user")
