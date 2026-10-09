import os
import json
from typing import List, Dict, Any, Optional

DEFAULT_SYSTEM_PROMPT = """
Bạn là Phi Nam AI, trợ lý ảo thông minh, nhanh nhẹn và lịch thiệp chạy trực tiếp trên máy tính của người dùng.
Quy tắc:
1. Trả lời súc tích, ngắn gọn (1 đến 2 câu).
2. Xưng hô tự nhiên, lễ phép: 'Dạ, em nghe anh Phi Nam' hoặc 'Dạ, em đã làm xong cho anh rồi ạ'.
3. Ưu tiên hỗ trợ điều khiển máy tính, mở app, tìm kiếm web, chỉnh âm thanh và tự động hóa.
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
            return "Dạ, em đang lắng nghe anh đây ạ. Anh cần em giúp gì ạ?"

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
        """Rule-based smart response in natural Vietnamese when offline."""
        p = prompt.lower()
        if any(w in p for w in ["bạn là ai", "em là ai", "phi nam là ai", "who are you"]):
            return "Dạ, em là Phi Nam AI, trợ lý ảo thông minh chạy trực tiếp trên máy tính của anh ạ."
        elif any(w in p for w in ["phi nam ơi", "việt nam ơi", "phi nam", "ơi em"]):
            return "Dạ, em nghe anh Phi Nam! Anh muốn em mở ứng dụng hay làm gì giúp anh ạ?"
        elif any(w in p for w in ["khỏe không", "thế nào rồi", "how are you"]):
            return "Dạ, hệ thống đang hoạt động với hiệu năng tối đa, sẵn sàng phục vụ anh ạ!"
        elif any(w in p for w in ["mấy giờ", "bây giờ là mấy giờ", "thời gian", "time"]):
            from datetime import datetime
            return f"Dạ, bây giờ là {datetime.now().strftime('%H:%M')} ạ."
        elif any(w in p for w in ["ngày mấy", "hôm nay ngày", "thứ mấy", "date"]):
            from datetime import datetime
            return f"Dạ, hôm nay là ngày {datetime.now().strftime('%d/%m/%Y')} ạ."
        elif any(w in p for w in ["cảm ơn", "thank"]):
            return "Dạ, được phục vụ anh là niềm vui của em ạ!"
        else:
            return f"Dạ, em đã nghe rõ yêu cầu: '{prompt}'. Em có thể giúp anh mở Chrome, VS Code, tăng giảm âm lượng hoặc tìm kiếm Google, YouTube ngay lập tức ạ!"

    def clear_history(self):
        """Resets conversational memory."""
        self.conversation_history = []


ai_engine = AIEngine()
