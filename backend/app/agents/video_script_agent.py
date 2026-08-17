"""
1. 1-2 Min Video Script & Code Walkthrough Generator agent for YouTube Shorts, LinkedIn & X videos.
2. Generates tight teleprompter speaking scripts with timestamps and actionable talking points.
3. Produces a clean, runnable code snippet designed to be shown on screen during video recording.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import VideoScriptDraft

logger = logging.getLogger(__name__)

VIDEO_SCRIPT_SYSTEM_PROMPT = """
You are an expert Short-Form Technical Creator and Senior AI Engineer.
Your job is to convert a deep technical architecture into a high-energy, 60-90 second video recording script and an on-screen code proof.

TARGET AUDIENCE:
Developers, AI Engineers, and Tech Recruiters watching on LinkedIn, X, and YouTube Shorts.

SCRIPT STRUCTURE (Teleprompter Format):
1. [00:00-00:15] HOOK: High-energy problem statement. Start with a common mistake engineers make (e.g. "Stop building naive RAG like this...").
2. [00:15-00:45] ARCHITECTURE / THE "WHY": Clearly explain the architectural shift and why standard solutions fail under production load.
3. [00:45-01:15] CODE WALKTHROUGH: Explain the exact logic that will be visible on screen in the IDE (e.g. "Look at line 12 where we handle state checkpointers...").
4. [01:15-01:30] WRAP UP & CTA: 1-sentence punchy conclusion and call-to-action (e.g. "Drop your thoughts below / Full code in comments").

ON-SCREEN CODE REQUIREMENTS:
- Provide a clean, elegant, runnable Python/LangGraph/OpenCV snippet (20-35 lines max).
- Include clear inline comments highlighting the critical parts mentioned in the script.
"""


async def video_script_node(state: AgentState) -> Dict[str, Any]:
    """
    Video Script Node in the LangGraph workflow.
    Generates 60-90s teleprompter script and screen-ready code for video recording.
    """
    logger.info("Generating 1-2 Min Video Script & Screen Code Kit...")
    
    technical_analysis = state.get("technical_analysis", "")
    
    prompt = f"""
Transform the following technical analysis into a high-impact 60-90 second Video Recording Kit:

TECHNICAL ANALYSIS:
{technical_analysis}

Generate output matching the required VideoScriptDraft schema.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=VIDEO_SCRIPT_SYSTEM_PROMPT,
        tier=ModelTier.WRITER,
        temperature=0.7,
        response_model=VideoScriptDraft,
    )

    logger.info("Video Creator Kit Generated Successfully.")
    
    if isinstance(draft, str):
        try:
            parsed_draft = VideoScriptDraft.model_validate_json(draft)
        except Exception:
            parsed_draft = None
    else:
        parsed_draft = draft

    return {
        "video_script_draft": parsed_draft,
        "status": "VIDEO_SCRIPT_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }
