from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for Many-to-Many: ContentPiece <-> Tag
content_tags = Table(
    "content_tags",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("content_pieces.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    content_pieces = relationship("ContentPiece", back_populates="owner")


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    status = Column(String, default="idea")
    script = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="content_pieces")

    comments = relationship(
        "Comment",
        back_populates="content_piece",
        cascade="all, delete-orphan"
    )

    tags = relationship(
        "Tag",
        secondary=content_tags,
        back_populates="content_pieces"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)

    content_id = Column(Integer, ForeignKey("content_pieces.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    content_piece = relationship("ContentPiece", back_populates="comments")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    content_pieces = relationship(
        "ContentPiece",
        secondary=content_tags,
        back_populates="tags"
    )