"""
1. Technical Analyst agent that deep-dives into raw scouted materials to verify architecture claims and code.
2. Formulates senior-level technical breakdowns, pseudocode examples, trade-off comparisons, and core takeaways.
3. Produces a structured technical summary that serves as the single source of truth for platform stylists.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier

logger = logging.getLogger(__name__)

ANALYST_SYSTEM_PROMPT = """
You are a Principal AI Systems Architect and Lead Researcher.
Your job is to analyze raw scouted research (arXiv papers, GitHub code, search results, or personal notes) and formulate an authoritative, deep-dive technical breakdown.

YOUR ANALYSIS MUST INCLUDE:
1. THE CORE BOTTLENECK: Why do standard/naive approaches fail in real-world production?
2. ARCHITECTURAL MECHANISM: How does this novel system/paper solve it? (Explain the data flow, state machine, or kernel optimization).
3. CONCRETE METRICS & TRADE-OFFS: Mention latency, memory (VRAM), accuracy, or compute cost trade-offs. Never say "it is better"; quantify why and where it might fail.
4. CODE / PSEUDOCODE PROOF: Provide a clean, elegant, runnable Python/PyTorch/LangGraph snippet demonstrating the core concept.
5. SENIOR KEY TAKEAWAYS: 3-4 bullet points a Staff Engineer or CTO would care about.

VOICE & TONE:
- Authoritative, senior, precise, and hands-on.
- ZERO generic marketing buzzwords ("revolutionize", "game changer", "thrilled").
- Focus on practical engineering implementation.
"""


async def analyst_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyst Node in the LangGraph workflow.
    Synthesizes raw candidate sources into deep technical breakdown and code proof.
    """
    logger.info("Starting Deep Technical Analysis & Verification...")
    
    raw_sources = state.get("raw_sources", [])
    if not raw_sources:
        logger.warning("No raw sources found. Using fallback state.")
        raw_sources_str = "Topic: Modern Multi-Agent State Machine Orchestration in LangGraph and Computer Vision"
    else:
        raw_sources_str = json.dumps(raw_sources[:5], indent=2)

    # If there is critique feedback from a previous revision loop, include it
    critic_review = state.get("critic_review")
    feedback_context = ""
    if critic_review and not critic_review.passed:
        feedback_context = f"\n\nCRITICAL REVISION FEEDBACK TO FIX:\n{critic_review.critique_notes}\nPlease address all deficiencies noted above."

    prompt = f"""
Analyze the following raw technical materials and produce a comprehensive technical analysis:

RAW SCOUTED MATERIALS:
{raw_sources_str}
{feedback_context}

Provide a structured, high-density technical analysis document.
"""

    analysis_output = await llm_router.generate(
        prompt=prompt,
        system_prompt=ANALYST_SYSTEM_PROMPT,
        tier=ModelTier.REASONING,
        temperature=0.4,  # Lower temperature for deterministic, sharp analysis
        max_tokens=2500,
    )

    logger.info("Technical Analysis Completed Successfully.")
    
    return {
        "technical_analysis": analysis_output,
        "status": "ANALYZED",
        "revision_count": state.get("revision_count", 0),
    }
