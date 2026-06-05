import os
import re
from aura.core.mandates import aura_component, SentinelGuard

@aura_component
class AndroidSentinel:
    """The Security Brain for Jules (Sentinel) - Android Target."""
    __slots__ = ("project_root", "patterns")

    def __init__(self, root: str):
        self.project_root = root
        self.patterns = {
            "exported_activities": r'android:exported="true"',
            "hardcoded_secrets": r'(api_key|token|password|secret)\s*=\s*".+"',
            "insecure_trust_all": r'X509TrustManager',
            "chaquopy_version": r'com\.chaquo\.python'
        }

    def scan_integrity(self) -> bool:
        print("[🛡️ SENTINEL // ANDROID] Initiating mobile security sweep...")
        issues_found = 0
        android_dir = os.path.join(self.project_root, "android")
        
        for root, _, files in os.walk(android_dir):
            for file in files:
                if file.endswith((".xml", ".kt", ".gradle")):
                    path = os.path.join(root, file)
                    issues_found += self._audit_file(path)
        
        if issues_found == 0:
            print("[🛡️ SENTINEL // ANDROID] Status: SECURE.")
            return True
        else:
            print(f"[🛡️ SENTINEL // ANDROID] Status: VULNERABLE. {issues_found} issues detected.")
            return False

    def _audit_file(self, path: str) -> int:
        count = 0
        with open(path, "r", errors="ignore") as f:
            content = f.read()
            for name, pattern in self.patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    # For Android, some exports are required, but we flag for review
                    print(f"  [!] {name.upper()} flagged in {os.path.relpath(path, self.project_root)}")
                    count += 1
        return count

if __name__ == "__main__":
    brain = AndroidSentinel(os.getcwd())
    brain.scan_integrity()
