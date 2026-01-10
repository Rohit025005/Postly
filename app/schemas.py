from pydantic import BaseModel
from fastapi_users import schemas
import uuid
from datetime import datetime

# ---------- POSTS ----------
class PostCreate(BaseModel):
    caption: str
    url: str
    file_type: str
    file_name: str


class PostResponse(PostCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


# ---------- USERS ----------
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
