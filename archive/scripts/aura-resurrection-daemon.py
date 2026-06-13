import subprocess
import time
import os

HUB_IP = "100.100.181.59"
HUB_MAC = "ec:b1:d7:5c:50:9c"
INTERFACE = "wlan0"

def ping_hub():
    try:
        # Use -c 1 -W 5 to ping once with 5 sec timeout
        result = subprocess.run(["ping", "-c", "1", "-W", "5", HUB_IP], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False

def wake_hub():
    print(f"[AURA-RESURRECTION] Hub unreachable. Firing WOL to {HUB_MAC}...")
    try:
        # Firing magic packet twice for redundancy
        subprocess.run(["sudo", "ether-wake", "-i", INTERFACE, HUB_MAC], check=True)
        time.sleep(2)
        subprocess.run(["sudo", "ether-wake", "-i", INTERFACE, HUB_MAC], check=True)
    except Exception as e:
        print(f"[AURA-RESURRECTION] WOL Error: {e}")

def main():
    print("[AURA-RESURRECTION] Daemon started.")
    failure_count = 0
    while True:
        if ping_hub():
            failure_count = 0
        else:
            failure_count += 1
            print(f"[AURA-RESURRECTION] Ping failed ({failure_count}/3)")
        
        if failure_count >= 3:
            wake_hub()
            failure_count = 0 # Reset and wait for boot
            time.sleep(180) # Wait 3 mins for boot process
        
        time.sleep(60)

if __name__ == "__main__":
    main()
