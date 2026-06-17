from openai import OpenAI

client = OpenAI(
    api_key="YOUR API KEY HERE"
)

def ask_jarvis(message, personality):

    system_prompt = {
        "Jarvis":
            "You are JARVIS from Iron Man. Intelligent, concise, professional.",

        "Friendly":
            "You are a friendly helpful AI.",

        "RPG":
            "You are a fantasy RPG game master."
    }

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role":"system","content":system_prompt[personality]},
            {"role":"user","content":message}
        ]
    )

    return response.choices[0].message.content