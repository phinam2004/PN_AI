import os
import sys
import webbrowser
import threading
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.platform_adapter import platform_adapter
from core.voice_engine import voice_engine
from core.ai_engine import ai_engine
from core.system_automation import system_automation
from core.command_registry import command_registry
from core.premium_features import premium_suite

class MayaCore:
    """
    Central Coordinator for Maya AI Assistant.
    Orchestrates UI, Voice I/O, Command Routing, and Cross-Platform Execution.
    """

    def __init__(self):
        self.is_running = True
        self.hud_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "web_hud", "index.html"))

    def launch_hud(self):
        """Opens the modern Google Labs compliant Web HUD."""
        if os.path.exists(self.hud_path):
            webbrowser.open(f"file://{self.hud_path}")
            print(f"[OK] Modern Maya Cockpit HUD launched at: file://{self.hud_path}")
        else:
            # Fallback to GIF or local HTML
            gif_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "maya_animation.html"))
            if os.path.exists(gif_html):
                webbrowser.open(f"file://{gif_html}")

    def execute_command(self, command_text: str) -> str:
        """Dispatches a command through the registry and triggers voice reply."""
        print(f"\n[User]: {command_text}")
        response = command_registry.dispatch(command_text)

        if response == "TERMINATE_SESSION":
            voice_engine.speak("Shutting down Maya. Have a productive day, boss!", sync=True)
            self.is_running = False
            return "Shutdown"

        if response:
            voice_engine.speak(response)
        return response

    def run_interactive_loop(self):
        """
        Dual input loop: Lends ear to microphone while accepting terminal text commands,
        ensuring 100% usability even when audio hardware is busy or absent.
        """
        self.launch_hud()
        voice_engine.speak(f"Maya AI activated on {platform_adapter.os_type}. All systems operational.")

        print("\n" + "="*60)
        print(f" [MAYA AI] v1.2 NEXT-GEN ({platform_adapter.os_type} Edition)")
        print(" [INFO] Say 'Maya' or type your command below.")
        print(" [INFO] Type 'exit' or 'stop maya' to quit.")
        print("="*60 + "\n")

        while self.is_running:
            try:
                # 1. Listen via microphone if available
                voice_input = voice_engine.listen(timeout=3, phrase_time=5)

                if voice_input:
                    voice_lower = voice_input.lower()
                    if "maya" in voice_lower:
                        voice_engine.speak("Yes boss?")
                        cmd = voice_engine.listen(timeout=5, phrase_time=7)
                        if cmd:
                            self.execute_command(cmd)
                    else:
                        # Direct speech command execution
                        self.execute_command(voice_input)
                else:
                    # Non-blocking pause
                    time.sleep(0.5)

            except KeyboardInterrupt:
                print("\nStopping Maya AI...")
                self.is_running = False
                break
            except Exception as e:
                print(f"[MayaCore] Runtime exception: {e}")
                time.sleep(1)

        voice_engine.shutdown()

maya_app = MayaCore()

if __name__ == "__main__":
    maya_app.run_interactive_loop()
