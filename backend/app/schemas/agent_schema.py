"""
1. Pydantic schemas defining structured outputs from LLM agent nodes (e.g. SlideDeckSchema, TweetThreadSchema).
2. Enforces schema validation on model outputs to guarantee reliable JSON parsing from OpenRouter models.
3. Structures critic evaluation results (technical depth score, anti-cringe check, feedback notes).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# 1. VISUAL CAROUSEL & SLIDE DECK SCHEMAS
# -----------------------------------------------------------------------------
class CarouselSlide(BaseModel):
    """Represents a single slide in a LinkedIn PDF carousel."""
    slide_number: int = Field(description="Sequential slide number (e.g. 1, 2, 3...)")
    title: str = Field(description="Punchy, bold slide title")
    bullets: List[str] = Field(description="2-3 concise, high-signal bullet points", max_items=4)
    code_snippet: Optional[str] = Field(default=None, description="Optional short syntax-highlighted code snippet")


class CarouselDeck(BaseModel):
    """Complete multi-slide PDF carousel deck."""
    deck_title: str = Field(description="Main topic or catchy hook of the carousel")
    slides: List[CarouselSlide] = Field(description="5 to 8 sequential carousel slides", min_items=4, max_items=8)


# -----------------------------------------------------------------------------
# 2. PLATFORM SPECIFIC CONTENT DRAFTS
# -----------------------------------------------------------------------------
class LinkedInPostDraft(BaseModel):
    """Structured LinkedIn authority post draft."""
    hook: str = Field(description="Contrarian or curiosity-driven first 2 lines (above 'see more')")
    body: str = Field(description="Senior technical breakdown explaining why standard approaches fail and how the solution works")
    key_takeaways: List[str] = Field(description="3-4 bulleted actionable engineering takeaways")
    carousel_deck: CarouselDeck = Field(description="Structured slide deck for PDF carousel generation")
    hashtags: List[str] = Field(description="3-5 niche technical hashtags (e.g. #AIEngineering, #LangGraph, #LLMOps)")


class VideoScriptDraft(BaseModel):
    """1-2 Min Video Creator Kit for LinkedIn, X & YouTube Shorts."""
    video_title: str = Field(description="Catchy video title / hook idea")
    hook_15s: str = Field(description="[00:00-00:15] High-energy hook highlighting the real-world problem or bottleneck")
    architecture_30s: str = Field(description="[00:15-00:45] System design explanation of why naive approaches fail")
    code_walkthrough_30s: str = Field(description="[00:45-01:15] Step-by-step narration of the code logic displayed on screen")
    cta_15s: str = Field(description="[01:15-01:30] Wrap up and Call to Action (e.g., 'Full repo in comments / drop your thoughts')")
    screen_code_snippet: str = Field(description="Clean, runnable Python script to keep open on your IDE screen during recording")


class TwitterThreadDraft(BaseModel):
    """Structured X (Twitter) thread draft."""
    hook_tweet: str = Field(description="Tweet 1: High-virality technical hook with thread indicator (1/N)")
    body_tweets: List[str] = Field(description="Tweets 2 to N: Punchy breakdown points, architecture insights, and code references", min_items=3, max_items=6)
    conclusion_tweet: str = Field(description="Final Tweet: Summary takeaway + invitation for developer discussion")
    code_card_snippet: Optional[str] = Field(default=None, description="Clean code snippet for automated dark-mode card image generation")


class TechnicalArticleDraft(BaseModel):
    """Full-length technical markdown tutorial for Dev.to and Medium."""
    title: str = Field(description="Comprehensive technical title (e.g. 'Under the Hood: Building GraphRAG with LangGraph')")
    subtitle: str = Field(description="SEO-friendly subtitle explaining target architecture and metrics")
    markdown_content: str = Field(description="1,200-2,000 word markdown tutorial with H2/H3 headers, code blocks, and diagrams")
    tags: List[str] = Field(description="4-5 technical tags for Dev.to / Medium SEO ranking")


class EngagementCommentDraft(BaseModel):
    """Thoughtful, non-aggressive value-add comments for top founders' posts."""
    suggested_comments: List[str] = Field(
        description="2-3 respectful, insightful technical comments to drop under relevant AI leaders' posts",
        min_items=2,
        max_items=3
    )


# -----------------------------------------------------------------------------
# 3. CRITIC QUALITY & ANTI-CRINGE RUBRIC SCHEMA
# -----------------------------------------------------------------------------
class CriticEvaluation(BaseModel):
    """Quality gatekeeper evaluation output."""
    passed: bool = Field(description="True if score >= CRITIC_PASS_THRESHOLD, False if rejected")
    overall_score: int = Field(description="Quality score from 0 to 100", ge=0, le=100)
    technical_accuracy_score: int = Field(description="Accuracy and depth score (0-100)", ge=0, le=100)
    anti_cringe_score: int = Field(description="Score for zero AI buzzwords and authentic senior persona (0-100)", ge=0, le=100)
    critique_notes: str = Field(description="Constructive feedback explaining what passed or specific instructions to fix if rejected")

