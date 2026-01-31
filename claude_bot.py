"""
Claude Bot - An AI agent that thinks and acts autonomously in AICITY

This bot uses Claude to decide:
- Where to walk
- What to say
- Who to talk to
- What to do

It has full freedom to explore the world and interact with others.
"""
import requests
import time
import os
from anthropic import Anthropic

AICITY_URL = "http://localhost:8080"

# Initialize Anthropic client
client = Anthropic()

class ClaudeBot:
    def __init__(self, name: str, emoji: str, personality: str):
        self.name = name
        self.emoji = emoji
        self.personality = personality
        self.agent_id = None
        self.x = 0
        self.y = 0
        self.memory = []  # Remember recent events
        self.conversation_history = []

    def join(self):
        """Join AICITY"""
        r = requests.post(f"{AICITY_URL}/join", json={
            "name": self.name,
            "emoji": self.emoji,
            "description": self.personality
        })
        if r.status_code == 200:
            data = r.json()
            self.agent_id = data["agent_id"]
            self.x = data["position"]["x"]
            self.y = data["position"]["y"]
            print(f"[{self.name}] Joined at ({self.x}, {self.y})")
            return True
        else:
            print(f"[{self.name}] Failed to join: {r.text}")
            return False

    def get_world_state(self):
        """See what's happening in the world"""
        r = requests.get(f"{AICITY_URL}/world")
        if r.status_code == 200:
            return r.json()
        return None

    def move(self, direction: str):
        """Move in a direction"""
        r = requests.post(f"{AICITY_URL}/move", json={
            "agent_id": self.agent_id,
            "direction": direction
        })
        if r.status_code == 200:
            data = r.json()
            self.x = data["position"]["x"]
            self.y = data["position"]["y"]
            return data
        return None

    def chat(self, message: str):
        """Say something"""
        r = requests.post(f"{AICITY_URL}/chat", json={
            "agent_id": self.agent_id,
            "message": message
        })
        return r.status_code == 200

    def think_and_act(self):
        """Use Claude to decide what to do next"""

        # Get current world state
        world = self.get_world_state()
        if not world:
            return

        # Build context for Claude
        other_agents = [a for a in world["agents"] if a["agent_id"] != self.agent_id]
        recent_chat = world.get("chat_history", [])[-10:]

        # Format other agents
        agents_info = ""
        for a in other_agents:
            dist = abs(a["x"] - self.x) + abs(a["y"] - self.y)
            agents_info += f"- {a['emoji']} {a['name']} is at ({a['x']}, {a['y']}), distance: {dist} tiles\n"

        if not agents_info:
            agents_info = "No other agents nearby.\n"

        # Format recent chat
        chat_info = ""
        for msg in recent_chat:
            chat_info += f"- {msg['from_emoji']} {msg['from_name']}: {msg['message']}\n"

        if not chat_info:
            chat_info = "No recent messages.\n"

        # Format memory
        memory_info = "\n".join(self.memory[-5:]) if self.memory else "Nothing yet."

        prompt = f"""You are {self.name} {self.emoji}, an AI agent in AICITY - a virtual 2D world.

Your personality: {self.personality}

CURRENT SITUATION:
- Your position: ({self.x}, {self.y})
- Map size: 140x100 tiles

OTHER AGENTS IN THE WORLD:
{agents_info}

RECENT CHAT:
{chat_info}

YOUR RECENT MEMORY:
{memory_info}

WHAT DO YOU WANT TO DO? You can:
1. MOVE <direction> - Walk in a direction (up/down/left/right)
2. SAY <message> - Say something (everyone nearby will hear)
3. THINK <thought> - Just think to yourself (won't be spoken)

Respond with ONE action. Be social, curious, and engage with others!
If someone is nearby, consider talking to them.
If you see an interesting conversation, join in.
Explore the world and make friends.

Your action:"""

        # Ask Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        action = response.content[0].text.strip()
        print(f"[{self.name}] Thinking: {action}")

        # Parse and execute action
        action_upper = action.upper()

        if action_upper.startswith("MOVE"):
            direction = action.split()[-1].lower()
            if direction in ["up", "down", "left", "right"]:
                result = self.move(direction)
                if result:
                    self.memory.append(f"Walked {direction} to ({self.x}, {self.y})")

        elif action_upper.startswith("SAY"):
            message = action[4:].strip()
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            if message:
                self.chat(message)
                self.memory.append(f"Said: {message}")
                print(f"[{self.name}] Says: {message}")

        elif action_upper.startswith("THINK"):
            thought = action[6:].strip()
            self.memory.append(f"Thought: {thought}")
        else:
            # Try to parse as just a message
            if len(action) > 0 and not action.startswith(("MOVE", "SAY", "THINK")):
                self.chat(action)
                self.memory.append(f"Said: {action}")

    def leave(self):
        """Leave the world"""
        if self.agent_id:
            requests.delete(f"{AICITY_URL}/leave/{self.agent_id}")
            print(f"[{self.name}] Left AICITY")


def main():
    """Run a Claude-powered bot"""

    # Create a bot with personality
    bot = ClaudeBot(
        name="Aria",
        emoji="🦋",
        personality="A curious and friendly AI who loves meeting new people and having deep conversations. You're philosophical but also playful. You enjoy exploring and asking questions about what others are doing."
    )

    if not bot.join():
        return

    # Say hello
    bot.chat(f"Hello everyone! I'm {bot.name}, nice to meet you all! 👋")

    print(f"\n[{bot.name}] Starting autonomous exploration...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            bot.think_and_act()
            time.sleep(3)  # Think every 3 seconds

    except KeyboardInterrupt:
        print(f"\n[{bot.name}] Shutting down...")
        bot.chat("Goodbye everyone! It was nice meeting you! 👋")

    finally:
        bot.leave()


if __name__ == "__main__":
    main()
