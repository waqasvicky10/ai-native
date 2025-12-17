from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from rag_service import RagService
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RagService()

class ChatRequest(BaseModel):
    query: str
    context: Optional[str] = None  # Text selected by user, if any

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

@app.on_event("startup")
async def startup_event():
    # Ensure collection exists
    rag_service.ensure_collection()

@app.get("/")
async def root():
    return {"message": "Physical AI Book Backend is running"}

@app.get("/favicon.ico", include_in_schema=False)
@app.head("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=None, status_code=204)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if request.context:
            # If user selected text, prioritize that context
            answer = await rag_service.chat_with_context(request.query, request.context)
            return ChatResponse(answer=answer, sources=["User Selection"])
        else:
            # Standard RAG
            answer, sources = await rag_service.chat_rag(request.query)
            return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest():
    """Trigger ingestion of docs (simplified for demo)."""
    try:
        count = await rag_service.ingest_docs("../docs")
        return {"message": f"Ingested {count} documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
