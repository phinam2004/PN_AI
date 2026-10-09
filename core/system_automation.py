import os
import subprocess
from typing import Dict, Any, Optional
from .platform_adapter import platform_adapter

class SystemAutomation:
    """
    Advanced Operating System Control: Audio, Displays, Windows, Battery, and Telemetry.
    """

    def __init__(self):
        self.has_psutil = self._check_psutil()

    def _check_psutil(self) -> bool:
        try:
            import psutil
            return True
        except Exception:
            return False

    def get_telemetry(self) -> Dict[str, Any]:
        """Collects real-time hardware telemetry."""
        telemetry = {
            "os": platform_adapter.os_type,
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "battery_percent": None,
            "battery_plugged": None,
        }

        if self.has_psutil:
            try:
                import psutil
                telemetry["cpu_percent"] = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                telemetry["ram_percent"] = mem.percent
                telemetry["ram_used_gb"] = round(mem.used / (1024 ** 3), 2)
                telemetry["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)

                battery = psutil.sensors_battery()
                if battery:
                    telemetry["battery_percent"] = battery.percent
                    telemetry["battery_plugged"] = battery.power_plugged
            except Exception as e:
                print(f"[SystemAutomation] Telemetry error: {e}")

        return telemetry

    def adjust_volume(self, action: str, level: Optional[int] = None) -> str:
        """
        Adjusts master audio volume across Windows, macOS, and Linux.
        action: 'up', 'down', 'mute', 'unmute', 'set'
        """
        try:
            if platform_adapter.is_windows:
                # Windows volume adjustment via PowerShell SendKeys or NirCmd
                if action == "mute":
                    ps_cmd = "$wscript = New-Object -ComObject Wscript.Shell; $wscript.SendKeys([char]173)"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
                    return "System audio muted."
                elif action == "up":
                    ps_cmd = "$wscript = New-Object -ComObject Wscript.Shell; 1..5 | % { $wscript.SendKeys([char]175) }"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
                    return "Volume increased."
                elif action == "down":
                    ps_cmd = "$wscript = New-Object -ComObject Wscript.Shell; 1..5 | % { $wscript.SendKeys([char]174) }"
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
                    return "Volume decreased."

            elif platform_adapter.is_macos:
                if action == "mute":
                    subprocess.run(["osascript", "-e", "set volume with output muted"], check=True)
                    return "Audio muted."
                elif action == "unmute":
                    subprocess.run(["osascript", "-e", "set volume without output muted"], check=True)
                    return "Audio unmuted."
                elif action == "up":
                    subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 10)"], check=True)
                    return "Volume increased."
                elif action == "down":
                    subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 10)"], check=True)
                    return "Volume decreased."
                elif action == "set" and level is not None:
                    subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
                    return f"Volume set to {level}%."

            elif platform_adapter.is_linux:
                if action == "up":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%+"], check=False)
                    return "Volume increased."
                elif action == "down":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%-"], check=False)
                    return "Volume decreased."
                elif action == "mute":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"], check=False)
                    return "Mute toggled."
        except Exception as e:
            return f"Unable to adjust volume: {e}"

        return "Volume adjustment executed."

    def minimize_all_windows(self) -> str:
        """Minimizes all windows (Boss Key)."""
        try:
            if platform_adapter.is_windows:
                import ctypes
                # Shell.Application ToggleDesktop
                ps_cmd = '(New-Object -ComObject Shell.Application).MinimizeAll()'
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
                return "All windows minimized."
            elif platform_adapter.is_macos:
                subprocess.run(["osascript", "-e", 'tell application "System Events" to set visible of every process whose visible is true to false'])
                return "Desktop cleared."
        except Exception as e:
            return f"Boss key error: {e}"
        return "Minimized."

    def get_clipboard_text(self) -> str:
        """Reads text content from system clipboard."""
        try:
            import pyperclip
            return pyperclip.paste()
        except ImportError:
            pass

        if platform_adapter.is_windows:
            try:
                res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True)
                return res.stdout.strip()
            except Exception:
                pass
        elif platform_adapter.is_macos:
            try:
                res = subprocess.run(["pbpaste"], capture_output=True, text=True)
                return res.stdout.strip()
            except Exception:
                pass
        return ""


system_automation = SystemAutomation()
