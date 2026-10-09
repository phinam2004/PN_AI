import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

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
    Optimized for Vietnamese (Edge-TTS Neural) and cross-platform native speech.
    """

    def __init__(self, voice_name: str = "vi-VN-HoaiMyNeural", language: str = "vi-VN"):
        self.voice_name = voice_name
        self.language = language
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.is_listening = False
        self._stop_event = threading.Event()

        # Check available TTS backends
        self.has_edge_tts = self._check_edge_tts()
        self.has_speech_recognition = self._check_speech_recognition()

        # Initialize speech recognizer once
        self.recognizer = None
        if self.has_speech_recognition:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 120
                self.recognizer.pause_threshold = 0.7
            except Exception:
                pass

        # Start background TTS worker thread
        self.tts_thread = threading.Thread(target=self._process_tts_queue, daemon=True)
        self.tts_thread.start()

    def calibrate_microphone(self):
        """Calibrates microphone sensitivity based on actual ambient noise in 0.5s."""
        if self.has_speech_recognition and self.recognizer:
            try:
                import speech_recognition as sr
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    # Keep energy threshold responsive (between 80 and 220)
                    self.recognizer.energy_threshold = max(80, min(self.recognizer.energy_threshold, 220))
                    print(f"[VoiceEngine] Micro đã cân chỉnh: ngưỡng {self.recognizer.energy_threshold:.1f}")
            except Exception as e:
                print(f"[VoiceEngine] Cân chỉnh micro: {e}")

    def _check_edge_tts(self) -> bool:
        try:
            import edge_tts
            return True
        except Exception:
            return False

    def _check_speech_recognition(self) -> bool:
        try:
            import speech_recognition
            return True
        except Exception:
            return False

    def play_wake_chime(self):
        """Plays the official high-fidelity Windows Speech recognition chime instantly."""
        try:
            if platform_adapter.is_windows:
                import winsound
                sound_file = r'C:\Windows\Media\Speech On.wav'
                if os.path.exists(sound_file):
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    winsound.Beep(1200, 100)
        except Exception:
            pass

    def play_cached_audio(self, filename: str, sync: bool = True) -> bool:
        """Plays a pre-cached local audio file instantly with 0ms network latency."""
        base_name = os.path.splitext(filename)[0]
        # Prefer uncompressed WAV for 0ms instant Windows playback
        wav_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", f"{base_name}.wav"))
        mp3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", f"{base_name}.mp3"))

        if platform_adapter.is_windows and os.path.exists(wav_path):
            try:
                import winsound
                flags = winsound.SND_FILENAME
                if not sync:
                    flags |= winsound.SND_ASYNC
                winsound.PlaySound(wav_path, flags)
                return True
            except Exception:
                pass

        target_file = wav_path if os.path.exists(wav_path) else mp3_path
        if os.path.exists(target_file):
            self._play_audio_file(target_file, text_len=15)
            return True
        return False

    def speak(self, text: str, sync: bool = False):
        """Queue text for voice synthesis."""
        if not text or not text.strip():
            return
        clean_text = text.strip()
        print(f"[Phi Nam Voice]: {clean_text}")

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
        # Method 1: Edge-TTS Neural Voice (High fidelity Vietnamese/English)
        if self.has_edge_tts:
            try:
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_file.close()

                async def generate_speech():
                    import edge_tts
                    communicate = edge_tts.Communicate(text, self.voice_name)
                    await communicate.save(temp_file.name)

                asyncio.run(generate_speech())
                self._play_audio_file(temp_file.name, text_len=len(text))
                try:
                    os.remove(temp_file.name)
                except Exception:
                    pass
                return
            except Exception:
                pass

        # Method 2: Windows Native SAPI.SpVoice via win32com
        if platform_adapter.is_windows:
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                return
            except Exception:
                pass

        # Method 3: macOS Native 'say'
        if platform_adapter.is_macos:
            try:
                safe_text = text.replace('"', '\\"')
                subprocess.run(["say", safe_text], check=True, timeout=10)
                return
            except Exception:
                pass

        # Method 4: Linux spd-say / espeak
        if platform_adapter.is_linux:
            import shutil
            for bin_cmd in ["spd-say", "espeak-ng", "espeak"]:
                if shutil.which(bin_cmd):
                    try:
                        subprocess.run([bin_cmd, text], check=True, timeout=10)
                        return
                    except Exception:
                        continue

        # Fallback print if all speech engines fail
        print(f"[VoiceEngine] (Silent output): {text}")

    def _play_audio_file(self, file_path: str, text_len: int = 20):
        """Cross-platform audio file playback with multi-fallback reliability."""
        import shutil

        # Method 1: ffplay (100% reliable across all formats MP3/WAV/AAC and direct WASAPI output)
        ffplay = shutil.which("ffplay")
        if ffplay:
            try:
                subprocess.run([ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", file_path],
                               check=True, timeout=12)
                return
            except Exception:
                pass

        if platform_adapter.is_windows:
            # Method 2: winsound for WAV
            if file_path.lower().endswith(".wav"):
                try:
                    import winsound
                    winsound.PlaySound(file_path, winsound.SND_FILENAME)
                    return
                except Exception:
                    pass

            # Method 3: Windows Media Player COM
            try:
                import win32com.client, time
                wmp = win32com.client.Dispatch("WMPlayer.OCX")
                wmp.URL = file_path
                wmp.controls.play()
                wait_time = min(10.0, max(1.5, text_len * 0.15))
                time.sleep(wait_time)
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
            for player in ["mpv", "aplay", "paplay"]:
                if shutil.which(player):
                    try:
                        subprocess.run([player, "-nodisp", "-autoexit", file_path], check=True, capture_output=True)
                        return
                    except Exception:
                        continue

    def listen(self, timeout: int = 4, phrase_time: int = 6) -> str:
        """
        Listen for user voice command using Vietnamese and English speech recognition.
        """
        if self.has_speech_recognition and self.recognizer:
            try:
                import speech_recognition as sr
                with sr.Microphone() as source:
                    self.is_listening = True
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time)
                    self.is_listening = False

                # Primary: Vietnamese recognition
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    return text.strip()
                except Exception:
                    # Fallback to English
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        return text.strip()
                    except Exception:
                        return ""
            except Exception:
                self.is_listening = False
                return ""
        return ""

    def shutdown(self):
        self._stop_event.set()


voice_engine = VoiceEngine()
