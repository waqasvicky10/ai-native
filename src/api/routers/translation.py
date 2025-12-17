# Translation API router
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import re

from ..database import get_db
from ..ai_client import ai_client
from ..schemas import TranslationRequest, TranslationResponse, BaseResponse

router = APIRouter()

# Technical terms that should be preserved in Urdu translation
TECHNICAL_TERMS = {
    "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning",
    "Neural Network", "CNN", "RNN", "LSTM", "Transformer", "GPT",
    "Computer Vision", "NLP", "Natural Language Processing",
    "Robotics", "Humanoid", "Actuator", "Sensor", "Servo", "Motor",
    "Algorithm", "API", "Framework", "Library", "Python", "TensorFlow",
    "PyTorch", "OpenCV", "ROS", "Robot Operating System",
    "Kinematics", "Dynamics", "Control System", "PID", "Feedback",
    "Reinforcement Learning", "Supervised Learning", "Unsupervised Learning",
    "Dataset", "Training", "Validation", "Testing", "Overfitting",
    "Hyperparameter", "Gradient Descent", "Backpropagation",
    "Convolutional", "Recurrent", "Attention", "Embedding"
}

def extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms from text that should be preserved."""
    found_terms = []
    text_lower = text.lower()
    
    for term in TECHNICAL_TERMS:
        # Case-insensitive search for technical terms
        if term.lower() in text_lower:
            found_terms.append(term)
    
    return found_terms

def calculate_translation_quality(
    original: str, 
    translated: str, 
    preserved_terms: List[str]
) -> float:
    """
    Calculate translation quality score based on various factors.
    
    Factors considered:
    - Length ratio (translated text should be reasonable length)
    - Technical term preservation
    - Basic structure preservation
    """
    if not translated or not original:
        return 0.0
    
    # Length ratio score (Urdu is typically 1.2-1.8x longer than English)
    length_ratio = len(translated) / len(original)
    length_score = 1.0 if 1.0 <= length_ratio <= 2.0 else max(0.5, 1.0 - abs(length_ratio - 1.4) * 0.5)
    
    # Technical term preservation score
    original_terms = extract_technical_terms(original)
    if original_terms:
        preserved_ratio = len(preserved_terms) / len(original_terms)
        term_score = preserved_ratio
    else:
        term_score = 1.0  # No technical terms to preserve
    
    # Structure preservation (basic check for formatting)
    structure_score = 1.0
    if original.count('\n') > 0:
        # Check if paragraph structure is maintained
        original_paragraphs = len(original.split('\n\n'))
        translated_paragraphs = len(translated.split('\n\n'))
        if original_paragraphs > 1:
            structure_score = min(1.0, translated_paragraphs / original_paragraphs)
    
    # Weighted average
    quality_score = (length_score * 0.3 + term_score * 0.5 + structure_score * 0.2)
    return min(1.0, quality_score)

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    db: Session = Depends(get_db)
):
    """
    Translate text to target language (primarily Urdu).
    
    Features:
    - High-quality translation with context awareness
    - Technical term preservation
    - Quality scoring
    - Cultural adaptation
    """
    try:
        # Extract technical terms that should be preserved
        technical_terms = extract_technical_terms(request.text) if request.preserve_technical_terms else []
        
        # Enhanced system prompt for better Urdu translation
        system_prompt = f"""You are a professional translator specializing in technical and educational content translation to {request.target_language.value}.

Translation Guidelines:
1. Maintain the original meaning, tone, and educational value
2. Use clear, natural {request.target_language.value} that flows well
3. {"Preserve these technical terms in English: " + ", ".join(technical_terms) if technical_terms else "Translate technical terms appropriately while maintaining clarity"}
4. Keep all formatting (markdown, line breaks, etc.) intact
5. Ensure the translation is suitable for educational content
6. Use appropriate academic and technical vocabulary in {request.target_language.value}
7. Maintain the structure and organization of the original text

{f"Additional context: {request.context}" if request.context else ""}

