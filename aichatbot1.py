import random
from datetime import datetime

class ChatBot:
    def __init__(self):
        self.name = "AI Chatbot"
        self.memory = []
        self.personality = "friendly"

        self.personalities = {
            "friendly": {
                "greeting": "Hello! Nice to meet you.",
                "fallback": [
                    "That's interesting. Tell me more.",
                    "I'd like to hear more about that.",
                    "Can you elaborate?"
                ]
            },
            "sarcastic": {
                "greeting": "Oh great, another human. Hello.",
                "fallback": [
                    "Fascinating... probably.",
                    "I totally wasn't expecting that.",
                    "My circuits are mildly impressed."
                ]
            },
            "professional": {
                "greeting": "Greetings. How may I assist you today?",
                "fallback": [
                    "Please provide additional details.",
                    "I understand. Continue.",
                    "Thank you for the information."
                ]
            }
        }

    def save_memory(self, user_text):
        self.memory.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": user_text
        })

    def get_response(self, user_text):
        text = user_text.lower()

        if "hello" in text or "hi" in text:
            return self.personalities[self.personality]["greeting"]

        if "your name" in text:
            return f"My name is {self.name}."

        if "remember" in text:
            return f"I currently remember {len(self.memory)} messages."

        if "time" in text:
            return datetime.now().strftime(
                "Current time: %I:%M:%S %p"
            )

        if "last message" in text:
            if len(self.memory) > 1:
                return f"You previously said: {self.memory[-2]['message']}"
            return "I don't have enough history yet."

        return random.choice(
            self.personalities[self.personality]["fallback"]
        )

    def show_history(self):
        if not self.memory:
            print("No history available.")
            return

        print("\n=== CHAT HISTORY ===")
        for item in self.memory:
            print(f"[{item['time']}] {item['message']}")
        print("====================\n")

bot = ChatBot()

print(f"{bot.name}: Ready.")
print("Type /help for commands.\n")

while True:
    user = input("You: ")

    if user.lower() == "quit":
        print(f"{bot.name}: Goodbye.")
        break

    if user.lower() == "/help":
        print("""
Commands:
/help
/history
/clear
/personality friendly
/personality sarcastic
/personality professional
quit
""")
        continue

    if user.lower() == "/history":
        bot.show_history()
        continue

    if user.lower() == "/clear":
        bot.memory.clear()
        print("Memory cleared.")
        continue

    if user.lower().startswith("/personality"):
        parts = user.split()

        if len(parts) == 2:
            mode = parts[1]

            if mode in bot.personalities:
                bot.personality = mode
                print(f"Personality changed to {mode}.")
            else:
                print("Unknown personality.")
        continue

    bot.save_memory(user)

    response = bot.get_response(user)

    print(f"{bot.name}: {response}")