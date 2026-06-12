import unittest
import sys
import os
import json

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

    def test_fleet_health_check(self):
        """Verify that fleet_health_check aggregates mock vitals."""
        # Mock satellite callback
        ToolRegistry.set_telemetry_callback(lambda f: '{"power": {"battery_level": 50, "is_charging": true}}')
        
        # We can't easily mock the subprocess SSH calls without complex mocking, 
        # so we just verify it runs and returns a JSON string with the 'satellite' key.
        result = ToolRegistry.fleet_health_check({})
        data = json.loads(result)
        
        self.assertIn("satellite", data)
        self.assertEqual(data["satellite"]["battery"], "50%")

if __name__ == '__main__':
    unittest.main()
