import os
import sys
import platform
import subprocess
import shutil
import webbrowser
from datetime import datetime
from typing import Optional, Dict, Any, List

class PlatformAdapter:
    """
    Cross-Platform Hardware & OS Abstraction Layer for Windows, macOS, and Linux.
    Normalizes app launching, path discovery, system calls, and file operations.
    """

    SYSTEM_WINDOWS = "Windows"
    SYSTEM_MACOS = "Darwin"
    SYSTEM_LINUX = "Linux"

    def __init__(self):
        self.os_type = platform.system()
        self.is_windows = self.os_type == self.SYSTEM_WINDOWS
        self.is_macos = self.os_type == self.SYSTEM_MACOS
        self.is_linux = self.os_type == self.SYSTEM_LINUX

        # Standard system paths cache
        self.home_dir = os.path.expanduser("~")
        self.standard_folders = {
            "downloads": os.path.join(self.home_dir, "Downloads"),
            "desktop": os.path.join(self.home_dir, "Desktop"),
            "documents": os.path.join(self.home_dir, "Documents"),
            "pictures": os.path.join(self.home_dir, "Pictures"),
            "music": os.path.join(self.home_dir, "Music"),
            "videos": os.path.join(self.home_dir, "Videos"),
        }

    def get_os_info(self) -> Dict[str, Any]:
        """Returns human-readable OS information."""
        return {
            "os": self.os_type,
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version.split()[0],
        }

    def open_path(self, target_path: str) -> bool:
        """Opens a file or directory using the OS default handler."""
        if not os.path.exists(target_path):
            return False

        try:
            if self.is_windows:
                os.startfile(target_path)
                return True
            elif self.is_macos:
                subprocess.run(["open", target_path], check=False)
                return True
            elif self.is_linux:
                subprocess.run(["xdg-open", target_path], check=False)
                return True
            return False
        except Exception as e:
            print(f"[PlatformAdapter] Error opening path '{target_path}': {e}")
            return False

    def open_application(self, app_name: str) -> bool:
        """
        Cross-platform application launcher with fallback registry/path resolution.
        """
        app_name_lower = app_name.lower().strip()

        # Dictionary of cross-platform app mappings
        known_apps = {
            "visual studio code": {"win": "code", "mac": "Visual Studio Code", "linux": "code"},
            "vs code": {"win": "code", "mac": "Visual Studio Code", "linux": "code"},
            "chrome": {"win": "chrome", "mac": "Google Chrome", "linux": "google-chrome"},
            "google chrome": {"win": "chrome", "mac": "Google Chrome", "linux": "google-chrome"},
            "safari": {"win": None, "mac": "Safari", "linux": None},
            "edge": {"win": "msedge", "mac": "Microsoft Edge", "linux": "microsoft-edge"},
            "firefox": {"win": "firefox", "mac": "Firefox", "linux": "firefox"},
            "whatsapp": {"win": "whatsapp", "mac": "WhatsApp", "linux": "whatsapp"},
            "spotify": {"win": "spotify", "mac": "Spotify", "linux": "spotify"},
            "notepad": {"win": "notepad", "mac": "TextEdit", "linux": "gedit"},
            "terminal": {"win": "cmd", "mac": "Terminal", "linux": "x-terminal-emulator"},
            "calculator": {"win": "calc", "mac": "Calculator", "linux": "gnome-calculator"},
        }

        target_meta = known_apps.get(app_name_lower)

        try:
            if self.is_windows:
                command = target_meta.get("win") if target_meta else app_name
                if not command:
                    return False
                # Try opening via start shell command
                try:
                    subprocess.Popen(f"start {command}", shell=True)
                    return True
                except Exception:
                    pass
                # Try finding executable in PATH
                cmd_path = shutil.which(command) or shutil.which(f"{command}.exe")
                if cmd_path:
                    subprocess.Popen([cmd_path])
                    return True

            elif self.is_macos:
                mac_app = target_meta.get("mac") if target_meta else app_name
                if mac_app:
                    result = subprocess.run(["open", "-a", mac_app], capture_output=True)
                    return result.returncode == 0

            elif self.is_linux:
                linux_cmd = target_meta.get("linux") if target_meta else app_name
                if linux_cmd:
                    cmd_path = shutil.which(linux_cmd)
                    if cmd_path:
                        subprocess.Popen([cmd_path])
                        return True
                    result = subprocess.run(["xdg-open", f"app:{linux_cmd}"], capture_output=True)
                    return result.returncode == 0

            # Fallback for generic command
            subprocess.Popen([app_name], shell=True)
            return True
        except Exception as e:
            print(f"[PlatformAdapter] Failed to open app '{app_name}': {e}")
            return False

    def find_and_open_folder(self, folder_query: str) -> bool:
        """
        Cross-platform smart folder search & open.
        """
        folder_clean = folder_query.lower().strip()

        # Check standard user folders first (Fast path)
        for key, path in self.standard_folders.items():
            if folder_clean in key or key in folder_clean:
                if os.path.exists(path):
                    return self.open_path(path)

        # macOS Spotlight Search
        if self.is_macos:
            try:
                res = subprocess.run(["mdfind", f"kMDItemContentType == 'public.folder' && kMDItemFSName == '*{folder_query}*'cd"],
                                     capture_output=True, text=True, timeout=5)
                matches = [p for p in res.stdout.strip().split("\n") if p and os.path.isdir(p)]
                if matches:
                    return self.open_path(matches[0])
            except Exception:
                pass

        # Windows Search / PowerShell or direct scan
        if self.is_windows:
            search_roots = [self.home_dir]
            for root_dir in search_roots:
                try:
                    for entry in os.scandir(root_dir):
                        if entry.is_dir() and folder_clean in entry.name.lower():
                            return self.open_path(entry.path)
                except (PermissionError, FileNotFoundError):
                    continue

        # Linux locate / scan
        if self.is_linux:
            locate_bin = shutil.which("locate")
            if locate_bin:
                try:
                    res = subprocess.run([locate_bin, "-b", f"\\{folder_query}"], capture_output=True, text=True, timeout=3)
                    for path in res.stdout.splitlines():
                        if os.path.isdir(path):
                            return self.open_path(path)
                except Exception:
                    pass

        return False

    def take_screenshot(self, output_dir: str = "screenshots") -> Optional[str]:
        """Cross-platform screenshot capture with safe fallbacks."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.abspath(os.path.join(output_dir, f"screenshot_{timestamp}.png"))

        # Try PIL ImageGrab
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            self.open_path(file_path)
            return file_path
        except Exception:
            pass

        # Try PyAutoGUI if available
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
            self.open_path(file_path)
            return file_path
        except Exception:
            pass

        # macOS Native screencapture fallback
        if self.is_macos:
            try:
                subprocess.run(["screencapture", "-x", file_path], check=True)
                self.open_path(file_path)
                return file_path
            except Exception:
                pass

        return None

    def lock_workstation(self) -> bool:
        """Locks the user screen across OS platforms."""
        try:
            if self.is_windows:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return True
            elif self.is_macos:
                subprocess.run(["pmset", "displaysleepnow"])
                return True
            elif self.is_linux:
                subprocess.run(["xdg-screensaver", "lock"])
                return True
        except Exception as e:
            print(f"[PlatformAdapter] Failed to lock screen: {e}")
        return False


# Singleton instance for global access
platform_adapter = PlatformAdapter()
