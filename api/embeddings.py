import openai
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import uuid
from PyPDF2 import PdfReader
import io

from api.reformat_text import reformat_text
from api.split_text_8000 import split_text_8000


load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
chroma_client = chromadb.PersistentClient(path="./data/chromadb")
# chroma_client = chromadb.Client()



def embeddings_text_api(files, collection):
    pdf_reader = PdfReader(io.BytesIO(files))
    text = ""

    for index, pdf_page in enumerate(pdf_reader.pages):
        text += pdf_page.extract_text()

    split_texts = split_text_8000(text, 8000)
    format_text = ""
    for split_text in split_texts:
        format_text += reformat_text(split_text)

    input_embeding = openai.Embedding.create(
        input=format_text,
        model="text-embedding-ada-002"
    )
    embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
    collection = chroma_client.get_or_create_collection(name=f"{collection}", embedding_function=embedding_function)
    collection.add(
        documents=split_texts,
        embeddings=[input_embeding.data[0].embedding] * len(split_texts),
        ids=[str(uuid.uuid4())] * len(split_texts)
    )

    return format_text