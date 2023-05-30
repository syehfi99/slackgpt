import openai
import os


openai.api_key = os.environ["OPENAI_API_KEY"]
# messages = []
message_history = [{"role": "system", "content": "You are a intelligent assistant."}]


def chatGPT(message):
    if message:
        message_history.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=message_history
        )
        reply = chat.choices[0].message.content
        message_history.append({"role": "assistant", "content": reply})
        return reply
