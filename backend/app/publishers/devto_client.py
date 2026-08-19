"""
Dev.to Article Publisher API Integration.
Publishes structured markdown technical tutorials directly to Dev.to.
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv("backend/.env")
logger = logging.getLogger(__name__)

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")

def post_to_devto(draft_data: dict, publish_live: bool = True) -> str:
    """
    Publishes structured TechnicalArticleDraft JSON to Dev.to.
    
    Args:
        draft_data: Dictionary containing title, subtitle, markdown_content, and tags.
        publish_live: True to publish immediately, False to save in Dev.to Drafts.
    
    Returns:
        Live or Draft URL of the created article.
    """
    if not DEVTO_API_KEY:
        logger.warning("⚠️ Dev.to API Key is missing in .env. Skipping Dev.to publishing.")
        return ""

    logger.info("✍️ Publishing technical article to Dev.to...")
    
    url = "https://dev.to/api/articles"
    headers = {
        "api-key": DEVTO_API_KEY,
        "Content-Type": "application/json"
    }
    
    title = draft_data.get("title", "Technical Deep Dive")
    subtitle = draft_data.get("subtitle", "")
    markdown_body = draft_data.get("markdown_content", "")
    
    # Dev.to supports max 4 tags, lowercase, alphanumeric only, no special chars
    raw_tags = draft_data.get("tags", [])
    clean_tags = [
        "".join(c for c in t.replace("#", "").lower() if c.isalnum())[:20]
        for t in raw_tags if t
    ]
    clean_tags = [t for t in clean_tags if t][:4]
    if not clean_tags:
        clean_tags = ["ai", "backend", "programming", "architecture"]
    
    # Construct complete markdown article
    full_markdown = f"*{subtitle}*\n\n{markdown_body}" if subtitle else markdown_body

    payload = {
        "article": {
            "title": title,
            "published": publish_live,
            "body_markdown": full_markdown,
            "tags": clean_tags,
            "description": subtitle[:150] if subtitle else title[:150]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in (200, 201):
            article_url = response.json().get("url", "")
            logger.info(f"✅ Successfully posted to Dev.to! URL: {article_url}")
            return article_url
        else:
            logger.error(f"❌ Failed to publish to Dev.to: {response.status_code} {response.text}")
            return ""
    except Exception as e:
        logger.error(f"❌ Dev.to Exception: {str(e)}")
        return ""
