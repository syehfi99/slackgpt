from time import sleep
import openai
import os
from db import save_user_reply, get_user_reply, delete_user_reply, save_ft_model, get_ft_model
from dotenv import load_dotenv
import tiktoken
import json  
import pandas as pd  
from openai.embeddings_utils import get_embedding, cosine_similarity
from sklearn.decomposition import PCA
# from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.decomposition import PCA
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import uuid



load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
collections = os.environ["COLLECTION"]
chroma_client = chromadb.PersistentClient(path="./data/chromadb")
# chroma_client = chromadb.Client()
# messages = []
# message_history = [{"role": "system", "content": "You are a intelligent assistant."}]
embeddings_temp=[]


def chatGPT(message, user_id):
    if message:
        # message_history.append(
        #     {"role": "user", "content": message},
        # )
        # ft_model = get_ft_model(user_id)
        save_user_reply({"role": "user", "content": message}, user_id)
        chat_db = get_user_reply(user_id)
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")
        num_token = 0
        for message in chat_db:
            for key, value in message.items():
                num_token += len(encoding.encode(value))
        print("num_tokens", num_token, flush=True)
        if num_token < 4096:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613", messages=chat_db, temperature=0
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

def get_example(question, answer):
    return {  
        "messages": [  
            {"role": "user", "content": question},  
            {"role": "assistant", "content": answer},  
        ]  
    } 

def fine_tune(say, id, df):
    # df = pd.read_csv("dataset.csv")  
    with open(f"train_data_{id}.jsonl", "w") as f:  
        for i, row in list(df.iterrows()):
            question = row["question"]  
            answer = row["answer"]  
            example = get_example(question, answer)  
            example_str = json.dumps(example)  
            f.write(example_str + "\n")
    sleep(5) #Generate jsonl file
    response = openai.File.create(file=open(f"train_data_{id}.jsonl", "rb"), purpose="fine-tune")
    uploaded_id = response.id
    print("uploaded_id",response.id, flush=True)
    say("Created fine-tuning job")
    say("Validating training file")
    print("Sleep 30 seconds...", flush=True)
    sleep(30)  # wait until dataset would be prepared
    say("Files validated, moving job to queued state")
    
    response_jobs = openai.FineTuningJob.create(training_file=uploaded_id,model="gpt-3.5-turbo-0613",suffix="ft:arkademi-gpt:01")
    # print("Fine-tune job is started", flush=True)
    say("Fine-tuning job started")
    print("response_jobs",response_jobs, flush=True)
    # resp = openai.FineTuningJob.retrieve(response_jobs.id)
    say('Wait...')
    while True:
        resp = openai.FineTuningJob.retrieve(response_jobs.id)
        fine_tuned_model = resp["fine_tuned_model"]
        error = resp["error"]

        if fine_tuned_model is not None or error is not None:
            # with open("data_model.txt", "w") as f:  
            #     f.write(fine_tuned_model)
            save_ft_model(fine_tuned_model, id)
            say('The job has successfully completed')
            break
        print('on proggres')
        sleep(30)

def delete_fine_tune(ft_id):
    openai.Model.delete(ft_id)

def embeddings_text(message):
    input_embeding = openai.Embedding.create(
        input=message,
        model="text-embedding-ada-002"
    )
    embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
    collection = chroma_client.get_or_create_collection(name=f"{collections}", embedding_function=embedding_function)
    collection.add(
        documents=[message],
        embeddings=[input_embeding.data[0].embedding],
        ids=[str(uuid.uuid4())]
    )

def from_chromadb(text):
    split_text = text.split()
    embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
    collection = chroma_client.get_collection(name=f"{collections}", embedding_function=embedding_function)
    results = collection.query(
        query_texts=[text],
        where_document={"$contains": text},
        n_results=5
    )
    documents = results["documents"][0]
    # print(documents, flush=True)
    if not documents:
        return None
    else:
        return documents[0]

def get_embeddings():
    input_embeding = openai.Embedding.create(
        input="server",
        model="text-embedding-ada-002"
    )
    similarities = cosine_similarity(input_embeding.data[0].embedding.reshape(1, -1), embeddings_temp)
    # Find the index of the text with the highest similarity
    most_similar_index = similarities.argmax()

    # Print the most similar text
    print(most_similar_index, flush=True)

def get_embed_dataset(say):
    embedding_model = "text-embedding-ada-002"
    embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
    max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
    # load & inspect dataset
    input_datapath = "data/Reviews.csv"  # to save space, we provide a pre-filtered dataset
    df = pd.read_csv(input_datapath, index_col=0)
    df = df[["Time", "ProductId", "UserId", "Score", "Summary", "Text"]]
    df = df.dropna()
    df["combined"] = (
        "Title: " + df.Summary.str.strip() + "; Content: " + df.Text.str.strip()
    )
    df.head(2)
    # subsample to 1k most recent reviews and remove samples that are too long
    top_n = 1000
    df = df.sort_values("Time").tail(top_n * 2)  # first cut to first 2k entries, assuming less than half will be filtered out
    df.drop("Time", axis=1, inplace=True)
    encoding = tiktoken.get_encoding(embedding_encoding)
    df["n_tokens"] = df.combined.apply(lambda x: len(encoding.encode(x)))
    df = df[df.n_tokens <= max_tokens].tail(top_n)
    say(f"{len(df)}")
    df["embedding"] = df.combined.apply(lambda x: get_embedding(x, engine=embedding_model))
    df.to_csv("data/fine_food_reviews_with_embeddings_1k.csv")
    say("Embedding is done")

def search_reviews(df, product_description,say, n=3, pprint=True):
    product_embedding = get_embedding(
        product_description,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))
    results = (
    df.sort_values("similarity", ascending=False)
        .head(n)
        .str.replace("Title: ", "")
        .str.replace("; Content:", ":")
    )
    print(results, flush=True)
    return results

