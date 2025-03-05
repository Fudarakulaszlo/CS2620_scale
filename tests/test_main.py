import unittest
import time
import threading
from unittest.mock import patch, MagicMock

import main  # import your main module

class TestMainOrchestrator(unittest.TestCase):

    @patch("time.sleep", return_value=None)
    def test_main_runs_with_three_machines(self, mock_sleep):
        """
        A simple test to verify main.py can initialize and stop 3 machines.
        We'll mock time.sleep so we don't actually wait 60 seconds.
        """
        # Patch arguments if main uses argparse, or run main.main() directly
        with patch("sys.argv", ["main.py", "--num_machines", "3", "--base_port", "60000", "--run_duration", "1"]):
            main.main()  # Should run quickly because run_duration=1 and sleep is mocked.

        # If no exceptions are raised, we consider this test passed.
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
