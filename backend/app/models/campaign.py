"""
1. Defines the Campaign database entity representing a single topic research run.
2. Tracks research sources, raw analysis, quality score, and execution timestamps.
3. Serves as the parent relationship for all generated platform posts.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Float, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from backend.app.models.post import Post


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    """
    Campaign model grouping multi-platform posts generated from a single research run.
    """
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    technical_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata & Quality
    critic_score: Mapped[float] = mapped_column(Float, default=0.0)
    sources_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relational link to all platform posts
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, topic='{self.topic[:30]}', score={self.critic_score})>"

