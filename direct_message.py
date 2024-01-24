import requests
from db import delete_user_reply
import fitz
from chatgpt import chatGPT, generateImage, fine_tune, search_reviews, get_embed_dataset, embeddings_text, from_chromadb
import openai
import pandas as pd
import os
from block_kit_generator import generateImageBlocks
import json
import numpy as np
from ast import literal_eval
from time import sleep


def direct_message_to_bot(body, client, event, say, bot_token):
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
        text_from_mention = body["event"]["blocks"][0]["elements"][0]["elements"][0][
            "text"
        ]
    except (KeyError, IndexError):
        text_from_mention = None

    postMessage = client.chat_postMessage(
        channel=channel_id, text="Tunggu sebentar ya :loading:"
    )
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
            # delete_user_reply(channel_id)
            with open(f"train_data_{user_id}{file_extension}", "wb") as file:
                file.write(r.content)
            df = pd.read_csv(
                f"train_data_{user_id}{file_extension}",
                # header=None,
                # index_col=False,
                # delimiter=",",
                # skipinitialspace=True,
            )
            fine_tune(say, channel_id, df=df)
            # reply = chatGPT(f"{text_from_mention} {df.to_string()}", channel_id)
            # client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            # say(f"{reply}")

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

    else:
        # Direct with ChatGPT
        if url_from_mention != None:
            reply = chatGPT(f"{text_from_mention} {url_from_mention}", channel_id)
            client.chat_delete(channel=channel_id, ts=postMessage["ts"])
            say(f"{reply}")

        if text_from_mention != None:
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
                # get_embed_dataset(say)
                # say('sleep 10s')
                # sleep(10)
                # datafile_path = "data/fine_food_reviews_with_embeddings_1k.csv"

                # df = pd.read_csv(datafile_path)
                # df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)
                # results = search_reviews(df, "delicious beans", say, n=3)
                # say(f"{results}")
                # get_embeddings()
                # delete_fine_tune("ft:gpt-3.5-turbo-0613:arkademi-tech:ft-arkademi-gpt-01:8T5Lk9Vj")
                reply = chatGPT(f"{text_from_mention}", channel_id)
                client.chat_delete(channel=channel_id, ts=postMessage["ts"])
                # say(f"{reply}")
                embeddings_text(text=f"{text_from_mention}", message=f"{reply}")
                embed = from_chromadb(f"{text_from_mention}")
                say(f"{embed}")
