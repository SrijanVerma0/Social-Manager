"""
1. X (Twitter) Thread Master agent that breaks complex AI engineering topics into punchy 4-7 tweet threads.
2. Formats hook tweets, diagram placeholders, code snippets, and concise summaries within 280-character constraints.
3. Optimizes threads for high virality among AI founders, researchers, and senior software engineers.
"""

import json
import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.schemas.agent_schema import TwitterThreadDraft

logger = logging.getLogger(__name__)

TWITTER_SYSTEM_PROMPT = """
You are a High-Signal AI Systems Engineer and Researcher writing organically on X (Twitter).
Your tone is authentic, peer-to-peer, technical, and curiosity-driven.

DYNAMIC THREAD GUIDELINES:
1. TWEET 1 (HOOK): 
   - State a contrarian insight, an unexpected debugging result, or a latency/VRAM benchmark discovery.
   - Use dynamic, natural transitions to the thread. Vary the ending organically (e.g. "Here's what happened under the hood:", "The 3-step architecture we landed on 🧵", "Breaking down the latency numbers:").
   - NEVER use the exact same repetitive formula or predictable bot phrases.
2. TWEETS 2 to N-1:
   - Deliver high-density engineering value with code logic, architecture transitions, and trade-offs.
   - Strictly under 280 characters per tweet.
   - Use clean spacing, concise bullet points, and code/math references.
3. CODE CARD SNIPPET:
   - Provide a clean 10-15 line Python/LangGraph snippet for visual card rendering.
4. FINAL TWEET:
   - Practical takeaway + a genuine question to invite technical discussion from fellow engineers.

ANTI-BOT RULES:
- NO cliché hype words ("unravel", "deep dive", "revolutionize").
- Write like a real senior builder sharing findings from their terminal.
"""



async def twitter_node(state: AgentState) -> Dict[str, Any]:
    """
    Twitter Stylist Node in the LangGraph workflow.
    Generates structured 4-7 tweet thread and code snapshot card.
    """
    logger.info("Generating X (Twitter) Technical Thread...")
    
    technical_analysis = state.get("technical_analysis", "")
    
    prompt = f"""
Transform the following technical analysis into a high-signal X (Twitter) Thread:

TECHNICAL ANALYSIS:
{technical_analysis}

Generate output matching the TwitterThreadDraft schema.
"""

    draft = await llm_router.generate(
        prompt=prompt,
        system_prompt=TWITTER_SYSTEM_PROMPT,
        tier=ModelTier.WRITER,
        temperature=0.7,
        response_model=TwitterThreadDraft,
    )

    logger.info("Twitter Thread Generated Successfully.")
    
    if isinstance(draft, str):
        try:
            parsed_draft = TwitterThreadDraft.model_validate_json(draft)
        except Exception:
            parsed_draft = None
    else:
        parsed_draft = draft

    return {
        "twitter_draft": parsed_draft,
        "status": "TWITTER_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }


