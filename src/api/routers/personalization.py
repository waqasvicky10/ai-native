# Personalization API router
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..database import get_db
from ..ai_client import ai_client
from ..schemas import (
    PersonalizationRequest, PersonalizationResponse, 
    UserLevel, BaseResponse
)

router = APIRouter()

# Learning level adaptation templates
LEVEL_ADAPTATIONS = {
    UserLevel.BEGINNER: {
        "complexity_reduction": 0.7,
        "example_ratio": 1.5,
        "explanation_depth": "basic",
        "terminology": "simplified",
        "prerequisites": "minimal"
    },
    UserLevel.INTERMEDIATE: {
        "complexity_reduction": 1.0,
        "example_ratio": 1.2,
        "explanation_depth": "moderate",
        "terminology": "standard",
        "prerequisites": "some"
    },
    UserLevel.ADVANCED: {
        "complexity_reduction": 1.3,
        "example_ratio": 0.8,
        "explanation_depth": "detailed",
        "terminology": "technical",
        "prerequisites": "extensive"
    }
}

# Background-specific adaptation strategies
BACKGROUND_ADAPTATIONS = {
    "software_engineering": {
        "analogies": ["software architecture", "algorithms", "data structures"],
        "examples": ["code optimization", "system design", "debugging"],
        "connections": ["programming paradigms", "software patterns"]
    },
    "mechanical_engineering": {
        "analogies": ["mechanical systems", "control theory", "dynamics"],
        "examples": ["servo motors", "feedback systems", "mechanical design"],
        "connections": ["kinematics", "materials science", "manufacturing"]
    },
    "electrical_engineering": {
        "analogies": ["circuit design", "signal processing", "control systems"],
        "examples": ["sensors", "actuators", "embedded systems"],
        "connections": ["electronics", "power systems", "communications"]
    },
    "computer_science": {
        "analogies": ["algorithms", "data structures", "computational theory"],
        "examples": ["machine learning", "computer vision", "AI systems"],
        "connections": ["mathematics", "statistics", "optimization"]
    },
    "mathematics": {
        "analogies": ["mathematical models", "optimization", "statistics"],
        "examples": ["linear algebra", "calculus", "probability"],
        "connections": ["theoretical foundations", "proofs", "analysis"]
    },
    "physics": {
        "analogies": ["physical laws", "dynamics", "energy systems"],
        "examples": ["mechanics", "thermodynamics", "wave theory"],
        "connections": ["fundamental principles", "modeling", "simulation"]
    }
}

def generate_adaptation_strategy(
    user_level: UserLevel,
    user_background: str,
    learning_goals: List[str]
) -> Dict[str, Any]:
    """Generate personalization strategy based on user profile."""
    
    # Get level-based adaptations
    level_config = LEVEL_ADAPTATIONS.get(user_level, LEVEL_ADAPTATIONS[UserLevel.INTERMEDIATE])
    
    # Get background-specific adaptations
    background_key = user_background.lower().replace(" ", "_")
    background_config = BACKGROUND_ADAPTATIONS.get(
        background_key, 
        BACKGROUND_ADAPTATIONS["computer_science"]  # Default fallback
    )
    
    # Analyze learning goals for focus areas
    goal_keywords = []
    for goal in learning_goals:
        goal_keywords.extend(goal.lower().split())
    
    focus_areas = []
    if any(word in goal_keywords for word in ["practical", "hands-on", "implementation"]):
        focus_areas.append("practical_examples")
    if any(word in goal_keywords for word in ["theory", "theoretical", "understanding"]):
        focus_areas.append("theoretical_depth")
    if any(word in goal_keywords for word in ["career", "job", "professional"]):
        focus_areas.append("career_relevance")
    if any(word in goal_keywords for word in ["research", "advanced", "cutting-edge"]):
        focus_areas.append("research_connections")
    
    return {
        "level_config": level_config,
        "background_config": background_config,
        "focus_areas": focus_areas,
        "learning_goals": learning_goals
    }

