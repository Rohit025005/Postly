from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

import tempfile,uuid,shutil,os

from app.users import auth_backend, current_active_user, fastapi_users
from cloudinary.uploader import upload as cloud_upload
import cloudinary
import app.images 
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan = lifespan)


# 1. Authentication (Login/Logout)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# 2. Registration
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# 3. Password Management
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )

# 4. User Management (Includes /auth/me)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/auth",
    tags=["users"],
)


@app.post("/upload")
async def uploadFile(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    temp_path = None
    try:
        # 1) Save incoming UploadFile to a temp file
        suffix = os.path.splitext(file.filename)[1] or ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        # 2) Sanity check Cloudinary config
        api_key = cloudinary.config().api_key
        if not api_key:
            # This will be visible to client as 500 with helpful message
            raise RuntimeError("Cloudinary not configured (missing API key). Check app/images.py and .env")

        # 3) Upload to Cloudinary
        # resource_type="auto" lets Cloudinary detect image vs video
        result = cloud_upload(
            temp_path,
            resource_type="auto",
            folder="simple_social",
            use_filename=True,
            unique_filename=True
        )

        # result is a dict. For example result['secure_url'] and result['public_id']
        secure_url = result.get("secure_url")
        public_id = result.get("public_id")
        if not secure_url:
            raise RuntimeError(f"Cloudinary upload did not return secure_url. Response keys: {list(result.keys())}")

        # 4) Create DB post
        post = Post(
            user_id=user.id,
            caption=caption,
            url=secure_url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=public_id or file.filename
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return {"success": True, "post": {
            "id": str(post.id),
            "url": post.url,
            "file_name": post.file_name,
        }}

    except Exception as e:
        # Send clear message back to the frontend
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        try:
            file.file.close()
        except Exception:
            pass



@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown")
            }
        )

    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))