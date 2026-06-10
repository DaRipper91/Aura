from aura_core.engine import ToolRegistry

print(ToolRegistry.execute("write_file", {"file_path": "test_file.txt", "content": "hello"}))
print(ToolRegistry.execute("read_file", {"file_path": "test_file.txt"}))
print(ToolRegistry.execute("run_shell_command", {"command": "ls test_file.txt"}))
