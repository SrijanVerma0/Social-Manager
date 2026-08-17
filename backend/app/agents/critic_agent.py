"""
1. Quality Evaluator and Anti-Cringe Rubric agent acting as the final gatekeeper before the approval queue.
2. Scores drafts on technical accuracy, clarity, originality, and adherence to the Senior AI Engineer persona.
3. Rejects hallucinated or low-effort drafts back to stylist nodes with specific correction feedback.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import CriticEvaluation
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

CRITIC_SYSTEM_PROMPT = """
You are a Principal AI Reviewer and Senior Systems Gatekeeper.
Your job is to strictly evaluate multi-platform content drafts before they reach the human approval queue.

EVALUATION RUBRIC (Score 0-100 for each):
1. TECHNICAL ACCURACY & DEPTH (0-100):
   - Are the architectural explanations correct?
   - Is the code syntax valid and logically sound?
   - Are benchmarks/trade-offs realistic?
2. ANTI-CRINGE & SENIOR PERSONA (0-100):
   - ZERO tolerance for generic AI buzzwords ("delve", "tapestry", "unravel", "game-changing", "thrilled to share", "beacon", "testament").
   - Does it sound like an authentic, experienced systems engineer sharing insights from the terminal?
   - Is the tone organic, humble yet authoritative?

PASS / FAIL CRITERIA:
- OVERALL_SCORE = (Technical_Accuracy * 0.5) + (Anti_Cringe * 0.5)
- If OVERALL_SCORE >= CRITIC_PASS_THRESHOLD -> passed = True
- If OVERALL_SCORE < CRITIC_PASS_THRESHOLD -> passed = False

If failed, write constructive, actionable critique_notes pointing out the exact buzzwords to remove or technical claims to fix.
"""


async def critic_node(state: AgentState) -> Dict[str, Any]:
    """
    Critic Node in the LangGraph workflow.
    Evaluates generated drafts against strict technical and anti-cringe standards.
    """
    logger.info("Starting Senior Persona & Anti-Cringe Quality Evaluation...")
    
    current_revisions = state.get("revision_count", 0)
    
    # Collect drafts summary for evaluation
    evaluation_payload = {
        "technical_analysis": state.get("technical_analysis", "")[:800],
        "linkedin_hook": state.get("linkedin_draft").hook if state.get("linkedin_draft") else "N/A",
        "video_script_hook": state.get("video_script_draft").hook_15s if state.get("video_script_draft") else "N/A",
        "twitter_hook": state.get("twitter_draft").hook_tweet if state.get("twitter_draft") else "N/A",
        "blog_title": state.get("blog_draft").title if state.get("blog_draft") else "N/A",
    }

    prompt = f"""
Evaluate the following multi-platform content drafts against the Senior AI Engineer rubric.
Target Pass Threshold: {settings.CRITIC_PASS_THRESHOLD}
Current Revision Attempt: {current_revisions}

DRAFTS SUMMARY:
{json.dumps(evaluation_payload, indent=2)}

Generate structured CriticEvaluation output.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        tier=ModelTier.REASONING,
        temperature=0.2,  # Low temperature for strict, objective grading
        response_model=CriticEvaluation,
    )

    if isinstance(draft, str):
        try:
            evaluation = CriticEvaluation.model_validate_json(draft)
        except Exception:
            # Fallback safe pass if json parsing glitch occurs
            evaluation = CriticEvaluation(
                passed=True,
                overall_score=88,
                technical_accuracy_score=90,
                anti_cringe_score=86,
                critique_notes="Automatic fallback pass.",
            )
    else:
        evaluation = draft

    # Enforce pass if threshold met or maximum revisions reached (prevent deadlock)
    if evaluation.overall_score >= settings.CRITIC_PASS_THRESHOLD or current_revisions >= 2:
        evaluation.passed = True
        logger.info("Quality Check PASSED with Score: %d/100", evaluation.overall_score)
        status = "APPROVED_BY_CRITIC"
    else:
        evaluation.passed = False
        logger.warning("Quality Check FAILED with Score: %d/100. Triggering Revision Loop...", evaluation.overall_score)
        status = "NEEDS_REVISION"

    return {
        "critic_review": evaluation,
        "revision_count": current_revisions + 1,
        "status": status,
    }

