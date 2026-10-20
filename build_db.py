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

# 샘플로 테스트 잠깐
# sample = data[:50]

# texts = [d["text"] for d in sample]
# metadatas = [d["metadata"] for d in sample]
# ids = [d["id"] for d in sample]

# vectorstore.add_texts(
#     texts = texts,
#     metadatas = metadatas,
#     ids = ids
# )

BATCH = 100

for i in range(0, len(data), BATCH):
    batch = data[i:i + BATCH]                   # data[0:100] 부터 시작
    vectorstore.add_texts(
        texts = [d["text"] for d in batch],
        metadatas = [d["metadata"] for d in batch],
        ids = [d["id"] for d in batch]
    )

print(f"DB 저장 완료 ! 저장 건수 -> {vectorstore._collection.count()}")

results = vectorstore.similarity_search("나이는 30대초반이고 취업준비생이에요.", k=3)

for doc in results:
    print(doc.metadata['plcy_name'])


