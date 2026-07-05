from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    text: str


class CommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentPieceCreate(BaseModel):
    title: str
    platform: str
    status: str = "idea"
    script: Optional[str] = None
    tag_names: List[str] = []


class ContentPieceOut(BaseModel):
    id: int
    title: str
    platform: str
    status: str
    script: Optional[str]
    created_at: datetime

    tags: List[TagOut] = []
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True