import openai
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import uuid
from PyPDF2 import PdfReader
import io
import tiktoken
from pdfminer.high_level import extract_text, extract_pages

from api.reformat_text import reformat_text
from api.split_text_8000 import split_text_8000


load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
chroma_client = chromadb.PersistentClient(path="./data/chromadb")
# chroma_client = chromadb.Client()



def embeddings_text_api(files, collection):
    embedding_encoding = "cl100k_base"
    # pdf_reader = PdfReader(io.BytesIO(files))
    pdf_reader = extract_text(io.BytesIO(files))
    # text = ""
    # print(pdf_reader, flush=True)

    # for index, pdf_page in enumerate(pdf_reader.pages):
    #     text += pdf_page.extract_text()

    split_texts = split_text_8000(pdf_reader, 8000, embedding_encoding)
    embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
    collection = chroma_client.get_or_create_collection(name=f"{collection}", embedding_function=embedding_function)
    collection.add(
        documents=split_texts,
        # embeddings=[input_embeding.data[0].embedding],
        ids=[str(uuid.uuid4()) for _ in split_texts]
    )

    return split_texts