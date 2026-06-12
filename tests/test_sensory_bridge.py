import unittest
import sys
import os

# Add python/ to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python')))

from aura_core.engine import ToolRegistry

class TestSensoryBridge(unittest.TestCase):
    def test_sensor_registration(self):
        """Verify that the telemetry callback can be registered and called."""
        mock_data = '{"battery": 85, "location": "fuzzed"}'
        def mock_callback(fuzzed):
            return mock_data
        
        ToolRegistry.set_telemetry_callback(mock_callback)
        result = ToolRegistry.check_satellite_sensors({"precision": "NORMAL"})
        
        self.assertEqual(result, mock_data)

    def test_risky_tool_policy(self):
        """Verify that run_shell_command is marked as RISKY."""
        policy = ToolRegistry.SECURITY_POLICY.get("run_shell_command")
        self.assertEqual(policy, "RISKY")

    def test_dispatch_routing(self):
        """Verify that dispatch_task routes correctly to registered callbacks."""
        mock_data = '{"status": "cellular_active"}'
        def mock_cellular(args):
            return mock_data
        
        # Override for testing
        ToolRegistry.check_cellular = staticmethod(mock_cellular)
        
        result = ToolRegistry.dispatch_task({
            "node_id": "pine",
            "tool": "check_cellular",
            "args": {"action": "get_status"}
        })
        
        self.assertEqual(result, mock_data)

if __name__ == '__main__':
    unittest.main()
