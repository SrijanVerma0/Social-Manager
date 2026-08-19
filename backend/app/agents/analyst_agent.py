"""
Technical Analyst agent that extracts practical developer insights from raw data.
Loads prompt from backend/app/prompts/analyst_system_prompt.md
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
ANALYST_PROMPT_FILE = PROMPTS_DIR / "analyst_system_prompt.md"

def load_analyst_prompt() -> str:
    """Reads the analyst system prompt from markdown file."""
    if not ANALYST_PROMPT_FILE.exists():
        logger.warning("Analyst prompt file not found, using default.")
        return "You are a practical AI engineer extracting clean system design lessons."
    with open(ANALYST_PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

async def analyst_node(state: AgentState) -> Dict[str, Any]:
    """Synthesizes raw candidate sources into practical developer architecture insights."""
    logger.info("Starting Practical Systems Analysis & Verification...")
    
    raw_sources = state.get("raw_sources", [])
    if not raw_sources:
        logger.warning("No raw sources found. Using fallback state.")
        raw_sources_str = "Topic: GraphRAG vs Vector Search in Production Multi-Agent Systems"
    else:
        raw_sources_str = json.dumps(raw_sources[:4], indent=2)

    critic_review = state.get("critic_review")
    feedback_context = ""
    if critic_review and not critic_review.passed:
        feedback_context = f"\n\nCRITICAL REVISION FEEDBACK TO FIX:\n{critic_review.critique_notes}\nPlease address all deficiencies noted above."

    prompt = f"""
Analyze the following raw technical materials and produce a practical, developer-friendly system design analysis:

RAW SCOUTED MATERIALS:
{raw_sources_str}
{feedback_context}

Follow all rules in the system prompt strictly (zero academic math, simple whiteboard explanation).
"""

    analyst_system_prompt = load_analyst_prompt()

    analysis_output = await llm_router.generate(
        prompt=prompt,
        system_prompt=analyst_system_prompt,
        tier=ModelTier.REASONING,
        temperature=0.3,
        max_tokens=2000,
    )

    logger.info("Practical Technical Analysis Completed Successfully.")
    
    return {
        "technical_analysis": analysis_output,
        "status": "ANALYZED",
        "revision_count": state.get("revision_count", 0),
    }
