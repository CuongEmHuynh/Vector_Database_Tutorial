import numpy as np
import pyodbc
import pandas as pd
from qdrant_client import QdrantClient,models
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import re, unicodedata

SERVERDB="192.168.6.54"
USERNAME="sa"
PASSWORD="p@ssw0rd789"
SERVERQDRANT="http://222.255.214.30:6333"
COLLECTION_NAME="advising_docs"
MODEL_EMBEDDING="keepitreal/vietnamese-sbert"


replacements = {
    "SV": "Sinh viên",
    "PH": "Phụ huynh",
    "CVHT": "Cố vấn học tập",
    "AV": "Anh văn",
    "TA": "Tiếng Anh",
    "DKMH": "Đăng ký môn học",
}

# sql_client.py
import pyodbc

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVERDB};"
        f"DATABASE=CoVan;"
        f"UID={USERNAME};PWD={PASSWORD}"
    )
    return conn

def  fetch_data(connection):
    df = pd.read_sql(''' SELECT TOP 1000 s.Id,FirstName, LastName , StudentCode, Email, SN.Notes, SN.CreateDate as N'Ngày tạo ghi chú' From Students S
LEFT JOIN StudentNotes SN ON  S.Id = SN.StudentId
order by SN.CreateDate desc ''', connection)
    return df


def creat_collection(client):

    vectors_config = models.VectorParams(size=768, distance=models.Distance.COSINE)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=vectors_config
    )


def search_vector(client, model, query, top_k=5):
    query_vector = model.encode([query])[0]

    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return search_result    


def normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản tiếng Việt: bỏ ký tự lỗi, viết tắt, khoảng trắng"""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\sÀ-ỹ.,;:!?()/-]", "", text)
    text = text.strip()
    for abbr, full in replacements.items():
        text = re.sub(rf"\b{abbr}\b", full, text)
    return text

if __name__ == "__main__":
    # Test the database connection
    try:
        
        connection = get_connection()

        data = fetch_data(connection)

        # model, client = creat_collection()
        client = QdrantClient(SERVERQDRANT)
        model = SentenceTransformer('keepitreal/vietnamese-sbert') 
        # creat_collection(client)

        # # Clean data from SQL Server      
        # # texts = data["Notes"].fillna("").astype(str)
        # data = data.dropna(subset=["Notes"]).copy()
        # data["Notes"] = data["Notes"].astype(str)
        # # Áp dụng clean
        # data["CleanNotes"] = data["Notes"].apply(normalize_text)
        # # data = data[data["CleanNotes"].str.len() > 20]
        # data = data.drop_duplicates(subset=["CleanNotes"]).reset_index(drop=True)
        # print(f"✅ Dữ liệu sau khi clean: {len(data)} ghi chú hợp lệ")


        # texts = data["CleanNotes"].tolist()

        # vectors = model.encode(texts, batch_size=64, show_progress_bar=True)
        # points = []
        # for i, row in data.iterrows():
        #     point = PointStruct(
        #         id=int(row["Id"]),
        #         vector=vectors[i],
        #         payload={
        #             "student_code": str(row["StudentCode"]),
        #             "text": row["Notes"],
        #             "source": "CoVanDB",
        #             "created_at": str(row["Ngày tạo ghi chú"])
        #         }
        #     )
        #     points.append(point)

        # BATCH_SIZE = 500
        # for i in range(0, len(points), BATCH_SIZE):
        #     batch = points[i:i+BATCH_SIZE]
        #     try:
        #         client.upsert(collection_name=COLLECTION_NAME, points=batch)
        #         print(f"✅ Upserted batch {i//BATCH_SIZE + 1} ({len(batch)} records)")
        #     except Exception as e:
        #         print(f"⚠️ Error at batch {i//BATCH_SIZE + 1}: {e}")

        # insert data to qdrant
        result =  search_vector(client,model,"Tư vấn lộ trình học tập cho sinh viên")
        print("Search Results:")
        for hit in result:
            print(f"ID: {hit.id}, Score: {hit.score}, Payload: {hit.payload}")

        # print(data.head()) 
        print("Connection successful!")
        # connection.close()
    except Exception as e:
        print(f"Connection failed: {e}")