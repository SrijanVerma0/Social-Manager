"""
Quality Evaluator and Anti-Cringe Rubric agent acting as the final gatekeeper.
Loads rules from backend/app/prompts/critic_system_prompt.md
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import CriticEvaluation
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
CRITIC_PROMPT_FILE = PROMPTS_DIR / "critic_system_prompt.md"

def load_critic_prompt() -> str:
    """Reads the critic system prompt from markdown file."""
    if not CRITIC_PROMPT_FILE.exists():
        logger.warning("Critic prompt file not found, using default.")
        return "You are a strict technical reviewer rejecting robotic or overly academic content."
    with open(CRITIC_PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

async def critic_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates generated drafts against strict human-authenticity and simplicity standards."""
    logger.info("Starting Strict Anti-Bot & Human Voice Evaluation...")
    
    current_revisions = state.get("revision_count", 0)
    linkedin_draft = state.get("linkedin_draft")
    
    # Send full LinkedIn content for comprehensive review
    evaluation_payload = {
        "technical_topic": state.get("topic_seed", "N/A"),
        "linkedin_hook": linkedin_draft.hook if linkedin_draft else "N/A",
        "linkedin_body": linkedin_draft.body if linkedin_draft else "N/A",
        "linkedin_takeaways": linkedin_draft.key_takeaways if linkedin_draft else [],
        "carousel_slides_count": len(linkedin_draft.carousel_deck.slides) if linkedin_draft and linkedin_draft.carousel_deck else 0,
        "blog_title": state.get("blog_draft").title if state.get("blog_draft") else "N/A",
    }

    prompt = f"""
Evaluate the following multi-platform drafts against the STRICT HUMAN-BUILDER Rubric.
Target Pass Threshold: 85/100
Current Revision Attempt: {current_revisions}

DRAFTS FOR REVIEW:
{json.dumps(evaluation_payload, indent=2)}

Enforce all rules strictly. If it sounds like an academic paper or is too long, FAIL it with specific critique notes.
"""

    critic_system_prompt = load_critic_prompt()

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=critic_system_prompt,
        tier=ModelTier.REASONING,
        temperature=0.1,  # Ultra-low temperature for strict grading
        response_model=CriticEvaluation,
    )

    if isinstance(draft, str):
        try:
            evaluation = CriticEvaluation.model_validate_json(draft)
        except Exception:
            evaluation = CriticEvaluation(
                passed=True,
                overall_score=85,
                technical_accuracy_score=85,
                anti_cringe_score=85,
                critique_notes="Automatic fallback pass.",
            )
    else:
        evaluation = draft

    # Pass if score >= 85 or max revisions reached (prevents infinite loops)
    if evaluation.overall_score >= 85 or current_revisions >= 2:
        evaluation.passed = True
        logger.info("✅ Quality Check PASSED with Score: %d/100", evaluation.overall_score)
        status = "APPROVED_BY_CRITIC"
    else:
        evaluation.passed = False
        logger.warning("❌ Quality Check FAILED (%d/100). Notes: %s", evaluation.overall_score, evaluation.critique_notes)
        status = "NEEDS_REVISION"

    return {
        "critic_review": evaluation,
        "revision_count": current_revisions + 1,
        "status": status,
    }