For Urdu specifically:
- Use proper Urdu script and grammar
- Maintain right-to-left text flow where appropriate
- Use appropriate honorifics and formal language for educational content
- Blend technical English terms naturally with Urdu text when preserving them
"""

        # Perform translation
        translation_result = await ai_client.translate_text(
            text=request.text,
            target_language=request.target_language.value,
            preserve_technical_terms=request.preserve_technical_terms,
            context=request.context
        )
        
        translated_text = translation_result["translated_text"]
        
        # Verify technical terms are preserved
        preserved_terms = []
        if request.preserve_technical_terms:
            for term in technical_terms:
                if term in translated_text:
                    preserved_terms.append(term)
        
        # Calculate quality score
        quality_score = calculate_translation_quality(
            original=request.text,
            translated=translated_text,
            preserved_terms=preserved_terms
        )
        
        return TranslationResponse(
            translated_text=translated_text,
            source_language="english",
            target_language=request.target_language.value,
            quality_score=quality_score,
            preserved_terms=preserved_terms
        )
        
    except Exception as e:
        print(f"Error in translation: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/translate-batch")
async def translate_batch(
    texts: List[str],
    target_language: str = "urdu",
    preserve_technical_terms: bool = True,
    context: str = None,
    db: Session = Depends(get_db)
):
    """
    Translate multiple texts in batch for efficiency.
    
    Useful for translating entire chapters or multiple sections.
    """
    try:
        results = []
        
        # Process in smaller batches to avoid timeout
        batch_size = 5
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = []
            
            for text in batch:
                # Create individual translation request
                request = TranslationRequest(
                    text=text,
                    target_language=target_language,
                    preserve_technical_terms=preserve_technical_terms,
                    context=context
                )
                
                # Translate individual text
                result = await translate_text(request, db)
                batch_results.append({
                    "original_text": text,
                    "translated_text": result.translated_text,
                    "quality_score": result.quality_score,
                    "preserved_terms": result.preserved_terms
                })
            
            results.extend(batch_results)
        
        return {
            "success": True,
            "translations": results,
            "total_count": len(results),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error in batch translation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported translation languages."""
    return {
        "success": True,
        "supported_languages": [
            {
                "code": "urdu",
                "name": "Urdu",
                "native_name": "اردو",
                "primary": True
            },
            {
                "code": "english",
                "name": "English",
                "native_name": "English",
                "primary": False
            }
        ],
        "default_target": "urdu",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/technical-terms")
async def get_technical_terms():
    """Get list of technical terms that are preserved during translation."""
    return {
        "success": True,
        "technical_terms": sorted(list(TECHNICAL_TERMS)),
        "total_count": len(TECHNICAL_TERMS),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/validate-translation")
async def validate_translation(
    original: str,
    translated: str,
    target_language: str = "urdu",
    db: Session = Depends(get_db)
):
    """
    Validate the quality of a translation.
    
    Provides detailed feedback on translation quality.
    """
    try:
        # Extract technical terms from original
        technical_terms = extract_technical_terms(original)
        
        # Check which terms are preserved
        preserved_terms = []
        for term in technical_terms:
            if term in translated:
                preserved_terms.append(term)
        
        # Calculate quality score
        quality_score = calculate_translation_quality(original, translated, preserved_terms)
        
        # Generate feedback
        feedback = []
        
        if quality_score >= 0.8:
            feedback.append("High quality translation")
        elif quality_score >= 0.6:
            feedback.append("Good translation with minor issues")
        else:
            feedback.append("Translation may need improvement")
        
        if technical_terms and len(preserved_terms) < len(technical_terms):
            missing_terms = set(technical_terms) - set(preserved_terms)
            feedback.append(f"Missing technical terms: {', '.join(missing_terms)}")
        
        length_ratio = len(translated) / len(original) if original else 0
        if length_ratio > 2.5:
            feedback.append("Translation may be too verbose")
        elif length_ratio < 0.5:
            feedback.append("Translation may be too brief")
        
        return {
            "success": True,
            "quality_score": quality_score,
            "preserved_terms": preserved_terms,
            "missing_terms": list(set(technical_terms) - set(preserved_terms)),
            "feedback": feedback,
            "length_ratio": length_ratio,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error validating translation: {e}")
        raise HTTPException(status_code=500, detail=f"Translation validation failed: {str(e)}")