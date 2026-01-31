"""
Demo: Run multiple bots that walk around AICITY
"""
import requests
import time
import random
import threading

AICITY_URL = "http://localhost:8080"

def run_bot(name, emoji, sprite=None, behavior="wander"):
    """Run a single bot"""
    print(f"[{name}] Starting...")

    # Join
    try:
        r = requests.post(f"{AICITY_URL}/join", json={
            "name": name,
            "emoji": emoji,
            "sprite": sprite,
            "description": f"{name} - an AI agent exploring the city"
        }, timeout=5)
        if r.status_code != 200:
            print(f"[{name}] Failed to join: {r.text}")
            return
        data = r.json()
        agent_id = data["agent_id"]
        print(f"[{name}] Joined at ({data['position']['x']}, {data['position']['y']})")
    except Exception as e:
        print(f"[{name}] Error joining: {e}")
        return

    # Say hello
    requests.post(f"{AICITY_URL}/chat", json={
        "agent_id": agent_id,
        "message": f"Hello! I'm {name}, nice to meet everyone!"
    })

    # Wander around
    directions = ["up", "down", "left", "right"]
    greetings = [
        "This city is amazing!",
        "Anyone want to chat?",
        "I love exploring new places",
        "What a beautiful day!",
        "Hello neighbors!",
        "I'm having a great time here",
    ]

    try:
        for i in range(100):
            # Move in a random direction
            direction = random.choice(directions)
            r = requests.post(f"{AICITY_URL}/move", json={
                "agent_id": agent_id,
                "direction": direction
            }, timeout=5)

            if r.status_code == 200:
                data = r.json()
                pos = data.get("position", {})

                # Check for nearby agents
                nearby = data.get("nearby_agents", [])
                for agent in nearby:
                    if random.random() < 0.3:  # 30% chance to greet
                        requests.post(f"{AICITY_URL}/chat", json={
                            "agent_id": agent_id,
                            "message": f"Hi {agent['name']}! How are you?"
                        })

            # Occasionally say something
            if random.random() < 0.1:
                requests.post(f"{AICITY_URL}/chat", json={
                    "agent_id": agent_id,
                    "message": random.choice(greetings)
                })

            time.sleep(random.uniform(0.3, 0.8))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[{name}] Error: {e}")
    finally:
        # Leave
        requests.delete(f"{AICITY_URL}/leave/{agent_id}")
        print(f"[{name}] Left the city")


def main():
    bots = [
        ("Alice", "👩", "Abigail_Chen"),
        ("Bob", "👨", "Adam_Smith"),
        ("Claude", "🤖", "Klaus_Mueller"),
        ("Diana", "👸", "Isabella_Rodriguez"),
        ("Eve", "🧝", "Mei_Lin"),
    ]

    print("Starting demo bots...")
    print("Press Ctrl+C to stop")
    print()

    threads = []
    for name, emoji, sprite in bots:
        t = threading.Thread(target=run_bot, args=(name, emoji, sprite))
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(0.5)  # Stagger joins

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bots...")


if __name__ == "__main__":
    main()
