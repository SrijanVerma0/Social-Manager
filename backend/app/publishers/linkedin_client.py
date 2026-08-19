"""
LinkedIn Publisher API Integration.
Uses the modern LinkedIn /rest/posts API to publish text & rich PDF document carousels.
"""

import os
import requests
import logging
from dotenv import load_dotenv
from backend.app.schemas.agent_schema import CarouselDeck
from backend.app.visual.carousel_generator import carousel_generator

load_dotenv("backend/.env")
logger = logging.getLogger(__name__)

LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_VERSION = "202607"  # Consistent API version string

def get_linkedin_urn():
    """Fetches the User's URN from the LinkedIn Profile API."""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return f"urn:li:person:{response.json().get('sub')}"
    else:
        logger.error(f"Failed to fetch LinkedIn URN: {response.text}")
        return None

def upload_linkedin_document(urn: str, pdf_path: str, title: str) -> str:
    """Registers and uploads a PDF document using the LinkedIn /rest/documents API."""
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found at: {pdf_path}")
        return ""
    
    # 1. Initialize Document Upload
    init_url = "https://api.linkedin.com/rest/documents?action=initializeUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    init_payload = {
        "initializeUploadRequest": {
            "owner": urn
        }
    }
    
    res = requests.post(init_url, headers=headers, json=init_payload)
    if res.status_code != 200:
        logger.error(f"❌ Failed to initialize document upload: {res.text}")
        return ""
        
    data = res.json().get("value", {})
    document_urn = data.get("document")
    upload_url = data.get("uploadUrl")
    
    if not document_urn or not upload_url:
        logger.error("❌ Document URN or Upload URL missing in LinkedIn response.")
        return ""
        
    # 2. Upload raw PDF binary (No auth header needed for S3 presigned URL)
    logger.info(f"📄 Uploading PDF Carousel ({pdf_path})...")
    with open(pdf_path, "rb") as f:
        upload_res = requests.put(
            upload_url,
            data=f,
            headers={
                "Content-Type": "application/octet-stream"
            }
        )
        
    if upload_res.status_code in (200, 201, 204):
        logger.info(f"✅ PDF successfully uploaded! Document: {document_urn}")
        return document_urn
    else:
        logger.error(f"❌ Failed to upload PDF binary: {upload_res.status_code} {upload_res.text}")
        return ""


async def post_to_linkedin(draft_data: dict) -> str:
    """Posts the parsed LinkedInPostDraft JSON to LinkedIn (attaching PDF Carousel if available)."""
    if not LINKEDIN_TOKEN:
        logger.error("❌ LinkedIn Access Token is missing in .env!")
        return ""

    urn = get_linkedin_urn()
    if not urn:
        return ""

    logger.info("💼 Preparing LinkedIn Post...")
    
    hook = draft_data.get("hook", "")
    body = draft_data.get("body", "")
    raw_takeaways = draft_data.get("key_takeaways", [])
    takeaways = "\n".join([f"• {t.replace('(', ' - ').replace(')', '')}" for t in raw_takeaways])

    hashtags = " ".join(draft_data.get("hashtags", []))
    
    post_text = f"{hook}\n\n{body}\n\n{takeaways}\n\n{hashtags}".strip()
    if not post_text:
        post_text = "Automated Post from Social Manager"
        
    carousel_deck_data = draft_data.get("carousel_deck")
    asset_urn = None
    deck_title = "Technical Visual Guide"
    
    if carousel_deck_data:
        try:
            deck = CarouselDeck.model_validate(carousel_deck_data)
            deck_title = deck.deck_title or deck_title
            logger.info("🎨 Rendering PDF Carousel slides via Playwright...")
            pdf_path = await carousel_generator.generate_pdf(deck=deck)
            if pdf_path and os.path.exists(pdf_path):
                asset_urn = upload_linkedin_document(urn, pdf_path, deck_title)
        except Exception as e:
            logger.error(f"⚠️ Carousel generation/upload failed, falling back to text-only: {str(e)}")

    post_url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    payload = {
        "author": urn,
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED"
    }

    if asset_urn:
        payload["content"] = {
            "media": {
                "title": deck_title,
                "id": asset_urn
            }
        }

    response = requests.post(post_url, headers=headers, json=payload)
    
    if response.status_code == 201:
        post_id = response.headers.get("x-restli-id", "Success")
        logger.info(f"✅ Successfully posted to LinkedIn! Post ID: {post_id}")
        return post_id
    else:
        logger.error(f"❌ Failed to publish to LinkedIn: {response.status_code} {response.text}")
        return ""