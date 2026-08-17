"""
1. Thoughtful Engagement & Counter-Comment Assistant agent for high-impact social networking.
2. Formulates polite, technically sound, value-additive insights under top AI founders' & researchers' posts.
3. Drives organic inbound profile visits from tech leaders, CTOs, and recruitment managers.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import EngagementCommentDraft

logger = logging.getLogger(__name__)

ENGAGEMENT_SYSTEM_PROMPT = """
You are a Real-World Senior AI Engineer casually commenting on Twitter/LinkedIn threads.
You talk like an engineer in a Discord server or GitHub issue discussion.

STRICT HUMAN DEVELOPER RULES:
1. MAX 1-2 SHORT SENTENCES per comment. Keep it under 40 words.
2. BANNED PHRASES (Instant Bot Tell):
   - NEVER say "truly resonates", "fascinating to see", "great observation", "the point about X is critical".
3. TONE & STRUCTURE:
   - Start immediately with a personal debugging note or practical question (e.g. "Hit the exact same wall on...", "Curious how you handle...", "In our benchmarks we saw...").
   - Mention one specific technical number or bottleneck (latency, VRAM, subgraphs, pruning).
   - End with a casual, sharp question.

Write 2-3 super punchy, realistic engineer comments.
"""



async def engagement_node(state: AgentState) -> Dict[str, Any]:
    """
    Engagement Node in the LangGraph workflow.
    Generates 2-3 high-value, polite comments for social media networking.
    """
    logger.info("Generating Thoughtful Engagement & Networking Comments...")
    
    technical_analysis = state.get("technical_analysis", "")
    
    prompt = f"""
Based on the following technical analysis, formulate 2-3 polite, value-additive technical comments to share in discussions with other AI engineers and founders:

TECHNICAL ANALYSIS:
{technical_analysis}

Generate output matching the EngagementCommentDraft schema.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=ENGAGEMENT_SYSTEM_PROMPT,
        tier=ModelTier.WRITER,
        temperature=0.6,
        response_model=EngagementCommentDraft,
    )

    logger.info("Engagement Comments Generated Successfully.")
    
    if isinstance(draft, str):
        try:
            parsed_draft = EngagementCommentDraft.model_validate_json(draft)
        except Exception:
            parsed_draft = None
    else:
        parsed_draft = draft

    return {
        "engagement_draft": parsed_draft,
        "status": "ENGAGEMENT_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }
