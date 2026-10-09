import os
import sys
import threading
import queue
import tempfile
import asyncio
import platform
import subprocess
from typing import Optional, Callable
from .platform_adapter import platform_adapter

class VoiceEngine:
    """
    High-Fidelity Multi-Engine Text-to-Speech (TTS) and Speech-to-Text (STT) Controller.
    Supports Edge-TTS Neural Voices, SAPI5/Pyttsx3, macOS 'say', and Linux espeak.
    """

    def __init__(self, voice_name: str = "en-US-AriaNeural", language: str = "en-US"):
        self.voice_name = voice_name
        self.language = language
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.is_listening = False
        self._stop_event = threading.Event()

        # Check available TTS backends
        self.has_edge_tts = self._check_edge_tts()
        self.has_speech_recognition = self._check_speech_recognition()

        # Start background TTS worker thread
        self.tts_thread = threading.Thread(target=self._process_tts_queue, daemon=True)
        self.tts_thread.start()

    def _check_edge_tts(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def _check_speech_recognition(self) -> bool:
        try:
            import speech_recognition
            return True
        except ImportError:
            return False

    def speak(self, text: str, sync: bool = False):
        """Queue text for non-blocking voice synthesis."""
        if not text or not text.strip():
            return
        clean_text = text.strip()
        print(f"[Maya Voice]: {clean_text}")

        if sync:
            self._synthesize_and_play(clean_text)
        else:
            self.speech_queue.put(clean_text)

    def _process_tts_queue(self):
        """Worker thread executing speech tasks sequentially."""
        while not self._stop_event.is_set():
            try:
                text = self.speech_queue.get(timeout=0.5)
                self.is_speaking = True
                self._synthesize_and_play(text)
                self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoiceEngine] TTS Worker Error: {e}")
                self.is_speaking = False

    def _synthesize_and_play(self, text: str):
        """Synthesize audio with best available engine and play it back."""
        # Method 1: Edge-TTS (Ultra realistic neural voice)
        if self.has_edge_tts:
            try:
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_file.close()

                async def generate_speech():
                    import edge_tts
                    communicate = edge_tts.Communicate(text, self.voice_name)
                    await communicate.save(temp_file.name)

                asyncio.run(generate_speech())
                self._play_audio_file(temp_file.name)
                try:
                    os.remove(temp_file.name)
                except Exception:
                    pass
                return
            except Exception as e:
                print(f"[VoiceEngine] Edge-TTS playback fallback triggered: {e}")

        # Method 2: macOS Native 'say'
        if platform_adapter.is_macos:
            try:
                safe_text = text.replace('"', '\\"')
                subprocess.run(["say", safe_text], check=True)
                return
            except Exception:
                pass

        # Method 3: Windows PowerShell Speech Synthesizer (Zero extra dependencies)
        if platform_adapter.is_windows:
            try:
                safe_text = text.replace('"', '""').replace("'", "''")
                ps_script = f'Add-Type -AssemblyName System.speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{safe_text}");'
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True, capture_output=True)
                return
            except Exception:
                pass

        # Method 4: Linux spd-say / espeak
        if platform_adapter.is_linux:
            for bin_cmd in ["spd-say", "espeak-ng", "espeak"]:
                if shutil.which(bin_cmd):
                    try:
                        subprocess.run([bin_cmd, text], check=True)
                        return
                    except Exception:
                        continue

        # Fallback print if all speech engines fail
        print(f"[VoiceEngine] (Audio output silent/unavailable): {text}")

    def _play_audio_file(self, file_path: str):
        """Cross-platform audio file playback."""
        if platform_adapter.is_windows:
            # Try playsound / sounddevice / PowerShell
            try:
                ps_cmd = f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
                return
            except Exception:
                pass

        elif platform_adapter.is_macos:
            try:
                subprocess.run(["afplay", file_path], check=True)
                return
            except Exception:
                pass

        elif platform_adapter.is_linux:
            for player in ["ffplay", "mpv", "aplay", "paplay"]:
                if shutil.which(player):
                    try:
                        subprocess.run([player, "-nodisp", "-autoexit", file_path], check=True, capture_output=True)
                        return
                    except Exception:
                        continue

    def listen(self, timeout: int = 5, phrase_time: int = 6) -> str:
        """
        Listen for user voice command with graceful fallback to terminal input.
        """
        if self.has_speech_recognition:
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                recognizer.dynamic_energy_threshold = True

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    self.is_listening = True
                    print("[VoiceEngine] Listening...")
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time)
                    self.is_listening = False

                text = recognizer.recognize_google(audio, language=self.language)
                return text.strip()
            except Exception:
                self.is_listening = False
                return ""
        else:
            # Fallback if speech_recognition or microphone driver is absent
            return ""

    def shutdown(self):
        self._stop_event.set()


voice_engine = VoiceEngine()
