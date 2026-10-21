import json
import time

from vector_store import get_vectorstore


def build():
    with open("policies_clean.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    vectorstore = get_vectorstore()

    BATCH = 100
    start = time.time()

    for i in range(0, len(data), BATCH):
        batch = data[i:i + BATCH]                      # data[0:100]부터 시작
        vectorstore.add_texts(
            texts=[d["text"] for d in batch],
            metadatas=[d["metadata"] for d in batch],
            ids=[d["id"] for d in batch],
        )
        print(f"{min(i + BATCH, len(data))}/{len(data)}  ({time.time() - start:.0f}초)")

    print(f"DB 저장 완료 ! 저장 건수 -> {vectorstore._collection.count()}")


if __name__ == "__main__":
    build()