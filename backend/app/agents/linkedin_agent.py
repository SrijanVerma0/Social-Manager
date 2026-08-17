"""
1. LinkedIn Authority Stylist agent that transforms technical summaries into high-impact thought leadership posts.
2. Crafts strong non-cringe hooks, actionable takeaways, and slide-by-slide outlines for PDF carousels.
3. Enforces senior AI engineer voice: zero generic fluff, high information density, and professional authority.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import LinkedInPostDraft

logger = logging.getLogger(__name__)

LINKEDIN_SYSTEM_PROMPT = """
You are a Principal AI Engineer and Thought Leader writing for LinkedIn.
Your audience consists of CTOs, AI Founders, Engineering Managers, and Senior Developers.

LINKEDIN FORMULA:
1. HOOK: 2 punchy lines that break a common misconception or highlight an engineering reality check.
2. CORE VALUE (The "Why"): Explain why standard architectures/approaches bottleneck in production.
3. TECHNICAL SOLUTION: Explain the architectural fix with concrete concepts (memory layout, state transitions, inference speedups).
4. KEY TAKEAWAYS: 3 bullet points of senior advice.
5. PDF CAROUSEL DECK (5-7 Slides):
   - Slide 1: High-contrast cover slide title & subtitle.
   - Slide 2: The Bottleneck / Problem breakdown.
   - Slide 3: System Architecture flow.
   - Slide 4: Deep-dive & Code/Logic example.
   - Slide 5: Trade-offs & Benchmark comparison.
   - Slide 6: Summary & Call to Action.

STRICT TONE RULES:
- ZERO cringe ("thrilled to share", "delve into", "game-changing", "in today's world").
- Write in first-person as a hands-on systems builder.
- Keep sentences crisp with clean line breaks.
"""


async def linkedin_node(state: AgentState) -> Dict[str, Any]:
    """
    LinkedIn Stylist Node in the LangGraph workflow.
    Generates structured LinkedIn Post and PDF Carousel slide deck.
    """
    logger.info("Generating LinkedIn Authority Post & PDF Carousel Outline...")
    
    technical_analysis = state.get("technical_analysis", "")
    
    prompt = f"""
Transform the following technical analysis into a high-authority LinkedIn Post and a structured 5-7 slide Carousel Deck:

TECHNICAL ANALYSIS:
{technical_analysis}

Generate output matching the required structured schema.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=LINKEDIN_SYSTEM_PROMPT,
        tier=ModelTier.WRITER,
        temperature=0.6,
        response_model=LinkedInPostDraft,
    )

    logger.info("LinkedIn Post and Carousel Draft Generated Successfully.")
    
    # If response is a Pydantic object or string, handle cleanly
    if isinstance(draft, str):
        try:
            parsed_draft = LinkedInPostDraft.model_validate_json(draft)
        except Exception:
            parsed_draft = None
    else:
        parsed_draft = draft

    return {
        "linkedin_draft": parsed_draft,
        "status": "LINKEDIN_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }
