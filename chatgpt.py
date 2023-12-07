from time import sleep
import openai
import os
from db import save_user_reply, get_user_reply, delete_user_reply
from dotenv import load_dotenv
import tiktoken
import json  
import pandas as pd  

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
                model="ft:gpt-3.5-turbo-0613:arkademi-tech:ft-arkademi-gpt-01:8ShooCuk", messages=chat_db, temperature=0.3
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

def fine_tune(say):
    # df = pd.read_csv("dataset.csv")  
    # with open("train_data.jsonl", "w") as f:  
    #     for i, row in list(df.iterrows()):
    #         question = row["question"]  
    #         answer = row["answer"]  
    #         example = get_example(question, answer)  
    #         example_str = json.dumps(example)  
    #         f.write(example_str + "\n")
    # sleep(5) #Generate jsonl file
    # response = openai.File.create(file=open("train_data.jsonl", "rb"), purpose="fine-tune")
    # uploaded_id = response.id
    # print("uploaded_id",response.id, flush=True)
    # say("Dataset is uploaded")
    # say("Wait a minute...")
    # print("Sleep 30 seconds...", flush=True)
    # sleep(30)  # wait until dataset would be prepared
    
    # response_jobs = openai.FineTuningJob.create(training_file=uploaded_id,model="gpt-3.5-turbo",suffix="ft:arkademi-gpt:01")
    # # print("Fine-tune job is started", flush=True)
    # say("Fine-tune job is started")
    # print("response_jobs",response_jobs, flush=True)
    resp = openai.FineTuningJob.retrieve("ftjob-GYyucXjsAm9AnaKrCVWPyIyn")
    say(f"{resp}")
    # chat = openai.ChatCompletion.create(
    # model="ft:gpt-3.5-turbo-0613:arkademi-tech:ft-arkademi-gpt-01:8Sh7r1oB",
    # messages=[
    #     {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
    #     {"role": "user", "content": "What is supervised learning?"}
    # ]
    # )
    # say(f"{chat.choices[0].message.content}")

# def wait_untill_done(job_id): 
#     events = {}
#     while True: 
#         response = openai.FineTuningJob.list_events(id=job_id, limit=10)
#         # collect all events
#         for event in response["data"]:
#             if "data" in event and event["data"]:
#                 events[event["data"]["step"]] = event["data"]["train_loss"]
#         messages = [it["message"] for it in response.data]
#         for m in messages:
#             if m.startswith("New fine-tuned model created: "):
#                 return m.split("created: ")[1], events
#         sleep(10)
#         response = openai.File.create(file=open("train.jsonl", "rb"), purpose="fine-tune")
#         uploaded_id = response.id
#         print("Dataset is uploaded")
#         print("Sleep 30 seconds...")
#         sleep(30)  # wait until dataset would be prepared
#         response = openai.FineTuningJob.create(training_file=uploaded_id,model=params["model"],hypeparameters={"n_epochs": 10})
#         print("Fine-tune job is started")
#         ft_job_id = response.id
#         new_model_name, events = wait_untill_done(ft_job_id)
#         with open("result/new_model_name.txt", "w") as fp:
#             fp.write(new_model_name)
#         print(new_model_name)

# def get_fine_tuned_model_name(): 
#     with open("result/new_model_name.txt") as fp:
#         return fp.read()