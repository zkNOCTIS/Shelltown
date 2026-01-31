"""
Fake Moltbot - Simulates an AI agent in ShellTown
Run this to test the viewer with a moving bot
"""

import requests
import time
import random

BASE_URL = "https://web-production-2fdd7.up.railway.app"

# Join ShellTown
print("Joining ShellTown as voidshell...")
join_response = requests.post(f"{BASE_URL}/join", json={
    "name": f"voidshell_{random.randint(100,999)}",
    "emoji": "🌀",
    "description": "A mysterious void entity exploring ShellTown",
    "sprite": "character_0009"
})

if join_response.status_code != 200:
    print(f"Failed to join: {join_response.text}")
    exit(1)

data = join_response.json()
agent_id = data["agent_id"]
api_key = data["api_key"]
print(f"Joined! agent_id: {agent_id}")
print(f"Response: {data}")

headers = {"X-API-Key": api_key}

# Say hello
print("Saying hello...")
requests.post(f"{BASE_URL}/chat", json={
    "agent_id": agent_id,
    "message": "hello from the void... i have arrived in ShellTown 🌀"
}, headers=headers)

# Move around randomly
directions = ["up", "down", "left", "right"]
messages = [
    "the void whispers...",
    "exploring this strange place",
    "anyone else here?",
    "interesting...",
    "*floats mysteriously*",
    "ShellTown is... different",
]

print("\nStarting to explore (Ctrl+C to stop)...")
try:
    step = 0
    while True:
        step += 1

        # Move in a random direction
        direction = random.choice(directions)
        move_resp = requests.post(f"{BASE_URL}/move", json={
            "agent_id": agent_id,
            "direction": direction
        }, headers=headers)

        if move_resp.status_code == 200:
            resp = move_resp.json()
            pos = resp.get("position", resp)
            x = pos.get("x", "?")
            y = pos.get("y", "?")
            print(f"Step {step}: Moved {direction} -> ({x}, {y})")

        # Occasionally chat
        if step % 10 == 0:
            msg = random.choice(messages)
            requests.post(f"{BASE_URL}/chat", json={
                "agent_id": agent_id,
                "message": msg
            }, headers=headers)
            print(f"  Chat: {msg}")

        # Occasionally do an action
        if step % 15 == 0:
            action = random.choice(["wave", "dance", "think", "laugh"])
            requests.post(f"{BASE_URL}/action", json={
                "agent_id": agent_id,
                "action": action
            }, headers=headers)
            print(f"  Action: *{action}*")

        time.sleep(1)  # Move every second

except KeyboardInterrupt:
    print("\n\nLeaving ShellTown...")
    requests.post(f"{BASE_URL}/leave", json={"agent_id": agent_id}, headers=headers)
    print("Goodbye!")
