import os
import uvicorn
import traceback
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from fastapi.concurrency import run_in_threadpool
import google.generativeai as genai

# --- CONFIGURATION ---
load_dotenv()
if not all(key in os.environ for key in ["QDRANT_URL", "QDRANT_API_KEY", "GEMINI_API_KEY"]):
    raise Exception("Missing required environment variables: QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- MODELS & GLOBALS ---
class QueryRequest(BaseModel):
    query: str
class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

embedding_model = None
qdrant_client = None
generative_model = None
COLLECTION_NAME = "book_content"
PROMPT_TEMPLATE = """
You are a helpful AI assistant who is an expert in the content of a book.
A user has a question, and you have retrieved the most relevant sections from the book to help answer it.
Use the provided context to answer the user's question.

CONTEXT:
---
{context}
---

QUESTION:
{question}

YOUR ANSWER:
"""

# --- APPLICATION LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model, qdrant_client, generative_model
    print("--- Server Starting Up ---")
    try:
        qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
        
        model_name = "all-MiniLM-L6-v2"
        print(f"Loading local embedding model: {model_name}...")
        embedding_model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

        print("Loading generative model...")
        generative_model = genai.GenerativeModel('gemini-1.5-flash')
        print("Generative model loaded successfully.")
        
    except Exception as e:
        print("---!!! FATAL ERROR DURING STARTUP !!!---")
        print(f"Could not initialize models or clients: {e}")
        raise e
        
    yield
    
    print("--- Server Shutting Down ---")
    embedding_model = None
    qdrant_client = None
    generative_model = None

# --- FASTAPI APP ---
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- API ENDPOINTS ---
@app.get("/ping")
def ping():
    return {"message": "RAG Backend Running!"}

@app.post("/query")
async def query_book(request: QueryRequest):
    if not all([embedding_model, qdrant_client, generative_model]):
        return JSONResponse(status_code=503, content={"answer": "Server is not ready, models are not loaded.", "sources": []})
    try:
        query_embedding = await run_in_threadpool(embedding_model.encode, request.query)
        
        search_results = await run_in_threadpool(
            qdrant_client.search,
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=3,
        )

        if not search_results:
            return QueryResponse(answer="I'm sorry, but I couldn't find any relevant information in the book for your question.", sources=[])

        context = ""
        sources = set()
        for i, result in enumerate(search_results):
            context += f"Section {i+1}:\n\"{result.payload['text']}\"\n\n"
            sources.add(result.payload['path'])

        prompt = PROMPT_TEMPLATE.format(context=context, question=request.query)
        
        # Use async generation
        response = await generative_model.generate_content_async(prompt)

        return QueryResponse(answer=response.text, sources=list(sources))

    except Exception as e:
        print(f"\n--- ERROR IN /query ENDPOINT ---")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"answer": f"An unknown server error occurred: {e}", "sources": []})

# --- MAIN ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
