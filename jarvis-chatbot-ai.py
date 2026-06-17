import random
import threading
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from openai import OpenAI

# ==========================
# CONFIG
# ==========================

API_KEY = "YOUR API KEY HERE"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

MODEL = "meta-llama/llama-3.1-8b-instruct"

JARVIS_SYSTEM_PROMPT = """
You are Jarvis.

You are intelligent, helpful, slightly witty,
and act like a personal AI assistant.

Keep responses concise.
"""

MOODS = [
    "happy",
    "curious",
    "focused",
    "sarcastic"
]

TOPICS = [
    "helicopters",
    "technology",
    "python programming",
    "space",
    "history",
    "fantasy RPGs"
]

IDLE_MESSAGES = [
    "All systems appear operational.",
    "I've been analyzing interesting ideas.",
    "Ready when you are.",
    "I enjoy our conversations.",
    "Monitoring systems.",
    "I've been thinking about technology."
]


class ChatBot(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            **kwargs
        )

        self.current_mood = random.choice(MOODS)
        self.silent_mode = False
        self.favorite_topics = {}

        self.messages = [
            {
                "role": "system",
                "content": JARVIS_SYSTEM_PROMPT
            }
        ]

        # ==================
        # CHAT WINDOW
        # ==================

        self.chat = TextInput(
            text="",
            readonly=True,
            multiline=True,
            size_hint=(1, 0.88)
        )

        self.add_widget(self.chat)

        # ==================
        # USER INPUT
        # ==================

        self.input_box = TextInput(
            multiline=False,
            size_hint=(1, 0.06)
        )

        self.input_box.bind(
            on_text_validate=self.send_message
        )

        self.add_widget(self.input_box)

        # ==================
        # SEND BUTTON
        # ==================

        send_button = Button(
            text="Send",
            size_hint=(1, 0.06)
        )

        send_button.bind(
            on_press=self.send_message
        )

        self.add_widget(send_button)

        # Greeting

        hour = datetime.now().hour

        if hour < 12:
            greeting = "Good morning."
        elif hour < 18:
            greeting = "Good afternoon."
        else:
            greeting = "Good evening."

        self.add_chat(
            f"Jarvis: {greeting} Systems operational."
        )

        # Timers

        Clock.schedule_interval(
            self.change_mood,
            300
        )

        Clock.schedule_interval(
            self.hour_check,
            60
        )

        self.schedule_idle_message()

    def add_chat(self, text):

        self.chat.text += text + "\n"

        # Auto-scroll to bottom
        self.chat.cursor = (
            len(self.chat.text),
            0
        )

    def schedule_idle_message(self):

        delay = random.randint(30, 90)

        Clock.schedule_once(
            self.random_idle_message,
            delay
        )

    def random_idle_message(self, dt):

        if not self.silent_mode:

            msg = random.choice(
                IDLE_MESSAGES
            )

            self.add_chat(
                f"Jarvis [{self.current_mood}]: {msg}"
            )

        self.schedule_idle_message()

    def change_mood(self, dt):

        self.current_mood = random.choice(
            MOODS
        )

        if not self.silent_mode:

            self.add_chat(
                f"Jarvis mood changed to "
                f"{self.current_mood}."
            )

    def hour_check(self, dt):

        now = datetime.now()

        if now.minute == 0:

            self.add_chat(
                f"Jarvis: The time is "
                f"{now.strftime('%I:%M %p')}."
            )

    def send_message(self, *args):

        text = self.input_box.text.strip()

        if not text:
            return

        self.input_box.text = ""

        # Commands

        if text == "/silent":

            self.silent_mode = True

            self.add_chat(
                "Jarvis: Silent mode enabled."
            )

            return

        if text == "/talk":

            self.silent_mode = False

            self.add_chat(
                "Jarvis: Random chatter enabled."
            )

            return

        # Track interests

        for topic in TOPICS:

            if topic.lower() in text.lower():

                self.favorite_topics[topic] = (
                    self.favorite_topics.get(
                        topic,
                        0
                    ) + 1
                )

        self.add_chat(
            f"You: {text}"
        )

        self.messages.append(
            {
                "role": "user",
                "content": text
            }
        )

        threading.Thread(
            target=self.get_ai_response,
            daemon=True
        ).start()

    def get_ai_response(self):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                max_tokens=300
            )

            reply = (
                response
                .choices[0]
                .message
                .content
            )

            self.messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )

            Clock.schedule_once(
                lambda dt:
                self.add_chat(
                    f"Jarvis: {reply}"
                )
            )

        except Exception as e:

            Clock.schedule_once(
                lambda dt:
                self.add_chat(
                    f"ERROR: {e}"
                )
            )


class JarvisApp(App):

    def build(self):
        return ChatBot()


if __name__ == "__main__":
    JarvisApp().run()