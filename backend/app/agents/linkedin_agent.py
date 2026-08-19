"""
LinkedIn Stylist Agent.
Loads prompt from backend/app/prompts/linkedin_system_prompt.md
"""

import logging
from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import LinkedInPostDraft

logger = logging.getLogger(__name__)

# Dynamic Prompt Loading from Markdown
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
PROMPT_FILE = PROMPTS_DIR / "linkedin_system_prompt.md"

def load_linkedin_prompt() -> str:
    """Reads the system prompt from markdown file."""
    if not PROMPT_FILE.exists():
        logger.warning("Prompt file not found, falling back to default.")
        return "You are an AI engineer writing short, crisp LinkedIn posts."
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

async def linkedin_node(state: AgentState) -> Dict[str, Any]:
    """Generates structured LinkedIn Post and PDF Carousel slide deck."""
    logger.info("Generating LinkedIn Authority Post & PDF Carousel Outline...")
    
    technical_analysis = state.get("technical_analysis", "")
    system_prompt = load_linkedin_prompt()
    
        # Critic ka feedback agar revision loop chal raha ho
    critic_review = state.get("critic_review")
    feedback_context = ""
    if critic_review and not critic_review.passed:
        feedback_context = f"\n\nCRITICAL FIXES REQUIRED FROM PREVIOUS REJECTION:\n{critic_review.critique_notes}\nFix these issues STRICTLY (cut down length, remove academic jargon)."

    prompt = f"""
Transform the following technical analysis into a punchy, human-like LinkedIn Post and a 5-6 slide Carousel Deck.
Follow all rules in the system prompt strictly (under 150 words, conversational tone, 1-2 sentence paragraphs).

TECHNICAL ANALYSIS:
{technical_analysis}
{feedback_context}
"""


    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        tier=ModelTier.WRITER,
        temperature=0.6,
        response_model=LinkedInPostDraft,
    )

    logger.info("LinkedIn Post and Carousel Draft Generated Successfully.")
    
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
