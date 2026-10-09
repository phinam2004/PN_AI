import sys
import os
import unittest

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.platform_adapter import platform_adapter
from core.ai_engine import ai_engine
from core.system_automation import system_automation
from core.command_registry import command_registry
from core.premium_features import premium_suite

class TestMayaCrossPlatformCore(unittest.TestCase):

    def test_01_platform_adapter(self):
        """Verify OS detection and path resolution."""
        os_info = platform_adapter.get_os_info()
        self.assertIn("os", os_info)
        self.assertIn(os_info["os"], ["Windows", "Darwin", "Linux"])
        self.assertTrue(len(platform_adapter.standard_folders) > 0)
        print(f"\n[Test] Detected OS: {os_info['os']} ({os_info['release']})")

    def test_02_system_telemetry(self):
        """Verify hardware metrics reporting."""
        telemetry = system_automation.get_telemetry()
        self.assertIn("cpu_percent", telemetry)
        self.assertIn("ram_percent", telemetry)
        self.assertIsInstance(telemetry["cpu_percent"], float)
        self.assertIsInstance(telemetry["ram_percent"], float)
        print(f"[Test] Telemetry: CPU={telemetry['cpu_percent']}%, RAM={telemetry['ram_percent']}%")

    def test_03_ai_engine_memory(self):
        """Verify conversational memory and fallback behavior."""
        ai_engine.clear_history()
        self.assertEqual(len(ai_engine.conversation_history), 0)

        # Query 1
        res1 = ai_engine.ask("who are you")
        self.assertTrue(len(res1) > 0)
        self.assertEqual(len(ai_engine.conversation_history), 2) # 1 user, 1 assistant

        # Query 2 (Check conversational retention)
        res2 = ai_engine.ask("what time is it")
        self.assertTrue(len(res2) > 0)
        self.assertEqual(len(ai_engine.conversation_history), 4)
        print(f"[Test] AI Query Response: '{res1[:60]}...'")

    def test_04_command_registry_exact_and_fuzzy(self):
        """Verify command dispatch for both exact and fuzzy queries."""
        # Exact command
        reply_intro = command_registry.dispatch("introduce yourself")
        self.assertTrue("Phi Nam" in reply_intro or "Maya" in reply_intro)

        # System telemetry command
        reply_telemetry = command_registry.dispatch("system status")
        self.assertIn("CPU", reply_telemetry)

        # Fuzzy matching test
        reply_fuzzy = command_registry.dispatch("tell me about yourself")
        self.assertTrue("Phi Nam" in reply_fuzzy or "Maya" in reply_fuzzy)

        # Battery check command
        reply_bat = command_registry.dispatch("battery level")
        self.assertTrue(len(reply_bat) > 0)
        print(f"[Test] Command Dispatch: battery -> '{reply_bat}'")

    def test_05_premium_features(self):
        """Verify persona switching and workflow execution."""
        # Switch persona
        res_persona = premium_suite.switch_persona("jarvis")
        self.assertIn("Jarvis", res_persona)
        self.assertEqual(premium_suite.active_persona, "jarvis")

        # Switch to Vietnamese
        res_vn = premium_suite.switch_persona("vietnamese_assistant")
        self.assertIn("Tiếng Việt", res_vn)

        # Workflow execution
        res_meeting = premium_suite.execute_workflow("meeting mode")
        self.assertIn("Meeting Mode", res_meeting)
        print(f"[Test] Premium Suite: {res_meeting}")

    def test_06_ui_files_exist(self):
        """Verify that the Google Labs compliant Web HUD files exist."""
        hud_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_hud"))
        self.assertTrue(os.path.exists(os.path.join(hud_dir, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(hud_dir, "style.css")))
        self.assertTrue(os.path.exists(os.path.join(hud_dir, "app.js")))
        print("[Test] Web HUD files verified.")

if __name__ == "__main__":
    unittest.main()
