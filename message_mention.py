import requests
from db import delete_user_reply, readPromptByName
from block_kit_generator import (
    generateRadioPrompt,
    generateAddPromptByChannelName,
    generateUpdatePromptByKey,
    generateDeletePrompt,
    generateSelectPrompt,
    generateImageBlocks
)
import fitz
from chatgpt import chatGPT, generateImage
import openai
import pandas as pd
import os
import json, re


def channel_prompt(channel_name, say, client, channel_id, postMessage):
    prompts = readPromptByName(channel_name)
    blocks = generateSelectPrompt(prompts)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(blocks=blocks)


def channel_add_prompt(channel_name, say, client, channel_id, postMessage):
    blocks = generateAddPromptByChannelName(channel_name)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(blocks=blocks)


def channel_update_prompt(channel_name, say, client, channel_id, postMessage):
    prompts = readPromptByName(channel_name)
    blocks = generateUpdatePromptByKey(prompts, channel_name)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(blocks=blocks)


def channel_delete_prompt(channel_name, say, client, channel_id, postMessage):
    prompts = readPromptByName(channel_name)
    blocks = generateDeletePrompt(prompts, channel_name)
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(blocks=blocks)


def channel_prompt_info(channel_name, say, client, channel_id, postMessage):
    prompts = readPromptByName(channel_name)
    prompt_list = []
    index = 1
    for data in prompts["prompts"]:
        prompt_list.append(f"{str(index)}. `{data['key']}`\n```{data['prompt']}```\n\n")
        index = index + 1

    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    say(f"Informasi prompt {channel_name.upper()}\n\n{''.join(prompt_list)}")


def channel_prompt_help(channel_name, say, client, channel_id, postMessage):
    client.chat_delete(channel=channel_id, ts=postMessage["ts"])
    info_text = f"1. `@[nama_bot] [keyword]`, prompt langsung slack gpt\n2. `@[nama_bot] prompt`, menampilkan prompting template channel `{channel_name.upper()}`\n3. `@[nama_bot] prompt info`, menampilkan detail prompt template dari channel `{channel_name.upper()}`\n"
    say(f"Bantuan Slack GPT Divisi {channel_name.upper()}\n\n{info_text}")


def message_bot_with_mention(body, client, event, say, bot_token):
    channel_id = event["channel"]
    user_id = body["event"]["user"]
    try:
        file_url = body["event"]["files"][0]["url_private_download"]
    except (KeyError, IndexError):
        file_url = None
    try:
        url_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][2][
            "url"
        ]
    except (KeyError, IndexError):
        url_from_mention = None
    try:
        text_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][1][
            "text"
        ]
    except (KeyError, IndexError):
        text_from_mention = None

    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
    print("text_from_mention", text_from_mention, flush=True)
    headers = {"Authorization": f"Bearer {bot_token}"}

    if file_url != None:
        r = requests.get(file_url, stream=True, headers=headers)
        file_url = body["event"]["files"][0]["url_private_download"]
        filename = os.path.basename(file_url)
        file_extension = os.path.splitext(filename)[1]
        if file_extension == ".pdf":
            delete_user_reply(channel_id)
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
            with open(f"train_data_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
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
                channel=channel_id,
                ts=postMessage["ts"],
                text=f"Data sudah dipelajari: {reply}",
            )
        elif file_extension == ".mp4":
            with open(f"audio_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
            audio_file = open(f"audio_{user_id}{file_extension}", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            reply = chatGPT(f"{transcript['text']}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")

    if url_from_mention != None:
        reply = chatGPT(f"{text_from_mention} {url_from_mention}", channel_id)
        client.chat_delete(channel=channel_id, ts=postMessage["ts"])
        say(f"{reply}")

    # -----------------------------------

    if text_from_mention == " prompt":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_prompt(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    if text_from_mention == " prompt add":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_add_prompt(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    if text_from_mention == " prompt update":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_update_prompt(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    if text_from_mention == " prompt delete":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_delete_prompt(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    if text_from_mention == " prompt info":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_prompt_info(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    if text_from_mention == " help":
        channel_name = client.conversations_info(channel=channel_id)
        print("channel_name", channel_name, flush=True)
        channel_prompt_help(
            channel_name=channel_name["channel"]["name"],
            say=say,
            client=client,
            channel_id=channel_id,
            postMessage=postMessage,
        )

    # -----------------------------------

    if text_from_mention != " prompt":
        split_text = text_from_mention.split()
        if split_text[0] == "generate":
            # Menggabungkan kata-kata setelah "generate" menjadi kalimat baru
            kalimat_baru = " ".join(split_text[1:])
            generate_image = generateImage(kalimat_baru)
            print(kalimat_baru)
            blocks = generateImageBlocks(
                image_url=generate_image, text=kalimat_baru
            )
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            client.chat_postMessage(
                channel=channel_id, text="Generate Selesai :checked:"
            )
            say(blocks=blocks)
        else:
            reply = chatGPT(f"{text_from_mention}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")
