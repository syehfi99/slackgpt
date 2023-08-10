import openai
import os
from db import save_user_reply, get_user_reply, delete_user_reply
from dotenv import load_dotenv
import tiktoken

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
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_token = 0
        for message in chat_db:
            for key, value in message.items():
                num_token += len(encoding.encode(value))
        print("num_tokens", num_token, flush=True)
        if num_token < 4096:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=chat_db, temperature=0.3
            )
            reply = chat.choices[0].message.content
            save_user_reply({"role": "assistant", "content": reply}, user_id)
            return reply
        else:
            reply = f"_*Error! token used: {num_token}, please reduce your prompt*_"
            delete_user_reply(user_id)
            return reply



def generateImage(message):
    response = openai.Image.create(prompt=message, n=1, size="512x512")
    image_url = response["data"][0]["url"]
    return image_url
