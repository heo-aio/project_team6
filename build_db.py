import json

import chromadb

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embed_fn = OllamaEmbeddings(base_url="http://localhost:11434", model="bge-m3:latest")
client = chromadb.PersistentClient(path="./store")
vectorstore = Chroma(client=client, collection_name="policies_data", embedding_function=embed_fn)

with open("policies_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# print(type(data[0]["text"]))

sample = data[:50]

texts = [d["text"] for d in sample]
metadatas = [d["metadata"] for d in sample]
ids = [d["id"] for d in sample]

vectorstore.add_texts(
    texts = texts,
    metadatas = metadatas,
    ids = ids
)

# print(vectorstore._collection.count())
print(vectorstore.similarity_search("창업 지원", k=3))

