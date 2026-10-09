import webbrowser
from typing import Dict, Any, List
from .platform_adapter import platform_adapter
from .system_automation import system_automation
from .voice_engine import voice_engine
from .ai_engine import ai_engine

class PremiumFeatureSuite:
    """
    Exclusive Premium Enhancements:
    - Persona Studio (Custom AI Personalities)
    - Automated Multi-Step Workflows (Focus Mode, Dev Mode, Meeting Mode)
    - Studio Neural Voices (Edge-TTS high definition)
    - Privacy Shield Mode
    """

    PERSONAS = {
        "maya_default": {
            "name": "Maya (Balanced)",
            "voice": "en-US-AriaNeural",
            "prompt": "You are Maya, an ultra-smart, witty, and fast personal AI assistant. Keep answers concise, natural, and helpful."
        },
        "jarvis": {
            "name": "Jarvis (Executive Butler)",
            "voice": "en-GB-RyanNeural",
            "prompt": "You are Jarvis, an ultra-sophisticated British AI system. Address the user as 'Sir' or 'Boss'. Maintain flawless formal etiquette and surgical efficiency."
        },
        "cyberpunk": {
            "name": "Cyberpunk Operator",
            "voice": "en-US-ChristopherNeural",
            "prompt": "You are a cybernetic terminal AI assistant in Neo-Tokyo. Speak directly, cold, technical, and use cyber-ops jargon sparingly."
        },
        "vietnamese_assistant": {
            "name": "Maya Tiếng Việt (Studio Voice)",
            "voice": "vi-VN-HoaiMyNeural",
            "prompt": "Bạn là Maya, trợ lý ảo thông minh và thân thiện. Trả lời bằng tiếng Việt tự nhiên, súc tích, lễ phép và rõ ràng."
        }
    }

    def __init__(self):
        self.active_persona = "maya_default"
        self.privacy_shield_enabled = False

    def switch_persona(self, persona_key: str) -> str:
        """Switch assistant voice and personality on the fly."""
        if persona_key not in self.PERSONAS:
            return f"Unknown persona '{persona_key}'. Available: {list(self.PERSONAS.keys())}"

        meta = self.PERSONAS[persona_key]
        self.active_persona = persona_key
        voice_engine.voice_name = meta["voice"]
        ai_engine.set_persona(meta["prompt"])
        return f"Persona switched to {meta['name']} with studio voice {meta['voice']}."

    def execute_workflow(self, workflow_name: str) -> str:
        """Executes multi-step automated power workflows."""
        w = workflow_name.lower().strip()

        if "focus" in w:
            # 1. Open VS Code
            platform_adapter.open_application("vs code")
            # 2. Lower volume to comfortable 30%
            system_automation.adjust_volume("down")
            # 3. Open Spotify or Lofi YouTube
            webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk") # Lofi Girl
            return "Focus Mode initiated: VS Code launched, volume balanced, and ambient lofi stream opened."

        elif "meeting" in w:
            # Mute volume, minimize background windows
            system_automation.minimize_all_windows()
            system_automation.adjust_volume("mute")
            return "Meeting Mode active: Workstation sanitized, audio muted."

        elif "dev" in w or "developer" in w:
            platform_adapter.open_application("vs code")
            platform_adapter.open_application("terminal")
            webbrowser.open("https://github.com")
            return "Developer workstation initialized."

        return f"Workflow '{workflow_name}' not recognized."


premium_suite = PremiumFeatureSuite()
