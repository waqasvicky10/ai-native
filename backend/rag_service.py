import os
from typing import Tuple, List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import AsyncOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob
import asyncio

class RagService:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_key = os.getenv("QDRANT_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.collection_name = "book_collection"
        
        if not self.openai_key:
            print("Warning: OPENAI_API_KEY not set")
        
        self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_key)
        self.openai_client = AsyncOpenAI(api_key=self.openai_key)
        self.embedding_model = "text-embedding-3-small"

    def ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

    async def get_embedding(self, text: str) -> List[float]:
        response = await self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    async def chat_with_context(self, query: str, context: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant answering questions about the selected text from a book."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content

    async def chat_rag(self, query: str) -> Tuple[str, List[str]]:
        query_vector = await self.get_embedding(query)
        
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=3
        ).points
        
        context_parts = [hit.payload["content"] for hit in search_result]
        sources = [hit.payload["source"] for hit in search_result]
        
        context_str = "\n\n".join(context_parts)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant answering questions about a book based on the retrieved context."},
            {"role": "user", "content": f"Context: {context_str}\n\nQuestion: {query}"}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return response.choices[0].message.content, list(set(sources))

    async def ingest_docs(self, docs_path: str) -> int:
        files = glob.glob(f"{docs_path}/**/*.md", recursive=True)
        total_chunks = 0
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        points = []
        point_id = 0
        
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                
            chunks = text_splitter.split_text(content)
            
            for chunk in chunks:
                embedding = await self.get_embedding(chunk)
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"content": chunk, "source": os.path.basename(file)}
                ))
                point_id += 1
                total_chunks += 1
                
        # Batch upload
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
        return total_chunks
