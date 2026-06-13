import time
import os

BATT_DIR = "/sys/class/power_supply/axp20x-battery"
BEHAVIOUR_FILE = os.path.join(BATT_DIR, "charge_behaviour")
CAPACITY_FILE = os.path.join(BATT_DIR, "capacity")

def set_charge(state):
    # state: 'auto' or 'inhibit-charge'
    try:
        with open(BEHAVIOUR_FILE, 'w') as f:
            f.write(state)
        print(f"[AURA-BATT] Set behaviour to: {state}")
    except Exception as e:
        print(f"[AURA-BATT] Error setting state: {e}")

def main():
    print("[AURA-BATT] Daemon started.")
    while True:
        try:
            with open(CAPACITY_FILE, 'r') as f:
                cap = int(f.read().strip())
            
            with open(BEHAVIOUR_FILE, 'r') as f:
                current = f.read().strip()

            if cap >= 60 and "[auto]" in current:
                set_charge("inhibit-charge")
            elif cap <= 40 and "auto" not in current:
                set_charge("auto")
            
            time.sleep(60)
        except Exception as e:
            print(f"[AURA-BATT] Loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
