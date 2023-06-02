from slack_bolt import App
from db import readDB, delete_user_reply
from chatgpt import chatGPT
import pandas as pd
import re
import requests
import fitz
import os
from dotenv import load_dotenv
from slack_bolt.adapter.flask import SlackRequestHandler
import chardet

load_dotenv()

app = App()

bot_token = os.environ["SLACK_BOT_TOKEN"]

blocks = [
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "Pilih prompt yang akan digunakan"},
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "SEO"},
                "value": "seo",
                "action_id": "seo",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Finance"},
                "value": "finance",
                "action_id": "finance",
            },
        ],
    },
]

input_blocks = [
    {
        "dispatch_action": True,
        "type": "input",
        "block_id": "input123",
        "label": {"type": "plain_text", "text": "Isi keyword"},
        "element": {
            "type": "plain_text_input",
            "action_id": "keyword_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
        },
    }
]

input_train_blocks = [
    {
        "dispatch_action": True,
        "type": "input",
        "block_id": "input123",
        "label": {"type": "plain_text", "text": "Input url"},
        "element": {
            "type": "plain_text_input",
            "action_id": "train_input",
            "placeholder": {"type": "plain_text", "text": "Enter some plain text"},
        },
    }
]

store_prompt = ""


# Add functionality here
@app.command("/devgpt-prompt")
def prompt_chat(ack, say, command):
    ack()
    say(blocks=blocks, text="Pilih prompt yang digunakan")


@app.command("/devgpt-write")
def chatWithGPT(ack, say, command):
    ack()
    say(blocks=input_blocks, text="")


@app.action("seo")
def prompt_seo(ack, respond, body):
    ack()
    respond(blocks=input_blocks)
    global store_prompt
    store_prompt = body["actions"][0]["value"]


@app.action("finance")
def prompt_finance(ack, respond, body):
    ack()
    global store_prompt
    store_prompt = body["actions"][0]["value"]
    respond(blocks=input_blocks)


@app.action("keyword_input")
def keyword_input(ack, body, say):
    ack()
    print(body)
    user_id = body["user"]['id']
    if store_prompt != "":
        prompt = readDB(store_prompt)
        print("ini prompt", prompt)
        reply = chatGPT(prompt["prompt"] + " " + body["actions"][0]["value"])
        say(f"{reply}")
        say(blocks=input_blocks, text="")

    reply = chatGPT(body["actions"][0]["value"], user_id)
    say(f"{reply}")
    say(blocks=input_blocks, text="")


# -----------------------------------


# ----------- Train data ------------
@app.command("/devgpt-train")
def trainWithGPT(ack, say, command):
    ack()
    say(blocks=input_train_blocks, text="Train with url gspread/url with pdf")


@app.action("train_input")
def train_input(ack, body, say):
    ack()
    print(body)
    say('Ditunggu ya data sedang dipelajari ⌛')
    user_id = body["user"]['id']
    sliced_url = "/".join(body["actions"][0]["value"].split("/")[:4])
    # print(sheet_id)
    if sliced_url == "https://docs.google.com/spreadsheets":
        sheet_id = re.search(r"/d/(.+)/", body["actions"][0]["value"]).group(1)
        print("sheet_id", sheet_id)
        df = pd.read_csv(
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
            header=None,
            index_col=False,
        )
        print(df.to_string())
        reply = chatGPT(f"pelajari data berikut: {df.to_string()}", user_id)
        print("reply", reply)
        say(f"{reply}")
        say(blocks=input_blocks, text="")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        file_url = body["actions"][0]["value"]
        r = requests.get(file_url, stream=True, headers=headers)
        print(r)
        with open(f"train_data_{body['user']['id']}.pdf", "wb") as file:
            for chunk in r.iter_content():
                if chunk:
                    file.write(chunk)

        doc = fitz.open(f"train_data_{body['user']['id']}.pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        print(text)
        reply = chatGPT(f"pelajari data berikut: {text}", user_id)
        print("reply", reply)
        say(f"Data sudah dipelajari, {reply}")
        say(blocks=input_blocks, text="")


@app.event("app_mention")
def file_share(body, say, ack):
    ack()
    say(text='Ditunggu ya data sedang dipelajari ⌛')
    headers = {
        "Authorization": f"Bearer {bot_token}"
    }
    text_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][1]['text']
    user_id = body["event"]["files"][0]["user"]
    file_url = body["event"]["files"][0]["url_private_download"]
    filename = os.path.basename(file_url)
    file_extension = os.path.splitext(filename)[1]
    delete_user_reply(user_id)
    r = requests.get(file_url, stream=True, headers=headers)
    
    if file_extension == ".pdf":
        with open(f"train_data_{user_id}{file_extension}", "wb") as file:
            for chunk in r.iter_content():
                if chunk:
                    file.write(chunk)
        doc = fitz.open(f"train_data_{user_id}{file_extension}")
        text = ""
        for page in doc:
            text += page.get_text()
        print(text)
        reply = chatGPT(f"{text_from_mention} {text}", user_id)
        print("reply", reply)
        say(f"Data sudah dipelajari: {reply}")
        say(blocks=input_blocks, text="")
    elif file_extension == ".csv":
        with open(f"train_data_{user_id}{file_extension}", "wb") as file:
            file.write(r.content)
        # rawdata = open(f"train_data_{user_id}{file_extension}", "rb").read()
        # encoding = chardet.detect(rawdata)['encoding']
        # print(encoding)
        df = pd.read_csv(
            f"train_data_{user_id}{file_extension}",
            header=None,
            index_col=False,
        )
        # print(df.to_string())
        reply = chatGPT(f"{text_from_mention} {df.to_string()}", user_id)
        print("reply", reply)
        say(f"Data sudah dipelajari: {reply}")
        say(blocks=input_blocks, text="")

    elif file_extension == ".xlsx":
        with open(f"train_data_{user_id}{file_extension}", "wb") as file:
            file.write(r.content)
        df = pd.read_excel(
            f"train_data_{user_id}{file_extension}",
            header=None,
            index_col=False,
        )
        # print(df.to_string())
        reply = chatGPT(f"{text_from_mention} {df.to_string()}", user_id)
        print("reply", reply)
        say(f"Data sudah dipelajari: {reply}")
        say(blocks=input_blocks, text="")


from flask import Flask, request

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# if __name__ == "__main__":
#     app.start(3000)
