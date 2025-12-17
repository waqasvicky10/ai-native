# RAG (Retrieval-Augmented Generation) API router
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from ..database import get_db
from ..vector_db import vector_db
from ..ai_client import ai_client
from ..schemas import (
    ChatRequest, ChatResponse, ContentIndexRequest, ContentIndexResponse,
    ContentSearchRequest, ContentSearchResponse, BaseResponse
)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_rag(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with RAG-enabled AI assistant.
    
    Processes user queries by:
    1. Generating embedding for the query
    2. Searching for relevant content in vector database
    3. Generating contextual response using AI
    """
    start_time = datetime.utcnow()
    
    try:
        # Generate embedding for the user query
        query_embedding = await ai_client.generate_embedding(request.message)
        
        # Search for relevant content
        filter_conditions = {}
        if request.chapter_id:
            filter_conditions["chapter_id"] = request.chapter_id
        
        search_results = await vector_db.search_similar(
            query_embedding=query_embedding,
            limit=5,
            score_threshold=0.7,
            filter_conditions=filter_conditions
        )
        
        # Prepare context from search results
        context_chunks = []
        sources = []
        
        for result in search_results:
            context_chunks.append(result["content"])
            sources.append({
                "id": result["id"],
                "score": result["score"],
                "chapter_id": result.get("chapter_id", ""),
                "section": result.get("section", ""),
                "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            })
        
        # Build context for AI
        context = "\n\n".join(context_chunks) if context_chunks else ""
        
        # Prepare messages for AI
        system_prompt = f"""You are an AI tutor for a Physical AI & Humanoid Robotics textbook. 
        Answer the user's question based on the provided context from the textbook.
        
        Guidelines:
        - Use the context to provide accurate, relevant answers
        - If the context doesn't contain enough information, say so clearly
        - Maintain an educational and helpful tone
        - Provide practical examples when appropriate
        - Reference specific concepts from the textbook when relevant
        
        Context from textbook:
        {context}
        """
        
        messages = []
        
        # Add conversation history
        for msg in request.conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Generate AI response
        ai_response = await ai_client.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Calculate confidence based on search results
        confidence = 0.9 if search_results else 0.3
        if search_results:
            avg_score = sum(r["score"] for r in search_results) / len(search_results)
            confidence = min(0.95, avg_score * 1.1)
        
        # Generate suggested follow-ups
        suggested_followups = []
        if search_results:
            # Extract topics from search results for follow-up suggestions
            topics = set()
            for result in search_results:
                if "metadata" in result and "tags" in result["metadata"]:
                    topics.update(result["metadata"]["tags"][:2])
            
            suggested_followups = [
                f"Can you explain more about {topic}?" 
                for topic in list(topics)[:3]
            ]
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ChatResponse(
            message=ai_response["content"],
            confidence=confidence,
            sources=sources,
            suggested_followups=suggested_followups,
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"Error in RAG chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/index-content", response_model=ContentIndexResponse)
async def index_content(
    request: ContentIndexRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Index content documents into the vector database.
    
    Processes documents by:
    1. Generating embeddings for each document
    2. Storing in vector database with metadata
    3. Returning indexing results
    """
    start_time = datetime.utcnow()
    
    try:
        document_ids = []
        
        # Process documents in batches for efficiency
        batch_size = 10
        for i in range(0, len(request.documents), batch_size):
            batch = request.documents[i:i + batch_size]
            
            # Extract content for embedding generation
            contents = [doc.content for doc in batch]
            
            # Generate embeddings in batch
            embeddings = await ai_client.generate_embeddings_batch(contents)
            
            # Store each document with its embedding
            for doc, embedding in zip(batch, embeddings):
                doc_id = await vector_db.add_document(
                    content=doc.content,
                    embedding=embedding,
                    metadata={
                        "chapter_id": doc.metadata.chapter_id,
                        "section": doc.metadata.section,
                        "content_type": doc.metadata.content_type.value,
                        "difficulty": doc.metadata.difficulty.value,
                        "tags": doc.metadata.tags,
                        "estimated_reading_time": doc.metadata.estimated_reading_time,
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                )
                document_ids.append(doc_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ContentIndexResponse(
            indexed_count=len(document_ids),
            document_ids=document_ids,
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"Error indexing content: {e}")
        raise HTTPException(status_code=500, detail=f"Content indexing failed: {str(e)}")

@router.post("/search", response_model=ContentSearchResponse)
async def search_content(
    request: ContentSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for content in the vector database.
    
    Performs semantic search based on query embedding.
    """
    start_time = datetime.utcnow()
    
    try:
        # Generate embedding for search query
        query_embedding = await ai_client.generate_embedding(request.query)
        
        # Build filter conditions
        filter_conditions = {}
        if request.chapter_id:
            filter_conditions["chapter_id"] = request.chapter_id
        if request.content_type:
            filter_conditions["content_type"] = request.content_type.value
        if request.difficulty:
            filter_conditions["difficulty"] = request.difficulty.value
        
        # Search vector database
        search_results = await vector_db.search_similar(
            query_embedding=query_embedding,
            limit=request.limit,
            score_threshold=request.score_threshold,
            filter_conditions=filter_conditions
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ContentSearchResponse(
            results=search_results,
            query=request.query,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"Error searching content: {e}")
        raise HTTPException(status_code=500, detail=f"Content search failed: {str(e)}")

@router.delete("/content/{doc_id}")
async def delete_content(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document from the vector database."""
    try:
        success = await vector_db.delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return BaseResponse(message=f"Document {doc_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting content: {e}")
        raise HTTPException(status_code=500, detail=f"Content deletion failed: {str(e)}")

@router.get("/collection-info")
async def get_collection_info():
    """Get information about the vector database collection."""
    try:
        info = await vector_db.get_collection_info()
        return {
            "success": True,
            "collection_info": info,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        print(f"Error getting collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")