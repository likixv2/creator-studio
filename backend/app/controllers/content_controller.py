from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ContentPiece, User, Tag
from ..schemas import ContentPieceCreate, ContentPieceOut
from ..auth import get_current_user
from typing import Optional
import os
import uuid
from fastapi import UploadFile, File
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/", response_model=ContentPieceOut)
def create_content(
    data: ContentPieceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    piece = ContentPiece(
        title=data.title,
        platform=data.platform,
        status=data.status,
        script=data.script,
        owner_id=current_user.id,
    )
    for name in data.tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        piece.tags.append(tag)
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece

@router.get("/", response_model=List[ContentPieceOut])
def list_content(
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ContentPiece).filter(ContentPiece.owner_id == current_user.id)

    if status:
        query = query.filter(ContentPiece.status.ilike(status.strip()))

    if search:
        query = query.filter(ContentPiece.title.ilike(f"%{search.strip()}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{content_id}", response_model=ContentPieceOut)
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    piece = db.query(ContentPiece).filter(ContentPiece.id == content_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if piece.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this content piece")
    return piece


@router.put("/{content_id}", response_model=ContentPieceOut)
def update_content(
    content_id: int,
    data: ContentPieceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    piece = db.query(ContentPiece).filter(ContentPiece.id == content_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if piece.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this content piece")

    piece.title = data.title
    piece.platform = data.platform
    piece.status = data.status
    piece.script = data.script
    db.commit()
    db.refresh(piece)
    return piece


@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    piece = db.query(ContentPiece).filter(ContentPiece.id == content_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if piece.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this content piece")

    db.delete(piece)
    db.commit()
    return {"message": "Content piece deleted"}

@router.post("/{content_id}/thumbnail", response_model=ContentPieceOut)
def upload_thumbnail(
    content_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    piece = db.query(ContentPiece).filter(ContentPiece.id == content_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Content piece not found")
    if piece.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this content piece")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    piece.thumbnail_url = f"/{UPLOAD_DIR}/{unique_filename}"
    db.commit()
    db.refresh(piece)
    return piece