import os
import json
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import uuid
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "book_content"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

if not (QDRANT_URL and QDRANT_API_KEY):
    raise Exception("Missing QDRANT configs in .env")

# --- TEXT PROCESSING ---
def split_text(text, chunk_size=1000, overlap=200):
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# --- MAIN ---
if __name__ == "__main__":
    print(f"Loading local embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded.")

    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    try:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created/recreated.")
    except Exception as e:
        print(f"Could not recreate collection: {e}")
        
    with open("content.json", "r", encoding="utf-8") as f:
        docs = json.load(f)

    all_chunks = []
    for doc in docs:
        chunks = split_text(doc['text'])
        # Print the first chunk for verification
        if chunks:
            print(f"First chunk of {doc['path']}: {chunks[0][:100]}...")
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "path": doc['path']
            })

    print(f"Split {len(docs)} documents into {len(all_chunks)} chunks.")

    batch_size = 32
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        texts_to_embed = [item['text'] for item in batch]
        
        print(f"Embedding batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}...")
        embeddings = model.encode(texts_to_embed, convert_to_tensor=False).tolist()

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": item["text"], "path": item["path"]},
                )
                for item, embedding in zip(batch, embeddings)
            ],
            wait=True,
        )
        print(f"✅ Uploaded batch {i//batch_size + 1}")

    print("🎉 All embeddings uploaded successfully.")
