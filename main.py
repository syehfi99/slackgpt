from slack_bolt import App
from db import (
    readPromptCollection,
    readPromptByName,
    writePrompt,
    updatePrompt,
    deletePrompt,
    readPromptByKey,
)
from chatgpt import chatGPT
from direct_message import direct_message_to_bot
from block_kit_generator import generateSelectPromptPrivate
from message_mention import message_bot_with_mention
import re
import os
from dotenv import load_dotenv
from slack_bolt.adapter.flask import SlackRequestHandler
from block_kit_generator import generateAllPromptButton

# from langchain.document_loaders import DirectoryLoader
# from langchain.document_loaders.csv_loader import CSVLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.chat_models import ChatOpenAI

load_dotenv()

app = App()

bot_token = os.environ["SLACK_BOT_TOKEN"]


# show all exist prompt from the bot DM
@app.message(re.compile("(prompt all)"))
def block_kit_message(say, context, ack):
    context["matches"][0]
    blocks = generateAllPromptButton()
    ack()
    say(blocks=blocks)


# show help commands DM
@app.message(re.compile("(help)"))
def block_kit_message(say, context, ack):
    context["matches"][0]
    text = "Bantuan Slack GPT:\n\n1. `prompt all`, menampilkan pilihan prompt dari semua channel\n2. `prompt [nama channel]`, menampilkan prompt sesuai nama channel"
    ack()
    say(f"{text}")


# read all data prompts
startingData = readPromptCollection()
dictData = "|".join(startingData["prompt_name"])
dictDataDM = []
for data in startingData["prompt_name"]:
    prompt = f"prompt {data}"
    dictDataDM.append(prompt)

# print("dictData", dictData, flush=True)
# print("dictDataDM", dictDataDM, flush=True)


@app.message(re.compile("|".join(dictDataDM)))
def block_kit_message(body, ack, say):
    ack()
    key = body["event"]["text"].split(" ")[1]
    prompts = readPromptByName(key)
    blocks = generateSelectPromptPrivate(prompts, key)
    say(blocks=blocks)


# action button prompt all
@app.action(re.compile(dictData))
def prompt_by_category(body, ack, respond):
    ack()
    key = body["actions"][0]["value"]
    prompts = readPromptByName(key)
    blocks = generateSelectPromptPrivate(prompts, key)
    respond(blocks=blocks)


@app.action("select_pilih_prompt")
def select_pilih_prompt(ack, body, logger):
    ack()
    logger.info(body)


@app.action("select_key")
def radio_key(ack, body, logger):
    ack()
    logger.info(body)


@app.action("keyword_input_private")
def keyword_input(body, client, ack, say):
    ack()
    global promptSelectKey
    channel_id = body["channel"]["id"]
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    select_pilih_prompt = None
    if data:
        for key in data:
            if "select_pilih_prompt" in data[key]:
                select_pilih_prompt = data[key]["select_pilih_prompt"][
                    "selected_option"
                ]["value"]
                break
    prompt_value = select_pilih_prompt.split()
    promptByKey = readPromptByKey(prompt_value[0], " ".join(prompt_value[1:]))
    user_input = body["actions"][0]["value"]
    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
    reply = chatGPT(f"{promptByKey} {user_input}", channel_id)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(f"Prompt {promptByKey}{user_input}\nBalasan Assistant :checked:\n{reply}")


@app.action("keyword_input")
def keyword_input(body, client, ack, say):
    ack()
    global promptSelectKey
    channel_id = body["channel"]["id"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    print("channel_name: ", channel_name, flush=True)
    print("select prompt: ", data, flush=True)
    select_pilih_prompt = None
    if data:
        for key in data:
            if "select_pilih_prompt" in data[key]:
                select_pilih_prompt = data[key]["select_pilih_prompt"][
                    "selected_option"
                ]["value"]
                break
    promptByKey = readPromptByKey(channel_name, select_pilih_prompt)
    user_input = body["actions"][0]["value"]
    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
    reply = chatGPT(f"{promptByKey} {user_input}", channel_id)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(f"Prompt {promptByKey}{user_input}\nBalasan Assistant :checked:\n{reply}")


@app.action("action_add_prompt")
def action_add_prompt(body, client, ack, say):
    ack()
    channel_id = body["channel"]["id"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    prompt_key = None
    prompt_value = None
    if data:
        for key in data:
            if "prompt_key" in data[key]:
                prompt_key = data[key]["prompt_key"]["value"]
            if "prompt_value" in data[key]:
                prompt_value = data[key]["prompt_value"]["value"]
    response = writePrompt(prompt_key, prompt_value, channel_name)
    berhasil = f"Berhasil simpan prompt {channel_name.upper()} :checked:\nKey: `{prompt_key}`\nPrompt: `{prompt_value}`"
    gagal = f"Gagal simpan prompt {channel_name.upper()}"
    if response != None:
        say(berhasil)
    else:
        say(gagal)


@app.action("keyword_update_prompt")
def keyword_update_prompt(body, client, ack, say):
    ack()
    channel_id = body["channel"]["id"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    select_key = None
    prompt_key = None
    if data:
        for key in data:
            if "select_key" in data[key]:
                select_key = data[key]["select_key"]["selected_option"]["text"][
                    "text"
                ].lower()
            if "prompt_key" in data[key]:
                prompt_key = data[key]["prompt_key"]["value"]
    user_input = body["actions"][0]["value"]
    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
    response = updatePrompt(select_key, prompt_key.lower(), user_input, channel_name)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    berhasil = f"Berhasil update prompt {channel_name.upper()} :checked:\nKey: `{radio_key}`\nNew key: `{prompt_key}`\nPrompt: `{user_input}`"
    gagal = f"Gagal update prompt {channel_name.upper()}"
    if response != None:
        say(berhasil)
    else:
        say(gagal)


@app.action("action_delete_prompt")
def action_delete_prompt(body, client, ack, say):
    ack()
    channel_id = body["channel"]["id"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    data = (
        body["state"]["values"]
        if body and "state" in body and "values" in body["state"]
        else None
    )
    print("data =>", data)
    select_key = None
    select_value = None
    if data:
        for key in data:
            if "select_key" in data[key]:
                select_key = data[key]["select_key"]["selected_option"]["text"]["text"]
                select_value = data[key]["select_key"]["selected_option"]["value"]
    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
    response = deletePrompt(select_key.lower(), select_value, channel_name)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    berhasil = f"Berhasil delete prompt {channel_name.upper()} :checked:\nKey: `{radio_key}`\nPrompt: `{select_value}`"
    gagal = f"Gagal delete prompt {channel_name.upper()}"
    if response != None:
        say(berhasil)
    else:
        say(gagal)


# -----------------------------------


@app.action("download_image")
def download_image(ack, body):
    ack()


@app.event("message")
def direct_message(body, client, ack, event, say):
    ack()
    direct_message_to_bot(body, client, event, say, bot_token)


@app.event("app_mention")
def file_share(body, client, ack, event, say):
    ack()
    message_bot_with_mention(body, client, event, say, bot_token)


# from flask import Flask, request

# app_name = os.environ["NAME_APP"]
# flask_app = Flask(__name__)
# handler = SlackRequestHandler(app)


# @flask_app.route("/")
# def index():
#     return f"<h1>Ascending SlackGPT Bot for {app_name}</h1>"


# @flask_app.route(f"/slack/events", methods=["POST"])
# def slack_events():
#     return handler.handle(request)


if __name__ == "__main__":
    app.start(3000)