@router.post("/personalize", response_model=PersonalizationResponse)
async def personalize_content(
    request: PersonalizationRequest,
    db: Session = Depends(get_db)
):
    """
    Personalize content based on user profile and learning preferences.
    
    Adapts content by:
    - Adjusting complexity level
    - Adding relevant examples from user's background
    - Emphasizing learning goals
    - Modifying explanation depth
    """
    try:
        # Generate adaptation strategy
        strategy = generate_adaptation_strategy(
            user_level=request.user_level,
            user_background=request.user_background,
            learning_goals=request.learning_goals
        )
        
        # Build comprehensive system prompt
        level_config = strategy["level_config"]
        background_config = strategy["background_config"]
        focus_areas = strategy["focus_areas"]
        
        system_prompt = f"""You are an AI tutor that personalizes educational content for individual learners.

User Profile:
- Level: {request.user_level.value}
- Background: {request.user_background}
- Learning Goals: {', '.join(request.learning_goals)}

Personalization Instructions:
1. Complexity Level: {level_config['explanation_depth']} explanations with {level_config['terminology']} terminology
2. Examples: Use {level_config['example_ratio']}x more examples, drawing from {request.user_background} background
3. Analogies: Connect concepts to {', '.join(background_config['analogies'])}
4. Focus Areas: Emphasize {', '.join(focus_areas) if focus_areas else 'balanced coverage'}

Background-Specific Adaptations:
- Use examples from: {', '.join(background_config['examples'])}
- Make connections to: {', '.join(background_config['connections'])}
- Draw analogies from: {', '.join(background_config['analogies'])}

Content Adaptation Rules:
- {"Simplify complex concepts and add more foundational explanations" if request.user_level == UserLevel.BEGINNER else ""}
- {"Provide moderate detail with practical applications" if request.user_level == UserLevel.INTERMEDIATE else ""}
- {"Include advanced details and research connections" if request.user_level == UserLevel.ADVANCED else ""}
- Maintain the original structure and key learning objectives
- Add relevant examples that resonate with their {request.user_background} background
- Emphasize aspects that align with their learning goals

{f"Additional context: {request.context}" if request.context else ""}

Adapt the following content while preserving its educational value and core concepts:"""

        # Generate personalized content
        personalization_result = await ai_client.personalize_content(
            content=request.content,
            user_level=request.user_level.value,
            user_background=request.user_background,
            learning_goals=request.learning_goals,
            context=request.context
        )
        
        # Generate adaptation reasons
        adaptation_reasons = []
        
        if request.user_level == UserLevel.BEGINNER:
            adaptation_reasons.append("Simplified technical terminology for beginner level")
            adaptation_reasons.append("Added foundational explanations")
        elif request.user_level == UserLevel.ADVANCED:
            adaptation_reasons.append("Included advanced technical details")
            adaptation_reasons.append("Added research connections and cutting-edge insights")
        
        adaptation_reasons.append(f"Incorporated examples from {request.user_background} background")
        
        if "practical" in " ".join(request.learning_goals).lower():
            adaptation_reasons.append("Emphasized practical applications and hands-on examples")
        
        if "career" in " ".join(request.learning_goals).lower():
            adaptation_reasons.append("Highlighted career-relevant applications")
        
        # Determine difficulty adjustment
        difficulty_adjustment = None
        if request.user_level == UserLevel.BEGINNER:
            difficulty_adjustment = "Reduced complexity by 30%"
        elif request.user_level == UserLevel.ADVANCED:
            difficulty_adjustment = "Increased depth by 30%"
        else:
            difficulty_adjustment = "Maintained standard complexity"
        
        return PersonalizationResponse(
            personalized_content=personalization_result["personalized_content"],
            adaptation_reasons=adaptation_reasons,
            difficulty_adjustment=difficulty_adjustment
        )
        
    except Exception as e:
        print(f"Error in personalization: {e}")
        raise HTTPException(status_code=500, detail=f"Content personalization failed: {str(e)}")

