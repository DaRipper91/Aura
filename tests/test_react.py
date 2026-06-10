import json
import unittest
from unittest.mock import patch, MagicMock
from aura_core.engine import OllamaClient

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass

class TestReAct(unittest.TestCase):
    @patch('requests.post')
    def test_autonomous_chat(self, mock_post):
        client = OllamaClient()
        client.history = []
        
        # Sequence of responses:
        # 1. Model asks to run a shell command
        # 2. Model reads the result and says final answer
        
        mock_post.side_effect = [
            MockResponse({"message": {"content": "I need to run a command.\n<tool_call>\n{\"name\": \"run_shell_command\", \"args\": {\"command\": \"echo test\"}}\n</tool_call>"}}),
            MockResponse({"message": {"content": "The result is test."}})
        ]
        
        final_answer = client.autonomous_chat("phi3:mini", "Run echo test")
        self.assertEqual(final_answer, "The result is test.")
        
        # Check that history includes the tool call and result
        self.assertEqual(len(client.history), 4) # User prompt, assistant tool call, user tool result, assistant final answer
        self.assertIn("<tool_result>", client.history[2]["content"])
        self.assertIn("test", client.history[2]["content"])

if __name__ == '__main__':
    unittest.main()
