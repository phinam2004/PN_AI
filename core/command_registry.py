import re
import difflib
import webbrowser
from typing import Callable, List, Dict, Tuple, Optional, Any
from .platform_adapter import platform_adapter
from .system_automation import system_automation
from .ai_engine import ai_engine

class CommandRegistry:
    """
    Extensible Natural Language Command Router.
    Supports both Vietnamese and English voice commands, regex, fuzzy matching,
    and fallback to smart conversational AI.
    """

    def __init__(self):
        self.handlers: List[Dict[str, Any]] = []
        self._register_default_commands()

    def register(self, keywords: List[str], handler: Callable[[str], str], description: str = ""):
        """Register a new action handler."""
        self.handlers.append({
            "keywords": [k.lower().strip() for k in keywords],
            "handler": handler,
            "description": description
        })

    def _register_default_commands(self):
        # 1. Self Introduction & Persona
        self.register(
            keywords=[
                "bạn là ai", "giới thiệu bản thân", "phi nam là ai", "phi nam là gì",
                "tell me about yourself", "introduce yourself", "who are you"
            ],
            handler=lambda cmd: "Dạ, em là Phi Nam AI, trợ lý ảo thông minh chạy trực tiếp trên máy tính của anh. Em có thể điều khiển mở ứng dụng, tăng giảm âm lượng, chụp màn hình, tìm kiếm thông tin và tự động hóa công việc cho anh ạ!",
            description="Phi Nam Introduction"
        )

        # 2. System Audio Controls
        self.register(
            keywords=["tăng âm lượng", "âm lượng to lên", "bật to lên", "to lên", "volume up", "increase volume", "louder"],
            handler=lambda cmd: (system_automation.adjust_volume("up"), "Dạ, em đã tăng âm lượng rồi ạ.")[1],
            description="Tăng âm lượng"
        )
        self.register(
            keywords=["giảm âm lượng", "âm lượng nhỏ lại", "bật nhỏ lại", "nhỏ lại", "volume down", "decrease volume", "lower volume", "quieter"],
            handler=lambda cmd: (system_automation.adjust_volume("down"), "Dạ, em đã giảm âm lượng rồi ạ.")[1],
            description="Giảm âm lượng"
        )
        self.register(
            keywords=["tắt tiếng", "tắt âm thanh", "im lặng", "mute", "silence"],
            handler=lambda cmd: (system_automation.adjust_volume("mute"), "Dạ, em đã tắt tiếng rồi ạ.")[1],
            description="Tắt tiếng"
        )
        self.register(
            keywords=["bật tiếng", "bật lại âm thanh", "mở lại tiếng", "unmute"],
            handler=lambda cmd: (system_automation.adjust_volume("mute"), "Dạ, em đã bật lại âm thanh rồi ạ.")[1],
            description="Bật tiếng"
        )

        # 3. Security & Desktop Automation
        self.register(
            keywords=["khóa màn hình", "khóa máy", "khóa máy tính", "lock screen", "lock computer", "lock pc"],
            handler=lambda cmd: "Dạ, em đã khóa màn hình máy tính rồi ạ." if platform_adapter.lock_workstation() else "Không thể khóa màn hình.",
            description="Khóa màn hình"
        )
        self.register(
            keywords=["ẩn hết cửa sổ", "thu nhỏ tất cả", "về màn hình chính", "boss key", "minimize all", "show desktop", "hide windows"],
            handler=lambda cmd: (system_automation.minimize_all_windows(), "Dạ, em đã thu nhỏ tất cả cửa sổ về màn hình chính rồi ạ.")[1],
            description="Thu nhỏ tất cả cửa sổ"
        )

        # 4. Screenshots
        self.register(
            keywords=["chụp màn hình", "chụp ảnh màn hình", "chụp hình", "screenshot", "take screenshot", "capture screen"],
            handler=lambda cmd: "Dạ, em đã chụp ảnh màn hình và lưu lại rồi ạ." if platform_adapter.take_screenshot() else "Không thể chụp màn hình.",
            description="Chụp màn hình"
        )

        # 5. Telemetry & Hardware Health
        self.register(
            keywords=["kiểm tra pin", "pin còn bao nhiêu", "thời lượng pin", "battery status", "battery level", "battery percent"],
            handler=self._handle_battery_check,
            description="Kiểm tra Pin"
        )
        self.register(
            keywords=["trạng thái hệ thống", "thông số máy", "kiểm tra máy", "cpu", "ram", "system status", "system health"],
            handler=self._handle_system_status,
            description="Kiểm tra hệ thống"
        )

        # 6. Smart Folders
        self.register(
            keywords=["mở thư mục tải về", "mở tải về", "thư mục tải về", "mở downloads", "open downloads"],
            handler=lambda cmd: "Dạ, em đang mở thư mục Tải về cho anh ạ." if platform_adapter.find_and_open_folder("downloads") else "Không tìm thấy thư mục Downloads.",
            description="Mở thư mục Downloads"
        )
        self.register(
            keywords=["mở desktop", "mở màn hình chính", "open desktop"],
            handler=lambda cmd: "Dạ, em đang mở thư mục Desktop cho anh ạ." if platform_adapter.find_and_open_folder("desktop") else "Không tìm thấy Desktop.",
            description="Mở Desktop"
        )
        self.register(
            keywords=["mở tài liệu", "mở documents", "open documents"],
            handler=lambda cmd: "Dạ, em đang mở thư mục Tài liệu cho anh ạ." if platform_adapter.find_and_open_folder("documents") else "Không tìm thấy Documents.",
            description="Mở Documents"
        )

        # 7. Common Apps
        self.register(
            keywords=["mở visual studio code", "mở vs code", "mở code", "bật code", "open vs code", "open code"],
            handler=lambda cmd: "Dạ, em đang mở Visual Studio Code cho anh ạ." if platform_adapter.open_application("vs code") else "Không mở được VS Code.",
            description="Mở VS Code"
        )
        self.register(
            keywords=["mở chrome", "mở google chrome", "bật chrome", "open chrome", "launch chrome"],
            handler=lambda cmd: "Dạ, em đang mở trình duyệt Google Chrome cho anh ạ." if platform_adapter.open_application("chrome") else "Không mở được Chrome.",
            description="Mở Chrome"
        )
        self.register(
            keywords=["mở zalo", "bật zalo", "open zalo"],
            handler=lambda cmd: "Dạ, em đang mở Zalo cho anh ạ." if platform_adapter.open_application("zalo") else "Không mở được Zalo.",
            description="Mở Zalo"
        )
        self.register(
            keywords=["mở edge", "mở microsoft edge", "open edge"],
            handler=lambda cmd: "Dạ, em đang mở Microsoft Edge cho anh ạ." if platform_adapter.open_application("edge") else "Không mở được Edge.",
            description="Mở Edge"
        )
        self.register(
            keywords=["mở word", "bật word", "open word"],
            handler=lambda cmd: "Dạ, em đang mở Microsoft Word cho anh ạ." if platform_adapter.open_application("word") else "Không mở được Word.",
            description="Mở Word"
        )
        self.register(
            keywords=["mở excel", "bật excel", "open excel"],
            handler=lambda cmd: "Dạ, em đang mở Microsoft Excel cho anh ạ." if platform_adapter.open_application("excel") else "Không mở được Excel.",
            description="Mở Excel"
        )
        self.register(
            keywords=["mở ghi chú", "mở notepad", "open notepad"],
            handler=lambda cmd: "Dạ, em đang mở Notepad cho anh ạ." if platform_adapter.open_application("notepad") else "Không mở được Notepad.",
            description="Mở Notepad"
        )
        self.register(
            keywords=["mở máy tính", "mở calc", "calculator"],
            handler=lambda cmd: "Dạ, em đang mở máy tính tính toán cho anh ạ." if platform_adapter.open_application("calculator") else "Không mở được Máy tính.",
            description="Mở Calculator"
        )
        self.register(
            keywords=["mở youtube", "bật youtube", "open youtube"],
            handler=lambda cmd: (webbrowser.open("https://youtube.com"), "Dạ, em đang mở trang YouTube cho anh ạ.")[1],
            description="Mở YouTube"
        )

    def _handle_battery_check(self, cmd: str) -> str:
        telemetry = system_automation.get_telemetry()
        pct = telemetry.get("battery_percent")
        plugged = telemetry.get("battery_plugged")
        if pct is not None:
            status = "đang cắm sạc nguồn" if plugged else "đang dùng pin"
            return f"Pin máy tính của anh đang ở mức {pct}%, hiện {status} ạ."
        return "Máy tính của anh đang sử dụng nguồn điện trực tiếp từ ổ cắm bàn ạ."

    def _handle_system_status(self, cmd: str) -> str:
        telemetry = system_automation.get_telemetry()
        return f"Hệ thống hiện tại: CPU đang chạy ở mức {telemetry['cpu_percent']}%, RAM đang dùng {telemetry['ram_percent']}% (tương đương {telemetry['ram_used_gb']} GB trên tổng số {telemetry['ram_total_gb']} GB) ạ."

    def dispatch(self, raw_command: str) -> str:
        """Processes voice command in Vietnamese or English."""
        command = raw_command.lower().strip()
        if not command:
            return ""

        # 1. Exit / Shutdown command
        if any(w in command for w in ["tạm biệt phi nam", "tắt trợ lý", "dừng lại", "ngủ đi", "thoát", "stop maya", "exit"]):
            return "TERMINATE_SESSION"

        # 2. Dynamic Search Queries (Google & YouTube)
        for prefix in ["tìm kiếm google về ", "tìm kiếm trên google ", "tìm trên google ", "tìm google ", "search google for "]:
            if prefix in command:
                query = command.split(prefix, 1)[1].strip()
                if query:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    return f"Dạ, em đang tìm kiếm '{query}' trên Google cho anh ạ."

        for prefix in ["tìm kiếm youtube về ", "tìm trên youtube ", "tìm youtube ", "search youtube for "]:
            if prefix in command:
                query = command.split(prefix, 1)[1].strip()
                if query:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                    return f"Dạ, em đang tìm kiếm '{query}' trên YouTube cho anh ạ."

        for prefix in ["phát bài hát ", "bật bài hát ", "mở bài hát ", "nghe bài ", "bật bài ", "mở bài ", "play "]:
            if command.startswith(prefix) or prefix in command:
                song = command.split(prefix, 1)[1].strip()
                if song:
                    try:
                        import pywhatkit
                        pywhatkit.playonyt(song)
                        return f"Dạ, em đang mở bài hát {song} trên YouTube cho anh ạ."
                    except Exception:
                        webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
                        return f"Dạ, em đang mở bài hát {song} trên YouTube cho anh ạ."

        # 3. Dynamic Folder Open
        if command.startswith("mở thư mục "):
            target_folder = command.replace("mở thư mục", "").strip()
            if platform_adapter.find_and_open_folder(target_folder):
                return f"Dạ, em đang mở thư mục {target_folder} cho anh ạ."
            return f"Dạ, không tìm thấy thư mục {target_folder} trên máy ạ."

        # 4. Registered Handlers Match
        for handler_entry in self.handlers:
            for kw in handler_entry["keywords"]:
                if kw in command or difflib.SequenceMatcher(None, kw, command).ratio() > 0.82:
                    return handler_entry["handler"](command)

        # 5. Smart AI Fallback (Ollama or Heuristic Conversational)
        return ai_engine.ask(command)


command_registry = CommandRegistry()
