import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main

class TestBackwardCompatibility(unittest.TestCase):

    def test_legacy_functions_exist(self):
        """Verify all legacy functions in main.py still exist and operate."""
        self.assertTrue(callable(main.speak))
        self.assertTrue(callable(main.introduce_yourself))
        self.assertTrue(callable(main.open_folder_anywhere))
        self.assertTrue(callable(main.ask_local_ai))
        self.assertTrue(callable(main.listen_command))
        self.assertTrue(callable(main.take_screenshot))
        self.assertTrue(callable(main.process_command))
        self.assertTrue(callable(main.start_maya))

    def test_ask_local_ai(self):
        """Verify ask_local_ai returns a valid string without throwing exception."""
        response = main.ask_local_ai("who are you")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        print(f"\n[Test] Legacy ask_local_ai: '{response[:50]}...'")

    def test_process_command(self):
        """Verify process_command runs smoothly for standard actions."""
        # This shouldn't raise exception
        main.process_command("tell me about yourself")
        main.process_command("system status")

if __name__ == "__main__":
    unittest.main()
