import random
import time
import threading
import sys

chaos_mode = False

def keyboard_listener():
    global chaos_mode
    while True:
        user_input = sys.stdin.readline().strip().lower()
        if user_input == 'chaos':
            chaos_mode = True
            print("[CHAOS] Spike triggered! Temp jumping to 95.0")
            time.sleep(3)
            chaos_mode = False
            print("[CHAOS] Normal mode resumed")

listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
listener_thread.start()

print("Data Generator Started")
print("Type 'chaos' + Enter to trigger a spike")
print("-" * 40)

while True:
    if chaos_mode:
        temp = 95.0
    else:
        temp = round(random.uniform(40.0, 50.0), 2)

    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] CPU Temp: {temp}°C")
    time.sleep(1)
