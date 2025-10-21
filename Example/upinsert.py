from qdrant_client import QdrantClient,models
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

client = QdrantClient("http://222.255.214.30:6333")
model = SentenceTransformer('all-MiniLM-L6-v2') 
COLLECTION_NAME="docs"

vectors_config = models.VectorParams(size=384, distance=models.Distance.COSINE)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=vectors_config
)


def InsertData():
    # Convert text to vector
    texts = [
        "Con mèo nằm trên ghế.",
        "Con chó đang ngủ.",
        "Xe hơi màu đỏ.",
    ]
    vectors = model.encode(texts)

    points = [
        PointStruct(
            id=i,
            vector=vectors[i],
            payload={
                "text": texts[i],
                "category": "animal" if "Con" in texts[i] else "vehicle",
                "source": "demo_dataset",
                "created_at": "2025-10-18"
            }
        )
        for i in range(len(texts))
    ]
    try: 
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print("Upsert operation completed successfully.")
    except Exception as e:
        print(f"An error occurred during upsert: {e}")


if __name__ == "__main__":
    InsertData()