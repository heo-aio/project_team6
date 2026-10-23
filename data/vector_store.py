import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def get_vectorstore():
    embed_fn = OllamaEmbeddings(base_url="http://localhost:11434", model="bge-m3:latest")
    client = chromadb.PersistentClient(path="./store")
    return Chroma(client=client, collection_name="policies_data", embedding_function=embed_fn)