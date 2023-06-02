import openai
import os
from db import save_user_reply, get_user_reply
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
# messages = []
# message_history = [{"role": "system", "content": "You are a intelligent assistant."}]


def chatGPT(message, user_id):
    if message:
        # message_history.append(
        #     {"role": "user", "content": message},
        # )
        save_user_reply({"role": "user", "content": message}, user_id)
        chat_db = get_user_reply(user_id)
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=chat_db['chat']
        )
        reply = chat.choices[0].message.content
        # message_history.append({"role": "assistant", "content": reply})
        save_user_reply({"role": "assistant", "content": reply}, user_id)
        return reply