@router.post("/personalize-batch")
async def personalize_content_batch(
    contents: List[str],
    user_level: UserLevel,
    user_background: str,
    learning_goals: List[str],
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Personalize multiple content pieces in batch.
    
    Useful for personalizing entire chapters or course sections.
    """
    try:
        results = []
        
        # Process in batches to manage API limits
        batch_size = 3
        for i in range(0, len(contents), batch_size):
            batch = contents[i:i + batch_size]
            batch_results = []
            
            for content in batch:
                # Create personalization request
                request = PersonalizationRequest(
                    content=content,
                    user_level=user_level,
                    user_background=user_background,
                    learning_goals=learning_goals,
                    context=context
                )
                
                # Personalize content
                result = await personalize_content(request, db)
                batch_results.append({
                    "original_content": content,
                    "personalized_content": result.personalized_content,
                    "adaptation_reasons": result.adaptation_reasons,
                    "difficulty_adjustment": result.difficulty_adjustment
                })
            
            results.extend(batch_results)
        
        return {
            "success": True,
            "personalizations": results,
            "total_count": len(results),
            "user_profile": {
                "level": user_level.value,
                "background": user_background,
                "learning_goals": learning_goals
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error in batch personalization: {e}")
        raise HTTPException(status_code=500, detail=f"Batch personalization failed: {str(e)}")

@router.get("/adaptation-strategies")
async def get_adaptation_strategies():
    """Get available adaptation strategies and configurations."""
    return {
        "success": True,
        "level_adaptations": {
            level.value: config for level, config in LEVEL_ADAPTATIONS.items()
        },
        "background_adaptations": BACKGROUND_ADAPTATIONS,
        "supported_levels": [level.value for level in UserLevel],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/generate-learning-path")
async def generate_learning_path(
    user_level: UserLevel,
    user_background: str,
    learning_goals: List[str],
    available_chapters: List[str],
    db: Session = Depends(get_db)
):
    """
    Generate a personalized learning path based on user profile.
    
    Recommends chapter order and focus areas.
    """
    try:
        # Generate strategy
        strategy = generate_adaptation_strategy(user_level, user_background, learning_goals)
        
        system_prompt = f"""You are an AI educational advisor that creates personalized learning paths.

User Profile:
- Level: {user_level.value}
- Background: {user_background}
- Learning Goals: {', '.join(learning_goals)}

Available Chapters: {', '.join(available_chapters)}

Create a personalized learning path by:
1. Recommending chapter order based on user level and background
2. Identifying prerequisite knowledge gaps
3. Suggesting focus areas for each chapter
4. Estimating time requirements
5. Recommending supplementary resources

Consider the user's {user_background} background to suggest relevant connections and skip redundant basics where appropriate."""

        messages = [
            {
                "role": "user",
                "content": f"Create a personalized learning path for this user profile with the available chapters."
            }
        ]
        
        ai_response = await ai_client.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        return {
            "success": True,
            "learning_path": ai_response["content"],
            "user_profile": {
                "level": user_level.value,
                "background": user_background,
                "learning_goals": learning_goals
            },
            "available_chapters": available_chapters,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")

@router.post("/analyze-content-difficulty")
async def analyze_content_difficulty(
    content: str,
    db: Session = Depends(get_db)
):
    """
    Analyze the difficulty level of content.
    
    Helps determine appropriate user levels for content.
    """
    try:
        system_prompt = """You are an educational content analyzer. Analyze the difficulty level of the provided content.

Provide analysis on:
1. Overall difficulty level (beginner/intermediate/advanced)
2. Technical complexity score (1-10)
3. Prerequisites required
4. Key concepts covered
5. Recommended user background
6. Estimated reading time

Be specific and provide reasoning for your assessment."""

        messages = [
            {
                "role": "user",
                "content": f"Analyze the difficulty level of this content:\n\n{content}"
            }
        ]
        
        ai_response = await ai_client.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=1000
        )
        
        return {
            "success": True,
            "difficulty_analysis": ai_response["content"],
            "content_length": len(content),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error analyzing content difficulty: {e}")
        raise HTTPException(status_code=500, detail=f"Content difficulty analysis failed: {str(e)}")