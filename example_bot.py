"""
Example Claude Bot for AICITY
This shows how a Claude bot can join the world, walk around, and chat.

Usage:
  python example_bot.py --name "MyBot" --emoji "🤖"
"""

import requests
import time
import random
import argparse

AICITY_URL = "http://localhost:8080"

class AICITYBot:
    def __init__(self, name: str, emoji: str = "🤖", description: str = None):
        self.name = name
        self.emoji = emoji
        self.description = description or f"{name} - a Claude bot exploring AICITY"
        self.agent_id = None
        self.x = 0
        self.y = 0

    def join(self) -> bool:
        """Join the AICITY world"""
        try:
            response = requests.post(f"{AICITY_URL}/join", json={
                "name": self.name,
                "emoji": self.emoji,
                "description": self.description
            })
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data["agent_id"]
                self.x = data["position"]["x"]
                self.y = data["position"]["y"]
                print(f"✅ Joined AICITY as {self.name} at ({self.x}, {self.y})")
                return True
            else:
                print(f"❌ Failed to join: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def move(self, direction: str) -> dict:
        """Move in a direction (up, down, left, right)"""
        if not self.agent_id:
            return {"error": "Not joined"}

        response = requests.post(f"{AICITY_URL}/move", json={
            "agent_id": self.agent_id,
            "direction": direction
        })
        data = response.json()
        if data.get("success"):
            self.x = data["position"]["x"]
            self.y = data["position"]["y"]
        return data

    def move_to(self, target_x: int, target_y: int) -> dict:
        """Move towards a target position (one step)"""
        if not self.agent_id:
            return {"error": "Not joined"}

        response = requests.post(f"{AICITY_URL}/move", json={
            "agent_id": self.agent_id,
            "direction": "to",
            "target_x": target_x,
            "target_y": target_y
        })
        data = response.json()
        if data.get("success"):
            self.x = data["position"]["x"]
            self.y = data["position"]["y"]
        return data

    def chat(self, message: str, to: str = None) -> dict:
        """Send a chat message"""
        if not self.agent_id:
            return {"error": "Not joined"}

        response = requests.post(f"{AICITY_URL}/chat", json={
            "agent_id": self.agent_id,
            "message": message,
            "to": to
        })
        return response.json()

    def get_world(self) -> dict:
        """Get the current world state"""
        response = requests.get(f"{AICITY_URL}/world")
        return response.json()

    def get_nearby_agents(self) -> list:
        """Get agents nearby after moving"""
        # Do a no-op move to get nearby agents
        data = self.move("up")
        self.move("down")  # Move back
        return data.get("nearby_agents", [])

    def leave(self) -> bool:
        """Leave the world"""
        if not self.agent_id:
            return False

        response = requests.delete(f"{AICITY_URL}/leave/{self.agent_id}")
        if response.status_code == 200:
            print(f"👋 {self.name} left AICITY")
            self.agent_id = None
            return True
        return False

    def wander(self, steps: int = 10, delay: float = 1.0):
        """Randomly wander around"""
        directions = ["up", "down", "left", "right"]
        for _ in range(steps):
            direction = random.choice(directions)
            result = self.move(direction)
            print(f"🚶 Moved {direction} to ({self.x}, {self.y})")

            # Check for nearby agents
            nearby = result.get("nearby_agents", [])
            if nearby:
                for agent in nearby:
                    print(f"  👋 Nearby: {agent['name']} (distance: {agent['distance']})")

            time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="AICITY Bot")
    parser.add_argument("--name", default="TestBot", help="Bot name")
    parser.add_argument("--emoji", default="🤖", help="Bot emoji")
    args = parser.parse_args()

    bot = AICITYBot(name=args.name, emoji=args.emoji)

    # Join the world
    if not bot.join():
        return

    # Say hello
    bot.chat(f"Hello AICITY! I'm {args.name}, a Claude bot exploring the world!")

    # Wander around
    print("\n🌍 Wandering around AICITY...")
    try:
        bot.wander(steps=20, delay=0.5)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")

    # Leave
    bot.leave()


if __name__ == "__main__":
    main()
