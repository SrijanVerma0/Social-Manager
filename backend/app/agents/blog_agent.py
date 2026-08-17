"""
1. Longform Technical Writer agent generating 1,200-2,000 word markdown tutorials for Dev.to and Medium.
2. Structures articles with clear headings, mermaid architecture diagrams, runnable code blocks, and SEO tags.
3. Showcases deep technical mastery to attract recruiter inbound messages and freelance client inquiries.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import TechnicalArticleDraft

logger = logging.getLogger(__name__)

BLOG_SYSTEM_PROMPT = """
You are a Principal Software Engineer and Technical Author writing in-depth tutorials on Dev.to and Medium.
Your goal is to write a comprehensive, highly practical 1,200-2,000 word technical case study.

ARTICLE STRUCTURE:
1. TITLE & SUBTITLE: Direct, technical, and SEO-optimized (e.g. "Architecting Multi-Agent State Persistence with LangGraph and SQLite Checkpointers").
2. THE PROBLEM IN PRODUCTION: Explain why naive implementations fail under real workloads (race conditions, memory leaks, latency bottlenecks).
3. SYSTEM ARCHITECTURE: Include a clear text or Mermaid diagram representation explaining data flow and agent transitions.
4. CODE IMPLEMENTATION: Provide full, runnable, and syntax-highlighted Python/LangGraph/OpenCV code snippets with line-by-line explanations.
5. BENCHMARKS & TRADE-OFFS: Compare latency, memory, or compute costs with alternatives.
6. PRACTICAL LESSONS & CONCLUSION: Concrete takeaways for production deployments.

STRICT HUMAN-WRITING RULES:
- NO robotic introduction clichés ("In this tutorial, we will delve into..."). Start directly with the engineering problem.
- NO corporate filler buzzwords ("tapestry", "unravel", "game-changing", "revolutionary").
- Write naturally with clear, pragmatic explanations as an experienced systems builder.
"""


async def blog_node(state: AgentState) -> Dict[str, Any]:
    """
    Longform Blog Node in the LangGraph workflow.
    Generates structured 1,200-2,000 word markdown tutorial for Dev.to and Medium.
    """
    logger.info("Generating Full-Length Technical Article (Dev.to / Medium)...")
    
    technical_analysis = state.get("technical_analysis", "")
    
    prompt = f"""
Transform the following technical analysis into a comprehensive 1,200-2,000 word Technical Markdown Tutorial:

TECHNICAL ANALYSIS:
{technical_analysis}

Generate output matching the TechnicalArticleDraft schema.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=BLOG_SYSTEM_PROMPT,
        tier=ModelTier.WRITER,
        temperature=0.6,
        max_tokens=3500,  # Longer token window for full-length article
        response_model=TechnicalArticleDraft,
    )

    logger.info("Technical Article Generated Successfully.")
    
    if isinstance(draft, str):
        try:
            parsed_draft = TechnicalArticleDraft.model_validate_json(draft)
        except Exception:
            parsed_draft = None
    else:
        parsed_draft = draft

    return {
        "blog_draft": parsed_draft,
        "status": "BLOG_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }

