# OpenAI and AI service client configuration
import openai
import os
from typing import List, Dict, Any, Optional
import asyncio
from enum import Enum

# AI service configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

class AIModel(Enum):
    """Available AI models."""
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"

class AIServiceClient:
    """Unified AI service client for OpenAI and other providers."""
    
    def __init__(self):
        """Initialize AI service client."""
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.default_model = AIModel.GPT_4_TURBO
        self.default_embedding_model = AIModel.TEXT_EMBEDDING_ADA_002
        
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: AIModel = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text completion using AI model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: AI model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            
        Returns:
            Completion response with content and metadata
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        model = model or self.default_model
        
        # Prepare messages
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        formatted_messages.extend(messages)
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model.value,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model.value,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            print(f"Error generating completion: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str,
        model: AIModel = None
    ) -> List[float]:
        """
        Generate text embedding.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            Vector embedding
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        model = model or self.default_embedding_model
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.embeddings.create,
                model=model.value,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: AIModel = None,
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            batch_size: Number of texts per batch
            
        Returns:
            List of vector embeddings
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        model = model or self.default_embedding_model
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await asyncio.to_thread(
                    self.openai_client.embeddings.create,
                    model=model.value,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
                raise
        
        return embeddings
    
    async def translate_text(
        self,
        text: str,
        target_language: str = "urdu",
        preserve_technical_terms: bool = True,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language (default: urdu)
            preserve_technical_terms: Whether to preserve technical terms
            context: Additional context for translation
            
        Returns:
            Translation result with metadata
        """
        system_prompt = f"""You are a professional translator specializing in technical and educational content. 
        Translate the following text to {target_language} while maintaining accuracy and clarity.
        
        Guidelines:
        - Maintain the original meaning and tone
        - {"Preserve technical terms in English when appropriate" if preserve_technical_terms else "Translate all terms to the target language"}
        - Keep formatting and structure intact
        - Ensure the translation is natural and fluent
        {f"- Context: {context}" if context else ""}
        """
        
        messages = [
            {
                "role": "user",
                "content": f"Translate this text to {target_language}:\n\n{text}"
            }
        ]
        
        response = await self.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent translations
            max_tokens=2000
        )
        
        return {
            "translated_text": response["content"],
            "source_language": "english",  # Assuming source is English
            "target_language": target_language,
            "model": response["model"],
            "usage": response["usage"]
        }
    
    async def personalize_content(
        self,
        content: str,
        user_level: str,
        user_background: str,
        learning_goals: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Personalize content based on user profile.
        
        Args:
            content: Original content
            user_level: User's experience level (beginner/intermediate/advanced)
            user_background: User's technical background
            learning_goals: User's learning goals
            context: Additional context
            
        Returns:
            Personalized content with metadata
        """
        goals_text = ", ".join(learning_goals) if learning_goals else "general learning"
        
        system_prompt = f"""You are an AI tutor that personalizes educational content. 
        Adapt the following content for a {user_level} level learner with background in {user_background}.
        
        User's learning goals: {goals_text}
        
        Guidelines:
        - Adjust complexity and terminology for {user_level} level
        - Add relevant examples based on their {user_background} background
        - Emphasize aspects that align with their learning goals
        - Maintain educational value while making it more relevant
        - Keep the same overall structure and key concepts
        {f"- Additional context: {context}" if context else ""}
        """
        
        messages = [
            {
                "role": "user",
                "content": f"Personalize this content:\n\n{content}"
            }
        ]
        
        response = await self.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=3000
        )
        
        return {
            "personalized_content": response["content"],
            "user_level": user_level,
            "user_background": user_background,
            "learning_goals": learning_goals,
            "model": response["model"],
            "usage": response["usage"]
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of AI services."""
        health_status = {
            "openai": False,
            "claude": False
        }
        
        # Check OpenAI
        if self.openai_client:
            try:
                await asyncio.to_thread(
                    self.openai_client.models.list
                )
                health_status["openai"] = True
            except Exception as e:
                print(f"OpenAI health check failed: {e}")
        
        # TODO: Add Claude health check when implemented
        
        return health_status

# Global AI service client
ai_client = AIServiceClient()