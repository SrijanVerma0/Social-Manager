"""
1. Connects the LangGraph pipeline to the Database layer.
2. Defines the save_to_db_node which persists the final AgentState into SQLite.
3. Automatically maps state text to Campaign and Post entities.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.campaign import Campaign
from backend.app.models.post import Post, PostPlatform, PostStatus

logger = logging.getLogger(__name__)

async def save_to_db_node(state: AgentState) -> Dict[str, Any]:
    """
    Saves the final approved content to the database.
    """
    logger.info("💾 Saving approved content to the database...")
    
    # Guarantee all tables exist
    await init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            critic_review = state.get("critic_review")
            score = critic_review.overall_score if critic_review else 0.0
            
            # 1. Create the Parent Campaign
            campaign = Campaign(
                topic=state.get("topic_seed", "Unknown Topic"),
                technical_analysis=state.get("technical_analysis", ""),
                critic_score=score,
                sources_count=len(state.get("raw_sources", []))
            )
            session.add(campaign)
            await session.flush() # Flush to get the newly generated campaign.id
            
            # 2. Create Posts for Active Platforms (LinkedIn & Dev.to Blog)
            posts_to_add = []
            
            if state.get("linkedin_draft"):
                posts_to_add.append(Post(
                    campaign_id=campaign.id,
                    platform=PostPlatform.LINKEDIN,
                    status=PostStatus.APPROVED,
                    content_text=state["linkedin_draft"].model_dump_json()
                ))
                
            if state.get("blog_draft"):
                posts_to_add.append(Post(
                    campaign_id=campaign.id,
                    platform=PostPlatform.BLOG,
                    status=PostStatus.APPROVED,
                    content_text=state["blog_draft"].model_dump_json()
                ))
            
            # Save all active posts at once
            session.add_all(posts_to_add)
            await session.commit()
            
            logger.info(f"✅ Successfully saved Campaign ID {campaign.id} and {len(posts_to_add)} Posts to DB.")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Failed to save to database: {str(e)}")
            raise e
            
    return {} # Final step, no more state updates needed
