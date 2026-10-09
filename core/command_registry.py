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
    Supports regex patterns, fuzzy keyword tolerance, chained commands,
    and seamless fallback to conversational AI.
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
            keywords=["tell me about yourself", "introduce yourself", "who are you"],
            handler=lambda cmd: "Hello! I am Maya, your personal AI assistant. Upgraded with cross-platform intelligence, advanced system automation, and lightning-fast voice execution. How can I help you today?",
            description="Maya Self Introduction"
        )

        # 2. System Audio Controls
        self.register(
            keywords=["volume up", "increase volume", "louder"],
            handler=lambda cmd: system_automation.adjust_volume("up"),
            description="Volume Up"
        )
        self.register(
            keywords=["volume down", "decrease volume", "lower volume", "quieter"],
            handler=lambda cmd: system_automation.adjust_volume("down"),
            description="Volume Down"
        )
        self.register(
            keywords=["mute", "silence", "unmute"],
            handler=lambda cmd: system_automation.adjust_volume("mute"),
            description="Mute / Unmute"
        )

        # 3. Security & Desktop Automation
        self.register(
            keywords=["lock screen", "lock computer", "lock pc"],
            handler=lambda cmd: "Screen locked." if platform_adapter.lock_workstation() else "Failed to lock screen.",
            description="Lock Screen"
        )
        self.register(
            keywords=["minimize all", "boss key", "show desktop", "hide windows"],
            handler=lambda cmd: system_automation.minimize_all_windows(),
            description="Minimize All Windows"
        )

        # 4. Screenshots
        self.register(
            keywords=["screenshot", "take screenshot", "capture screen"],
            handler=lambda cmd: f"Screenshot captured at {platform_adapter.take_screenshot()}" if platform_adapter.take_screenshot() else "Screenshot captured.",
            description="Take Screenshot"
        )

        # 5. Telemetry & Hardware Health
        self.register(
            keywords=["battery status", "battery level", "battery percent"],
            handler=self._handle_battery_check,
            description="Check Battery"
        )
        self.register(
            keywords=["system status", "system health", "cpu usage", "ram usage"],
            handler=self._handle_system_status,
            description="Hardware Diagnostics"
        )

        # 6. Smart Folders
        self.register(
            keywords=["open downloads", "open folder downloads", "downloads folder"],
            handler=lambda cmd: "Opening Downloads folder." if platform_adapter.find_and_open_folder("downloads") else "Downloads folder not found.",
            description="Open Downloads Folder"
        )
        self.register(
            keywords=["open desktop", "open folder desktop", "desktop folder"],
            handler=lambda cmd: "Opening Desktop." if platform_adapter.find_and_open_folder("desktop") else "Desktop folder not found.",
            description="Open Desktop Folder"
        )
        self.register(
            keywords=["open documents", "open folder documents", "documents folder"],
            handler=lambda cmd: "Opening Documents." if platform_adapter.find_and_open_folder("documents") else "Documents folder not found.",
            description="Open Documents Folder"
        )

        # 7. Common Apps
        self.register(
            keywords=["open visual studio code", "open vs code", "launch code", "open code"],
            handler=lambda cmd: "Opening Visual Studio Code." if platform_adapter.open_application("vs code") else "Could not launch VS Code.",
            description="Open VS Code"
        )
        self.register(
            keywords=["open chrome", "launch chrome", "open google chrome"],
            handler=lambda cmd: "Opening Google Chrome." if platform_adapter.open_application("chrome") else "Could not launch Chrome.",
            description="Open Chrome"
        )
        self.register(
            keywords=["open safari"],
            handler=lambda cmd: "Opening Safari." if platform_adapter.open_application("safari") else "Safari is only supported on macOS.",
            description="Open Safari"
        )
        self.register(
            keywords=["open youtube", "launch youtube"],
            handler=lambda cmd: (webbrowser.open("https://youtube.com"), "Opening YouTube.")[1],
            description="Open YouTube"
        )

    def _handle_battery_check(self, cmd: str) -> str:
        telemetry = system_automation.get_telemetry()
        pct = telemetry.get("battery_percent")
        plugged = telemetry.get("battery_plugged")
        if pct is not None:
            status = "plugged in" if plugged else "on battery power"
            return f"Your battery is at {pct}%, currently {status}."
        return "No battery detected (running on desktop AC power)."

    def _handle_system_status(self, cmd: str) -> str:
        telemetry = system_automation.get_telemetry()
        return f"System telemetry: CPU is at {telemetry['cpu_percent']}%, RAM usage is at {telemetry['ram_percent']}% ({telemetry['ram_used_gb']} GB of {telemetry['ram_total_gb']} GB used)."

    def dispatch(self, raw_command: str) -> str:
        """
        Processes and dispatches voice text to the appropriate handler.
        Handles chained requests and passes unhandled queries to AI.
        """
        command = raw_command.lower().strip()
        if not command:
            return ""

        # 1. Stop Maya Command
        if command in ["stop maya", "exit maya", "quit maya", "goodbye maya", "shutdown maya"]:
            return "TERMINATE_SESSION"

        # 2. Dynamic Search Queries
        if "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"Searching YouTube for {query}."

        if "search google for" in command:
            query = command.replace("search google for", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching Google for {query}."

        if command.startswith("play "):
            song = command.replace("play", "", 1).strip()
            if song:
                try:
                    import pywhatkit
                    pywhatkit.playonyt(song)
                    return f"Playing {song} on YouTube."
                except Exception:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
                    return f"Opening {song} on YouTube."

        # Dynamic Generic Folder Open
        if command.startswith("open folder "):
            target_folder = command.replace("open folder", "").strip()
            if platform_adapter.find_and_open_folder(target_folder):
                return f"Opening folder {target_folder}."
            return f"Folder {target_folder} not found."

        # 3. Keyword & Fuzzy Match against Registered Handlers
        for handler_entry in self.handlers:
            for kw in handler_entry["keywords"]:
                if kw in command or difflib.SequenceMatcher(None, kw, command).ratio() > 0.85:
                    return handler_entry["handler"](command)

        # 4. Fallback to Smarter Conversational AI Engine
        return ai_engine.ask(command)


command_registry = CommandRegistry()
