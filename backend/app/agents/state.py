"""
1. Defines the 'AgentState' TypedDict that acts as the central blackboard memory passed across LangGraph nodes.
2. Holds raw scraped articles, validated technical summaries, platform drafts, visual metadata, and critic reviews.
3. Ensures immutable and observable state updates throughout the multi-agent graph execution cycle.
"""

from typing import TypedDict, List, Dict, Any, Optional
from backend.app.schemas.agent_schema import (
    LinkedInPostDraft,
    VideoScriptDraft,
    TwitterThreadDraft,
    TechnicalArticleDraft,
    EngagementCommentDraft,
    CriticEvaluation,
)


class AgentState(TypedDict):
    """
    Central State Graph memory shared across all LangGraph nodes.
    """
    # 1. Input Trigger & Raw Ingestion
    topic_seed: Optional[str]                    # Manual input or autonomous discovery topic
    build_in_public_note: Optional[str]          # Optional voice/video/commit note from you
    raw_sources: List[Dict[str, Any]]            # Tavily, arXiv, and GitHub extracted raw items

    # 2. Deep Technical Analysis & Verification
    technical_analysis: Optional[str]            # Structured architectural takeaways & verified code

    # 3. Multi-Platform Output Drafts
    linkedin_draft: Optional[LinkedInPostDraft]
    video_script_draft: Optional[VideoScriptDraft]
    twitter_draft: Optional[TwitterThreadDraft]
    blog_draft: Optional[TechnicalArticleDraft]
    engagement_draft: Optional[EngagementCommentDraft]

    # 4. Critic Evaluation & Feedback Loop
    critic_review: Optional[CriticEvaluation]
    revision_count: int                          # Prevents infinite loops (max 3 retries)
    status: str                                  # 'SCOUTING', 'ANALYZING', 'DRAFTING', 'REVIEWING', 'APPROVED', 'REJECTED'

