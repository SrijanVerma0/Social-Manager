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

import os
from pathlib import Path

def load_blog_prompt() -> str:
    """Loads the dynamic Dev.to/Medium blog system prompt from the markdown file."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "blog_system_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "You are an expert software engineer writing concise, high-signal developer guides."


async def blog_node(state: AgentState) -> Dict[str, Any]:
    """
    Longform Blog Node in the LangGraph workflow.
    Generates structured, lightweight 600-900 word markdown tutorial for Dev.to and Medium.
    """
    logger.info("Generating Lightweight Technical Guide (Dev.to / Medium)...")
    
    technical_analysis = state.get("technical_analysis", "")
    system_prompt = load_blog_prompt()
    
    prompt = f"""
Write a concise, high-impact 600-900 word practical technical guide based on the following analysis:

TECHNICAL ANALYSIS:
{technical_analysis}

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
# TITLE: <Punchy, High-Authority Technical Title>
## SUBTITLE: <Clean 1-Sentence Value Proposition>
**TAGS:** ai, backend, softwareengineering, systemdesign

<Write the crisp 600-900 word Markdown article with headers, short paragraphs, and a clean Python code snippet>
"""

    draft_text = await llm_router.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        tier=ModelTier.WRITER,
        temperature=0.5,
        max_tokens=2000,  # Lightweight token limit (saves 50%+ tokens)
    )

    logger.info("Technical Article Generated Successfully.")
    
    # Clean extraction of Title, Subtitle, Tags, and Pure Markdown Body
    title = state.get("topic_seed", "Technical Deep Dive")
    subtitle = "A practical engineering guide"
    tags = ["ai", "backend", "softwareengineering", "systemdesign"]
    clean_markdown = draft_text.strip()
    
    # If LLM returned raw JSON string, extract the markdown_content cleanly
    if clean_markdown.startswith("{") and "markdown_content" in clean_markdown:
        try:
            import json, re
            # Clean invalid escape sequences in JSON string
            cleaned_json = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', clean_markdown)
            data = json.loads(cleaned_json, strict=False)
            title = data.get("title", title)
            subtitle = data.get("subtitle", subtitle)
            clean_markdown = data.get("markdown_content", clean_markdown)
            tags = data.get("tags", tags)
        except Exception:
            # Regex extraction for markdown_content field
            import re
            m = re.search(r'"markdown_content"\s*:\s*"(.*)"\s*,\s*"tags"', clean_markdown, re.DOTALL)
            if m:
                clean_markdown = m.group(1).encode().decode('unicode-escape')

    # Standard Markdown header extraction
    lines = clean_markdown.splitlines()
    body_start_idx = 0
    
    for idx, line in enumerate(lines[:10]):
        stripped = line.strip()
        if stripped.startswith("# TITLE:") or stripped.startswith("# Title:"):
            title = stripped.split(":", 1)[1].strip()
            body_start_idx = max(body_start_idx, idx + 1)
        elif stripped.startswith("## SUBTITLE:") or stripped.startswith("## Subtitle:"):
            subtitle = stripped.split(":", 1)[1].strip()
            body_start_idx = max(body_start_idx, idx + 1)
        elif stripped.startswith("**TAGS:**") or stripped.startswith("TAGS:"):
            tag_str = stripped.split(":", 1)[1].replace("*", "").strip()
            tags = [t.strip() for t in tag_str.split(",") if t.strip()]
            body_start_idx = max(body_start_idx, idx + 1)

    # Remaining lines form the true markdown body
    if body_start_idx > 0:
        clean_markdown = "\n".join(lines[body_start_idx:]).strip()

    parsed_draft = TechnicalArticleDraft(
        title=title,
        subtitle=subtitle,
        markdown_content=clean_markdown,
        tags=tags
    )

    return {
        "blog_draft": parsed_draft,
        "status": "BLOG_DRAFTED",
        "revision_count": state.get("revision_count", 0),
    }

