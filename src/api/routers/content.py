# Content management API router
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..database import get_db
from ..vector_db import vector_db
from ..ai_client import ai_client
from ..routers.auth import get_current_user
from ..models.user import User, UserProgress, UserBookmark
from ..schemas import (
    ProgressUpdate, BookmarkCreate, BookmarkResponse, 
    ProgressResponse, BaseResponse, ContentType, UserLevel
)

router = APIRouter()

@router.post("/progress", response_model=ProgressResponse)
async def update_progress(
    request: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user progress for a chapter.
    
    Tracks reading time, completion status, and assessment scores.
    """
    try:
        # Get or create progress record
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.chapter_id == request.chapter_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                chapter_id=request.chapter_id,
                time_spent=0,
                completed=False,
                created_at=datetime.utcnow()
            )
            db.add(progress)
        
        # Update progress
        progress.time_spent += request.time_spent
        
        if request.completed is not None:
            progress.completed = request.completed
            if request.completed:
                progress.completed_at = datetime.utcnow()
        
        if request.assessment_score is not None:
            progress.assessment_score = request.assessment_score
            progress.assessment_completed_at = datetime.utcnow()
        
        progress.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Calculate overall progress statistics
        total_progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id
        ).all()
        
        total_chapters = len(total_progress)
        completed_chapters = len([p for p in total_progress if p.completed])
        total_time = sum(p.time_spent for p in total_progress)
        avg_assessment_score = None
        
        assessment_scores = [p.assessment_score for p in total_progress if p.assessment_score is not None]
        if assessment_scores:
            avg_assessment_score = sum(assessment_scores) / len(assessment_scores)
        
        progress_data = {
            "chapter_id": progress.chapter_id,
            "time_spent": progress.time_spent,
            "completed": progress.completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "assessment_score": progress.assessment_score,
            "assessment_completed_at": progress.assessment_completed_at.isoformat() if progress.assessment_completed_at else None,
            "updated_at": progress.updated_at.isoformat(),
            "overall_stats": {
                "total_chapters": total_chapters,
                "completed_chapters": completed_chapters,
                "completion_percentage": (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
                "total_time_spent": total_time,
                "average_assessment_score": avg_assessment_score
            }
        }
        
        return ProgressResponse(progress=progress_data)
        
    except Exception as e:
        db.rollback()
        print(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=f"Progress update failed: {str(e)}")

@router.get("/progress", response_model=ProgressResponse)
async def get_user_progress(
    chapter_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user progress for all chapters or a specific chapter.
    """
    try:
        query = db.query(UserProgress).filter(UserProgress.user_id == current_user.id)
        
        if chapter_id:
            query = query.filter(UserProgress.chapter_id == chapter_id)
            progress = query.first()
            
            if not progress:
                # Return empty progress for chapter
                progress_data = {
                    "chapter_id": chapter_id,
                    "time_spent": 0,
                    "completed": False,
                    "completed_at": None,
                    "assessment_score": None,
                    "assessment_completed_at": None,
                    "updated_at": None
                }
            else:
                progress_data = {
                    "chapter_id": progress.chapter_id,
                    "time_spent": progress.time_spent,
                    "completed": progress.completed,
                    "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
                    "assessment_score": progress.assessment_score,
                    "assessment_completed_at": progress.assessment_completed_at.isoformat() if progress.assessment_completed_at else None,
                    "updated_at": progress.updated_at.isoformat() if progress.updated_at else None
                }
        else:
            # Return all progress
            all_progress = query.all()
            
            progress_data = {
                "chapters": [
                    {
                        "chapter_id": p.chapter_id,
                        "time_spent": p.time_spent,
                        "completed": p.completed,
                        "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                        "assessment_score": p.assessment_score,
                        "assessment_completed_at": p.assessment_completed_at.isoformat() if p.assessment_completed_at else None,
                        "updated_at": p.updated_at.isoformat() if p.updated_at else None
                    }
                    for p in all_progress
                ],
                "overall_stats": {
                    "total_chapters": len(all_progress),
                    "completed_chapters": len([p for p in all_progress if p.completed]),
                    "completion_percentage": (len([p for p in all_progress if p.completed]) / len(all_progress) * 100) if all_progress else 0,
                    "total_time_spent": sum(p.time_spent for p in all_progress),
                    "average_assessment_score": sum(p.assessment_score for p in all_progress if p.assessment_score) / len([p for p in all_progress if p.assessment_score]) if [p for p in all_progress if p.assessment_score] else None
                }
            }
        
        return ProgressResponse(progress=progress_data)
        
    except Exception as e:
        print(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    request: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a bookmark for a chapter section.
    """
    try:
        # Check if bookmark already exists
        existing_bookmark = db.query(UserBookmark).filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.chapter_id == request.chapter_id,
            UserBookmark.section == request.section
        ).first()
        
        if existing_bookmark:
            # Update existing bookmark
            existing_bookmark.note = request.note
            existing_bookmark.updated_at = datetime.utcnow()
            bookmark = existing_bookmark
        else:
            # Create new bookmark
            bookmark = UserBookmark(
                user_id=current_user.id,
                chapter_id=request.chapter_id,
                section=request.section,
                note=request.note,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(bookmark)
        
        db.commit()
        
        bookmark_data = {
            "id": bookmark.id,
            "chapter_id": bookmark.chapter_id,
            "section": bookmark.section,
            "note": bookmark.note,
            "created_at": bookmark.created_at.isoformat(),
            "updated_at": bookmark.updated_at.isoformat()
        }
        
        return BookmarkResponse(bookmark=bookmark_data)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating bookmark: {e}")
        raise HTTPException(status_code=500, detail=f"Bookmark creation failed: {str(e)}")

@router.get("/bookmarks")
async def get_user_bookmarks(
    chapter_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user bookmarks for all chapters or a specific chapter.
    """
    try:
        query = db.query(UserBookmark).filter(UserBookmark.user_id == current_user.id)
        
        if chapter_id:
            query = query.filter(UserBookmark.chapter_id == chapter_id)
        
        bookmarks = query.order_by(UserBookmark.created_at.desc()).all()
        
        bookmark_data = [
            {
                "id": b.id,
                "chapter_id": b.chapter_id,
                "section": b.section,
                "note": b.note,
                "created_at": b.created_at.isoformat(),
                "updated_at": b.updated_at.isoformat()
            }
            for b in bookmarks
        ]
        
        return {
            "success": True,
            "bookmarks": bookmark_data,
            "total_count": len(bookmark_data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"Error getting bookmarks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get bookmarks: {str(e)}")

@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user bookmark.
    """
    try:
        bookmark = db.query(UserBookmark).filter(
            UserBookmark.id == bookmark_id,
            UserBookmark.user_id == current_user.id
        ).first()
        
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        db.delete(bookmark)
        db.commit()
        
        return BaseResponse(message="Bookmark deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting bookmark: {e}")
        raise HTTPException(status_code=500, detail=f"Bookmark deletion failed: {str(e)}")

@router.get("/chapters")
async def get_available_chapters():
    """
    Get list of available chapters in the textbook.
    
    This would typically come from a database or configuration file.
    For now, returning a static list based on the textbook structure.
    """
    chapters = [
        {
            "id": "intro",
            "title": "Introduction to Physical AI",
            "description": "Overview of Physical AI and its applications",
            "difficulty": "beginner",
            "estimated_reading_time": 30,
            "sections": [
                "What is Physical AI?",
                "Applications and Use Cases",
                "Historical Context",
                "Future Prospects"
            ]
        },
        {
            "id": "fundamentals",
            "title": "Fundamentals of Robotics",
            "description": "Basic concepts in robotics and automation",
            "difficulty": "beginner",
            "estimated_reading_time": 45,
            "sections": [
                "Robot Components",
                "Sensors and Actuators",
                "Control Systems",
                "Programming Basics"
            ]
        },
        {
            "id": "ai-integration",
            "title": "AI Integration in Robotics",
            "description": "How AI enhances robotic capabilities",
            "difficulty": "intermediate",
            "estimated_reading_time": 60,
            "sections": [
                "Machine Learning in Robotics",
                "Computer Vision",
                "Natural Language Processing",
                "Decision Making Systems"
            ]
        },
        {
            "id": "humanoid-design",
            "title": "Humanoid Robot Design",
            "description": "Principles of designing human-like robots",
            "difficulty": "intermediate",
            "estimated_reading_time": 75,
            "sections": [
                "Biomechanics",
                "Locomotion Systems",
                "Manipulation",
                "Human-Robot Interaction"
            ]
        },
        {
            "id": "advanced-topics",
            "title": "Advanced Topics",
            "description": "Cutting-edge research and applications",
            "difficulty": "advanced",
            "estimated_reading_time": 90,
            "sections": [
                "Swarm Robotics",
                "Soft Robotics",
                "Ethical Considerations",
                "Future Research Directions"
            ]
        }
    ]
    
    return {
        "success": True,
        "chapters": chapters,
        "total_count": len(chapters),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/chapters/{chapter_id}")
async def get_chapter_details(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific chapter.
    
    Includes user progress and personalization recommendations.
    """
    try:
        # Get chapter info (this would come from a database in a real implementation)
        chapters = await get_available_chapters()
        chapter = next((c for c in chapters["chapters"] if c["id"] == chapter_id), None)
        
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        # Get user progress for this chapter
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.chapter_id == chapter_id
        ).first()
        
        # Get user bookmarks for this chapter
        bookmarks = db.query(UserBookmark).filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.chapter_id == chapter_id
        ).all()
        
        chapter_details = {
            **chapter,
            "user_progress": {
                "time_spent": progress.time_spent if progress else 0,
                "completed": progress.completed if progress else False,
                "completed_at": progress.completed_at.isoformat() if progress and progress.completed_at else None,
                "assessment_score": progress.assessment_score if progress else None
            },
            "bookmarks": [
                {
                    "id": b.id,
                    "section": b.section,
                    "note": b.note,
                    "created_at": b.created_at.isoformat()
                }
                for b in bookmarks
            ],
            "bookmark_count": len(bookmarks)
        }
        
        return {
            "success": True,
            "chapter": chapter_details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chapter details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chapter details: {str(e)}")

@router.post("/chapters/{chapter_id}/generate-summary")
async def generate_chapter_summary(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized summary of a chapter based on user progress and profile.
    """
    try:
        # Get chapter content from vector database
        search_results = await vector_db.search_similar(
            query_embedding=await ai_client.generate_embedding(f"chapter {chapter_id} summary"),
            limit=10,
            filter_conditions={"chapter_id": chapter_id}
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="Chapter content not found")
        
        # Combine content
        chapter_content = "\n\n".join([result["content"] for result in search_results])
        
        # Get user profile for personalization
        from ..models.user import UserProfile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        # Generate personalized summary
        system_prompt = f"""Generate a comprehensive summary of this chapter content.

{f"User Level: {profile.background_level}" if profile else ""}
{f"User Background: {profile.technical_background}" if profile else ""}
{f"Learning Goals: {', '.join(profile.learning_goals)}" if profile and profile.learning_goals else ""}

Create a summary that:
1. Highlights key concepts and takeaways
2. Identifies practical applications
3. Suggests areas for further study
4. {"Adapts complexity for " + profile.background_level + " level" if profile else "Uses appropriate technical level"}

Keep the summary concise but comprehensive."""

        messages = [
            {
                "role": "user",
                "content": f"Summarize this chapter content:\n\n{chapter_content}"
            }
        ]
        
        ai_response = await ai_client.generate_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        return {
            "success": True,
            "chapter_id": chapter_id,
            "summary": ai_response["content"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "personalized": profile is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating chapter summary: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")