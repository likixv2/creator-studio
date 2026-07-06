from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ContentPiece, User, Tag
from ..schemas import ContentPieceCreate, ContentPieceOut
from ..auth import get_current_user

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(ContentPiece).filter(ContentPiece.owner_id == current_user.id).all()


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