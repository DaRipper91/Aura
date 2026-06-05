import os
import re
from aura.core.mandates import aura_component, SentinelGuard

@aura_component
class SentinelBrain:
    """The Security Brain for Jules (Sentinel)."""
    __slots__ = ("project_root", "patterns")

    def __init__(self, root: str):
        self.project_root = root
        self.patterns = {
            "secrets": r"(api_key|secret|password|token)\s*[:=]\s*['\"]",
            "insecure_requests": r"verify\s*=\s*False",
            "exposed_ollama": r"http://0\.0\.0\.0"
        }

    def scan_integrity(self) -> bool:
        print("[🛡️ SENTINEL] Initiating security sweep...")
        issues_found = 0
        for root, _, files in os.walk(self.project_root):
            if ".git" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith((".py", ".yml", ".json", ".zig")):
                    path = os.path.join(root, file)
                    issues_found += self._audit_file(path)
        
        if issues_found == 0:
            print("[🛡️ SENTINEL] Status: SECURE.")
            return True
        else:
            print(f"[🛡️ SENTINEL] Status: VULNERABLE. {issues_found} issues detected.")
            return False

    def _audit_file(self, path: str) -> int:
        count = 0
        with open(path, "r", errors="ignore") as f:
            content = f.read()
            for name, pattern in self.patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"  [!] {name.upper()} detected in {os.path.relpath(path)}")
                    count += 1
        return count

if __name__ == "__main__":
    brain = SentinelBrain(os.getcwd())
    brain.scan_integrity()
