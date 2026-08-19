"""
1. Defines the Post database entity representing a single piece of content for a specific social platform.
2. Tracks the lifecycle state of the post (DRAFT -> APPROVED -> PUBLISHED -> REJECTED).
3. Stores platform-specific binary assets like generated PDF carousel paths or PNG images.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.campaign import Base

if TYPE_CHECKING:
    from backend.app.models.campaign import Campaign


class PostStatus(str, PyEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"


class PostPlatform(str, PyEnum):
    LINKEDIN = "LINKEDIN"
    TWITTER = "TWITTER"
    BLOG = "BLOG"
    VIDEO = "VIDEO"
    ENGAGEMENT = "ENGAGEMENT"


class Post(Base):
    """
    Individual social media post linked to a parent Campaign.
    """
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    
    platform: Mapped[PostPlatform] = mapped_column(Enum(PostPlatform), nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.DRAFT)
    
    # Text Content
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Binary Assets (Paths stored on disk)
    media_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True) # PDF or PNG path
    
    # Live URL after successful API publishing
    published_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to Campaign
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, platform='{self.platform.name}', status='{self.status.name}')>"
