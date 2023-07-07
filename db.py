import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate("./cred-test-prompt.json")
firebase_admin.initialize_app(cred)

firestore_db = firestore.client()


def save_user_reply(message, user_id):
    message_history = [
        {"role": "system", "content": "You are a intelligent assistant."}
    ]
    new_message = [*message_history, message]
    firestore_db.collection("history_chat").document(f"chat_{user_id}").set(
        {"chat": firestore.ArrayUnion(new_message)}, merge=True
    )


def delete_user_reply(user_id):
    firestore_db.collection("history_chat").document(f"chat_{user_id}").delete()


def get_user_reply(user_id):
    doc_ref = firestore_db.collection("history_chat")
    doc_chat = doc_ref.document(f"chat_{user_id}")
    doc = doc_chat.get().to_dict()
    return doc


def readDB(prompt):
    doc_ref = firestore_db.collection("prompts")
    prompt_bank = doc_ref.document("prompt_bank")
    coll_prompt = prompt_bank.collection(f"{prompt}")
    data_prompt = coll_prompt.document(f"prompt_{prompt}")
    doc = data_prompt.get().to_dict()
    return doc
    # snapshots = firestore_db.collection('prompts').document('prompt_bank').collections()
    # for collection in snapshots:
    #   for doc in collection.stream():
    #       print(f'{doc.id} => {doc.to_dict()}')
    # return snapshot.to_dict()


def readBankCollection():
    data_array = []  # Array untuk menyimpan data
    doc_ref = firestore_db.collection("prompts").stream()
    for doc in doc_ref:
        data_array.append({doc.id: doc.to_dict()})
    return data_array
    # doc_ref = firestore_db.collection("prompts")
    # prompt_bank = doc_ref.document("prompt_bank")
    # prompt_banks = prompt_bank.collections()

    # data_array = []  # Array untuk menyimpan data

    # for collection in prompt_banks:
    #     for doc in collection.stream():
    #         data_array.append({doc.id: doc.to_dict()})

    # return data_array


# prompting db
def readPromptCollection():
    doc_ref = firestore_db.collection("prompts")
    prompt_bank = doc_ref.document("prompts")
    doc = prompt_bank.get().to_dict()
    print("banks", doc, flush=True)
    return doc


def readPromptByName(prompt):
    doc_ref = firestore_db.collection("prompts")
    prompt_bank = doc_ref.document(f"prompt_{prompt}")
    doc = prompt_bank.get().to_dict()
    print("banks by name", doc, flush=True)
    return doc
