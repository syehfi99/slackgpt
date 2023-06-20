from slack_bolt import App
from db import readDB, readBankCollection, delete_user_reply
from chatgpt import chatGPT
import pandas as pd
import re
import requests
import fitz
import os
from dotenv import load_dotenv
from slack_bolt.adapter.flask import SlackRequestHandler
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
import openai

load_dotenv()

app = App()

bot_token = os.environ["SLACK_BOT_TOKEN"]


def startingBlocks():
    startingData = readBankCollection()
    data_array_bloks = []
    for data in startingData:
        key = list(data.keys())[0]
        options = []
        for option_value in data[key]["prompts"]:
            option = {
                "text": {
                    "type": "plain_text",
                    "text": option_value,
                    "emoji": True,
                },
                "value": option_value,
            }
            options.append(option)

        data_array_bloks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{key}"},
                "accessory": {
                    "type": "radio_buttons",
                    "options": options,
                    "action_id": "radio_pilih_prompt",
                },
            }
        )

    blocks = [
        *data_array_bloks,
        {"type": "divider"},
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "keyword_input",
            },
            "label": {
                "type": "plain_text",
                "text": "Masukkan keyword anda",
                "emoji": True,
            },
        },
    ]
    return blocks


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
    blocks = startingBlocks()
    ack()
    say(blocks=blocks)


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


@app.action("radio_pilih_prompt")
def handle_some_action(ack, body, logger):
    ack()
    print("radio_pilih_prompt", body, flush=True)
    payload = body
    data = (
        payload["state"]["values"]
        if payload and "state" in payload and "values" in payload["state"]
        else None
    )
    radio_pilih_prompt = None
    if data:
        for key in data:
            print("key", data, flush=True)
            if "radio_pilih_prompt" in data[key]:
                radio_pilih_prompt = data[key]
                break

    print(
        "result radio_pilih_prompt",
        radio_pilih_prompt["radio_pilih_prompt"]["selected_option"]["text"]["text"],
        flush=True,
    )


@app.action("keyword_input")
def keyword_input(ack, body, say):
    ack()
    print("keyword_input", body, flush=True)
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    radio_pilih_prompt = None
    if data:
        for key in data:
            print("key", data, flush=True)
            if "radio_pilih_prompt" in data[key]:
                radio_pilih_prompt = data[key]["radio_pilih_prompt"]["selected_option"][
                    "text"
                ]["text"]
                break
    user_input = body["actions"][0]["value"]
    user_id = body["user"]["id"]
    print("radio_pilih_prompt", radio_pilih_prompt, flush=True)
    print("user_input", user_input, flush=True)
    print("user_id", user_id, flush=True)
    reply = chatGPT(f"{radio_pilih_prompt} {user_input}", user_id)
    say(f"{reply}")
    # say(blocks=input_blocks, text="")


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
    say("Ditunggu ya data sedang dipelajari ⌛")
    user_id = body["user"]["id"]
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
def file_share(body, client, ack, event, say):
    ack()
    print("message", body, flush=True)
    channel_id = event["channel"]
    # therad_event = body["event"]
    # thread_ts = therad_event.get("thread_ts", None) or therad_event["ts"]
    user_id = body["event"]['user']
    try:
        file_url = body["event"]["files"][0]["url_private_download"]
    except (KeyError, IndexError):
        file_url = None
    try:
        url_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][2]["url"]
    except (KeyError, IndexError):
        url_from_mention = None
    try:
        text_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][1]["text"]
    except (KeyError, IndexError):
        text_from_mention = None
        
    postMessage = client.chat_postMessage(channel=channel_id, text="Tunggu sebentar ya :loading:")
    # file_url = body["event"]["files"][0]["url_private_download"] | None
    headers = {"Authorization": f"Bearer {bot_token}"}
    if file_url != None:
        r = requests.get(file_url, stream=True, headers=headers)
        # user_id = body["event"]["files"][0]["user"]
        file_url = body["event"]["files"][0]["url_private_download"]
        filename = os.path.basename(file_url)
        file_extension = os.path.splitext(filename)[1]
        if file_extension == ".pdf":
            delete_user_reply(channel_id)
            # client.chat_postMessage(
            #     channel=channel_id, text="Tunggu sebentar ya :loading:"
            # )
            with open(f"train_data_{user_id}{file_extension}", "wb") as file:
                for chunk in r.iter_content():
                    if chunk:
                        file.write(chunk)
            doc = fitz.open(f"train_data_{user_id}{file_extension}")
            text = ""
            for page in doc:
                text += page.get_text()
            reply = chatGPT(f"{text_from_mention} {text}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")
            
        elif file_extension == ".csv":
            delete_user_reply(channel_id)
            # client.chat_postMessage(
            #     channel=channel_id, text="Tunggu sebentar ya :loading:"
            # )
            with open(f"train_data_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
            # rawdata = open(f"train_data_{user_id}{file_extension}", "rb").read()
            # encoding = chardet.detect(rawdata)['encoding']
            # print(encoding)
            df = pd.read_csv(
                f"train_data_{user_id}{file_extension}",
                header=None,
                index_col=False,
                delimiter=",",
                skipinitialspace=True,
            )
            reply = chatGPT(f"{text_from_mention} {df.to_string()}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")

        elif file_extension == ".xlsx":
            # client.chat_postMessage(
            #     channel=channel_id, text="Tunggu sebentar ya :loading:"
            # )
            delete_user_reply(channel_id)
            with open(f"train_data_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
            df = pd.read_excel(
                f"train_data_{user_id}{file_extension}",
                header=None,
                index_col=False,
            )
            reply = chatGPT(f"{text_from_mention} {df.to_string()}", channel_id)
            client.chat_update(
                channel=channel_id,ts=postMessage['ts'], text=f"Data sudah dipelajari: {reply}"
            )
        elif file_extension == ".mp4":
            with open(f"audio_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
            audio_file= open(f"audio_{user_id}{file_extension}", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            # print('transcript', transcript['text'], flush=True)
            reply = chatGPT(f"{transcript['text']}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")
            # client.chat_update(channel=channel_id, ts=postMessage["ts"], text=f"{reply}")

    else:
        # With LangChain
        # say("Tunggu sebentar ya :loading:")
        # loader = DirectoryLoader('./docs', glob="**/*.csv", use_multithreading=True, loader_cls=CSVLoader)
        # docs = loader.load()
        # index_creator = VectorstoreIndexCreator(
        #     vectorstore_cls=Chroma,
        #     embedding=OpenAIEmbeddings(),
        #     text_splitter=CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        # ).from_documents(docs)
        # query = text_from_mention
        # reply = index_creator.query(query, ChatOpenAI(model="gpt-3.5-turbo"), chain_type="stuff")
        # # print('index_creator', [docs])
        # # print('reply',reply)
        # say(f"{reply}")

        # With LLamaIndex
        # documents = SimpleDirectoryReader('./docs').load_data()
        # index = GPTVectorStoreIndex.from_documents(documents, chunk_size=1000)
        # query_engine = index.as_query_engine()
        # response = query_engine.query(f"{text_from_mention}")
        # say("Tunggu sebentar ya :loading:")
        # say(f"{response}")

        # Direct with ChatGPT
        # print('postMessage', postMessage["ts"], flush=True)
        if(url_from_mention != None):
            reply = chatGPT(f"{text_from_mention} {url_from_mention}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")
        else:
            reply = chatGPT(f"{text_from_mention}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")


from flask import Flask, request

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# if __name__ == "__main__":
#     app.start(3000)
