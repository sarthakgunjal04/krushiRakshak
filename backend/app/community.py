"""
Community/Posts API endpoints.

Handles post creation, fetching, liking, and commenting.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import uuid

from .database import get_db
from .models import Post, PostLike, Comment, User
from .schemas import PostCreate, PostOut, PostLikeCreate, CommentCreate, CommentOut
from .auth import get_current_user

router = APIRouter(prefix="/community", tags=["community"])

# Create uploads directory if it doesn't exist
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


# ============================================================================
# Posts Endpoints
# ============================================================================

@router.get("/posts", response_model=List[PostOut])
async def get_posts(
    skip: int = 0,
    limit: int = 50,
    crop: str = None,
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all posts with author information and like status. Supports filtering by crop and category."""
    try:
        query = db.query(Post)
        
        # Apply filters
        if crop:
            query = query.filter(Post.crop == crop)
        if category:
            query = query.filter(Post.category == category)
        
        posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for post in posts:
            # Get author info
            author = db.query(User).filter(User.id == post.author_id).first()
            
            # Check if current user liked this post
            is_liked = db.query(PostLike).filter(
                PostLike.post_id == post.id,
                PostLike.user_id == current_user.id
            ).first() is not None
            
            post_dict = {
                "id": post.id,
                "content": post.content,
                "author_id": post.author_id,
                "author": {
                    "id": author.id,
                    "name": author.name,
                    "email": author.email
                } if author else None,
                "author_name": author.name if author else None,
                "region": post.region or (author.state if author else None),
                "crop": post.crop,
                "category": post.category,
                "likes_count": post.likes_count if post.likes_count is not None else 0,
                "comments_count": post.comments_count if post.comments_count is not None else 0,
                "image_url": post.image_url,
                "created_at": post.created_at,
                "is_liked": is_liked
            }
            result.append(PostOut(**post_dict))
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post."""
    # Use user's state as region if not provided
    region = post_data.region or current_user.state
    
    db_post = Post(
        content=post_data.content,
        author_id=current_user.id,
        region=region,
        crop=post_data.crop,
        category=post_data.category,
        image_url=post_data.image_url,
        likes_count=0,
        comments_count=0
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Return with author info
    author = db.query(User).filter(User.id == db_post.author_id).first()
    return PostOut(
        id=db_post.id,
        content=db_post.content,
        author_id=db_post.author_id,
        author={
            "id": author.id,
            "name": author.name,
            "email": author.email
        } if author else None,
        author_name=author.name if author else None,
        region=db_post.region,
        crop=db_post.crop,
        category=db_post.category,
        likes_count=db_post.likes_count,
        comments_count=db_post.comments_count,
        image_url=db_post.image_url,
        created_at=db_post.created_at,
        is_liked=False
    )


@router.post("/posts/{post_id}/like", response_model=dict)
async def toggle_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or unlike a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        # Unlike: remove the like
        db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        is_liked = False
    else:
        # Like: add the like
        new_like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        post.likes_count += 1
        is_liked = True
    
    db.commit()
    
    return {
        "post_id": post_id,
        "likes_count": post.likes_count,
        "is_liked": is_liked
    }


# ============================================================================
# Comments Endpoints
# ============================================================================

@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def get_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    
    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.user_id).first()
        result.append(CommentOut(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            author_name=author.name if author else None,
            content=comment.content,
            created_at=comment.created_at
        ))
    
    return result


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    db.add(db_comment)
    post.comments_count += 1
    db.commit()
    db.refresh(db_comment)
    
    author = db.query(User).filter(User.id == current_user.id).first()
    return CommentOut(
        id=db_comment.id,
        post_id=db_comment.post_id,
        user_id=db_comment.user_id,
        author_name=author.name if author else None,
        content=db_comment.content,
        created_at=db_comment.created_at
    )


# ============================================================================
# Image Upload Endpoint
# ============================================================================

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an image file and return its URL."""
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Return URL (relative path that can be served)
    return {"url": f"/community/images/{unique_filename}"}


@router.get("/images/{filename}")
async def get_image(filename: str):
    """Serve uploaded images."""
    file_path = UPLOAD_DIR / filename
    
    # Security: prevent directory traversal
    if not file_path.exists() or not str(file_path.resolve()).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)


# ============================================================================
# Top Contributors Endpoint
# ============================================================================

@router.get("/top-contributors")
async def get_top_contributors(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top contributors by post count."""
    # Query to get users with their post counts, ordered by count descending
    contributors = db.query(
        User.id,
        User.name,
        func.count(Post.id).label('posts_count')
    ).join(Post, User.id == Post.author_id)\
     .group_by(User.id, User.name)\
     .order_by(desc('posts_count'))\
     .limit(limit)\
     .all()
    
    result = []
    for user_id, name, posts_count in contributors:
        result.append({
            "user_id": user_id,
            "name": name or f"User {user_id}",
            "posts_count": posts_count
        })
    
    return result


# ============================================================================
# Search Endpoint
# ============================================================================

@router.get("/posts/search", response_model=List[PostOut])
async def search_posts(
    q: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search posts by content, author name, or crop."""
    if not q or not q.strip():
        return []
    
    search_term = f"%{q.strip()}%"
    
    # Search in post content, author name, and crop
    query = db.query(Post).join(User, Post.author_id == User.id).filter(
        or_(
            Post.content.ilike(search_term),
            User.name.ilike(search_term),
            Post.crop.ilike(search_term)
        )
    )
    
    posts = query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        # Get author info
        author = db.query(User).filter(User.id == post.author_id).first()
        
        # Check if current user liked this post
        is_liked = db.query(PostLike).filter(
            PostLike.post_id == post.id,
            PostLike.user_id == current_user.id
        ).first() is not None
        
        post_dict = {
            "id": post.id,
            "content": post.content,
            "author_id": post.author_id,
            "author": {
                "id": author.id,
                "name": author.name,
                "email": author.email
            } if author else None,
            "author_name": author.name if author else None,
            "region": post.region or (author.state if author else None),
            "crop": post.crop,
            "category": post.category,
            "likes_count": post.likes_count if post.likes_count is not None else 0,
            "comments_count": post.comments_count if post.comments_count is not None else 0,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "is_liked": is_liked
        }
        result.append(PostOut(**post_dict))
    
    return result


