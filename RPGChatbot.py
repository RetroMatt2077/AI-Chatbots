import json
import os
import threading
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from openai import OpenAI

# ==================================
# CONFIG
# ==================================

OPENROUTER_API_KEY = "YOUR API KEY HERE"

MODEL = "meta-llama/llama-3.1-8b-instruct"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

DATA_FILE = "aitourasu_data.json"

# ==================================
# PERSONALITIES
# ==================================

PERSONALITIES = {
    "jarvis":
        "You are Jarvis, an intelligent and helpful AI assistant.",

    "programmer":
        "You are an expert software engineer. Give code examples and explain clearly.",

    "teacher":
        "You are an experienced teacher. Explain concepts step-by-step.",

    "comedian":
        "You are a witty comedian who enjoys humor and clever jokes.",

    "dungeonmaster":
        """
You are a fantasy RPG Dungeon Master.

Track:
- Health
- Gold
- Inventory
- Quests
- Locations

Rules:
- Create monsters and treasure.
- Present choices.
- Never choose actions for the player.
- Remember previous events.
- Keep track of stats.
- Start in the village of Black Hollow.
"""
}

# ==================================
# STORAGE
# ==================================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return {
        "notes": [],
        "history": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==================================
# CHATBOT
# ==================================

class ChatBot(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.data = load_data()

        self.current_personality = "jarvis"

        self.messages = [
            {
                "role": "system",
                "content": PERSONALITIES["jarvis"]
            }
        ]

        scroll = ScrollView()

        self.chat = Label(
            text="Aitourasu AI Online\n\nType /help\n",
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.chat.bind(
            texture_size=self.chat.setter("size")
        )

        scroll.add_widget(self.chat)

        self.add_widget(scroll)

        self.input_box = TextInput(
            multiline=False,
            size_hint_y=0.12
        )

        self.input_box.bind(
            on_text_validate=self.send_message
        )

        self.add_widget(self.input_box)

        send_button = Button(
            text="Send",
            size_hint_y=0.12
        )

        send_button.bind(on_press=self.send_message)

        self.add_widget(send_button)

    def add_chat(self, text):
        self.chat.text += text + "\n"

    def send_message(self, *args):

        user_text = self.input_box.text.strip()

        if not user_text:
            return

        self.input_box.text = ""

        # Help
        if user_text == "/help":

            self.add_chat("""
Commands:
/help
/personalities
/personality jarvis
/personality programmer
/personality teacher
/personality comedian
/personality dungeonmaster
/start
/note your note here
/notes
/clear
""")

            return

        # List personalities
        if user_text == "/personalities":

            self.add_chat(
                "Available:\n" +
                "\n".join(PERSONALITIES.keys())
            )

            return

        # Change personality
        if user_text.startswith("/personality"):

            parts = user_text.split()

            if len(parts) == 2:

                mode = parts[1].lower()

                if mode in PERSONALITIES:

                    self.current_personality = mode

                    self.messages = [
                        {
                            "role": "system",
                            "content": PERSONALITIES[mode]
                        }
                    ]

                    self.add_chat(
                        f"System: Personality changed to {mode}"
                    )

                else:
                    self.add_chat(
                        "System: Unknown personality."
                    )

            return

        # RPG Start
        if user_text == "/start":

            self.messages.append({
                "role": "user",
                "content":
                    "Begin the adventure. Show stats and choices."
            })

            threading.Thread(
                target=self.get_ai_response,
                daemon=True
            ).start()

            return

        # Notes
        if user_text.startswith("/note "):

            note = user_text[6:]

            self.data["notes"].append(note)

            save_data(self.data)

            self.add_chat(
                f"Note saved: {note}"
            )

            return

        if user_text == "/notes":

            if not self.data["notes"]:
                self.add_chat("No notes saved.")
            else:
                self.add_chat(
                    "Notes:\n" +
                    "\n".join(self.data["notes"])
                )

            return

        if user_text == "/clear":

            self.messages = [
                {
                    "role": "system",
                    "content":
                        PERSONALITIES[self.current_personality]
                }
            ]

            self.add_chat("Conversation cleared.")

            return

        self.add_chat(f"You: {user_text}")

        self.messages.append({
            "role": "user",
            "content": user_text
        })

        threading.Thread(
            target=self.get_ai_response,
            daemon=True
        ).start()

    def get_ai_response(self):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                max_tokens=500
            )

            reply = response.choices[0].message.content

            self.messages.append({
                "role": "assistant",
                "content": reply
            })

            self.data["history"].append({
                "time": str(datetime.now()),
                "message": reply
            })

            save_data(self.data)

            Clock.schedule_once(
                lambda dt: self.add_chat(
                    f"AI: {reply}"
                )
            )

        except Exception as e:

            Clock.schedule_once(
                lambda dt: self.add_chat(
                    f"ERROR:\n{str(e)}"
                )
            )

# ==================================
# APP
# ==================================

class AitourasuApp(App):

    def build(self):
        return ChatBot()

if __name__ == "__main__":
    AitourasuApp().run()