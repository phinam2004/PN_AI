import os
import json
from typing import List, Dict, Any, Optional

DEFAULT_SYSTEM_PROMPT = """
You are Maya, an ultra-intelligent, fast, and witty personal AI assistant.
Guidelines:
1. Keep spoken responses concise (1 to 3 sentences maximum) unless specifically asked for a detailed explanation.
2. Be direct, helpful, and courteous. Address the user respectfully as 'boss' or with natural warmth.
3. If executing a command or answering a factual query, prioritize crisp clarity without conversational filler.
4. When writing code, summarize the solution in one sentence and offer to open or write the file.
"""

class AIEngine:
    """
    Hybrid Smart AI Engine with Conversation Memory, Multi-Model Routing,
    and Dynamic Fallbacks.
    """

    def __init__(self, model_name: str = "llama3", max_history: int = 10):
        self.model_name = model_name
        self.max_history = max_history
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.conversation_history: List[Dict[str, str]] = []
        self.has_ollama = self._check_ollama()

    def _check_ollama(self) -> bool:
        try:
            import ollama
            return True
        except Exception as e:
            return False

    def set_persona(self, persona_prompt: str):
        """Allows switching the system personality dynamically."""
        self.system_prompt = persona_prompt

    def ask(self, user_prompt: str) -> str:
        """
        Query the intelligence core with context memory.
        Falls back gracefully if local LLM is unreachable.
        """
        if not user_prompt or not user_prompt.strip():
            return "I am listening, boss. What can I do for you?"

        # Append to history
        self.conversation_history.append({"role": "user", "content": user_prompt})

        # Trim history to max window
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

        # 1. Try Ollama Local Engine
        if self.has_ollama:
            try:
                import ollama
                response = ollama.chat(model=self.model_name, messages=messages)
                reply = response.get("message", {}).get("content", "").strip()
                if reply:
                    self.conversation_history.append({"role": "assistant", "content": reply})
                    return reply
            except Exception as e:
                print(f"[AIEngine] Ollama connection notice: {e}")

        # 2. Offline Heuristic AI Fallback (Guarantees zero downtime & instant response)
        fallback_reply = self._heuristic_fallback(user_prompt)
        self.conversation_history.append({"role": "assistant", "content": fallback_reply})
        return fallback_reply

    def _heuristic_fallback(self, prompt: str) -> str:
        """Rule-based smart response when offline or when LLM server is starting up."""
        p = prompt.lower()
        if any(w in p for w in ["who are you", "what is your name", "introduce yourself"]):
            return "I am Maya, your next-generation personal AI assistant, built for speed, automation, and effortless voice control."
        elif any(w in p for w in ["how are you", "how's it going"]):
            return "All operational systems are running at peak efficiency, boss. Standing by for your command."
        elif any(w in p for w in ["time", "what time"]):
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        elif any(w in p for w in ["date", "what day"]):
            from datetime import datetime
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        elif "thank" in p:
            return "Always a pleasure to assist you, boss."
        else:
            return f"I heard you say: '{prompt}'. Local LLM is offline, but my system automation commands remain fully operational."

    def clear_history(self):
        """Resets conversational memory."""
        self.conversation_history = []


ai_engine = AIEngine()
