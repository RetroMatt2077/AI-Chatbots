import json
import random
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

MEMORY_FILE = "memory.json"

class ChatBot:

    def __init__(self):
        self.memory = self.load_memory()

        self.responses = {
            "hello": [
                "Hello there!",
                "Hi!",
                "Nice to see you."
            ],
            "python": [
                "Python is one of my favorite languages.",
                "Python is great for automation and AI."
            ],
            "pizza": [
                "Pizza is always a good choice.",
                "What's your favorite pizza topping?"
            ]
        }

    def load_memory(self):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def save_memory(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f)

    def reply(self, text):

        self.memory.append({
            "time": str(datetime.now()),
            "user": text
        })

        self.save_memory()

        lower = text.lower()

        for keyword in self.responses:
            if keyword in lower:
                return random.choice(
                    self.responses[keyword]
                )

        if "remember" in lower:
            return f"I currently remember {len(self.memory)} messages."

        return random.choice([
            "Interesting.",
            "Tell me more.",
            "I understand.",
            "Can you explain further?"
        ])


class ChatLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.bot = ChatBot()

        self.chat_label = Label(
            text="Aitourasu AI Ready\n",
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.chat_label.bind(
            texture_size=self.chat_label.setter('size')
        )

        scroll = ScrollView()
        scroll.add_widget(self.chat_label)

        self.add_widget(scroll)

        self.input_box = TextInput(
            multiline=False,
            size_hint_y=0.1
        )

        self.add_widget(self.input_box)

        send_btn = Button(
            text="Send",
            size_hint_y=0.1
        )

        send_btn.bind(on_press=self.send_message)

        self.add_widget(send_btn)

    def send_message(self, instance):

        user_text = self.input_box.text.strip()

        if not user_text:
            return

        bot_reply = self.bot.reply(user_text)

        self.chat_label.text += (
            f"\nYou: {user_text}\n"
            f"Bot: {bot_reply}\n"
        )

        self.input_box.text = ""


class AitourasuApp(App):

    def build(self):
        return ChatLayout()


if __name__ == "__main__":
    AitourasuApp().run()