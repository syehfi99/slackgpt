import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate("./cred-test-prompt.json")
firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

def save_user_reply(message, user_id):
    firestore_db.collection(u'history_chat').document(f"chat_{user_id}").set({'chat': message}, merge=True )

# def get_user_reply():
   

def readDB(prompt):
  doc_ref = firestore_db.collection('prompts')
  prompt_bank = doc_ref.document('prompt_bank')
  coll_prompt = prompt_bank.collection(f"{prompt}")
  data_prompt = coll_prompt.document(f"prompt_{prompt}")
  doc = data_prompt.get().to_dict()
  return doc
  # snapshots = firestore_db.collection('prompts').document('prompt_bank').collections()
  # for collection in snapshots:
  #   for doc in collection.stream():
  #       print(f'{doc.id} => {doc.to_dict()}')
    # return snapshot.to_dict()