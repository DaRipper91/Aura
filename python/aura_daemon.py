import os
import time
import subprocess
from aura_core.engine import OllamaClient

class AuraDaemon:
    """
    Aura Autonomous Daemon: Performs background repository maintenance on the DA-HP Hub.
    """
    def __init__(self, interval_hours=6):
        self.interval = interval_hours * 3600
        self.client = OllamaClient()
        self.architect_model = "aura-architect:latest" # deepseek-coder-v2:16b

    def run(self):
        print(f"🌌 AURA DAEMON: System initialized. Maintenance interval: {self.interval/3600}h")
        while True:
            try:
                self.perform_maintenance()
            except Exception as e:
                print(f"❌ DAEMON_ERROR: {e}")
            
            print(f"💤 Sleeping for {self.interval/3600} hours...")
            time.sleep(self.interval)

    def perform_maintenance(self):
        print("🕒 MAINTENANCE_START: Mapping monorepo state...")
        self.graph_repository()
        
        print("🔍 MAINTENANCE_SCAN: Checking for security vulnerabilities...")
        self.audit_security()
        
        print("🚀 MAINTENANCE_REVIEW: Analyzing pending PRs...")
        self.review_pull_requests()

    def graph_repository(self):
        # Uses the Architect model to maintain an internal understanding of the monorepo structure
        prompt = "Analyze the current monorepo structure. Identify any circular dependencies between root, mobile, and core modules. Provide a summary in thoughts/repo_graph.md"
        response = ""
        for chunk in self.client.stream_chat(self.architect_model, prompt):
            response += chunk
        
        os.makedirs("thoughts", exist_ok=True)
        with open("thoughts/repo_graph.md", "w") as f:
            f.write(response)
        print("✅ GRAPHING: thoughts/repo_graph.md updated.")

    def audit_security(self):
        # Automated grep scans for secrets or insecure patterns
        vulnerabilities = []
        patterns = ["api_key =", "secret =", "password =", "shell=True"]
        
        for pattern in patterns:
            result = subprocess.run(["grep", "-rn", pattern, "."], capture_output=True, text=True)
            if result.stdout:
                vulnerabilities.append(result.stdout)
        
        if vulnerabilities:
            prompt = f"The following potential security risks were found in the repo:\n\n{''.join(vulnerabilities)}\n\nSuggest immediate patches or fixes."
            response = ""
            for chunk in self.client.stream_chat(self.architect_model, prompt):
                response += chunk
            
            with open("thoughts/security_audit.md", "w") as f:
                f.write(response)
            print("⚠️ SECURITY: Vulnerabilities detected and logged to thoughts/security_audit.md")
        else:
            print("✅ SECURITY: No immediate risks found.")

    def review_pull_requests(self):
        # If GitHub CLI is configured, it can fetch PRs and review them
        try:
            prs = subprocess.run(["gh", "pr", "list", "--json", "number,title"], capture_output=True, text=True)
            if prs.stdout:
                # Placeholder for active PR review logic
                print("✅ PR_REVIEW: Fetched active PRs for background analysis.")
        except:
            print("ℹ️ PR_REVIEW: gh cli not available or no PRs found.")

if __name__ == "__main__":
    daemon = AuraDaemon()
    daemon.run()
