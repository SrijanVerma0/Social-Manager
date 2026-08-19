"""
1. Compiles structured slide deck JSON into modern multi-page PDF carousels tailored for LinkedIn uploads.
2. Injects dynamic text, syntax-highlighted code, and slide counters into an HTML/CSS layout rendered via Playwright.
3. Generates sleek dark-mode slides that drive massive engagement and dwell time on LinkedIn algorithms.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from backend.app.schemas.agent_schema import CarouselDeck

logger = logging.getLogger(__name__)

# Template & Output Directories
VISUAL_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = VISUAL_DIR / "templates"
OUTPUT_DIR = VISUAL_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class CarouselGenerator:
    """
    Renders structured CarouselDeck data into high-resolution LinkedIn PDF Carousels.
    """
    def __init__(self):
        self.jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        self.template = self.jinja_env.get_template("carousel_template.html")

    async def generate_pdf(
        self,
        deck: CarouselDeck,
        tag: str = "AI ENGINEERING",
        filename: Optional[str] = None,
    ) -> str:
        """
        Renders HTML from CarouselDeck and compiles into a multi-page PDF using Playwright.
        
        Returns:
            Absolute file path of the generated PDF.
        """
        logger.info("🎨 Compiling PDF Carousel for topic: '%s' (%d slides)...", deck.deck_title, len(deck.slides))
        
        # 1. Render Dynamic HTML using Jinja2
        html_content = self.template.render(
            deck_title=deck.deck_title,
            tag=tag,
            slides=deck.slides,
            total_slides=len(deck.slides),
        )

        # 2. Output PDF Path
        safe_title = "".join(c for c in deck.deck_title if c.isalnum() or c in (" ", "_", "-")).rstrip()
        safe_title = safe_title.replace(" ", "_").lower()[:40]
        if not filename:
            filename = f"carousel_{safe_title}.pdf"
        
        output_pdf_path = OUTPUT_DIR / filename

        # 3. Headless Chrome PDF Compilation via Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Viewport set to 1080x1350 (4:5 aspect ratio)
            page = await browser.new_page(viewport={"width": 1080, "height": 1350})
            
            # Load rendered HTML
            await page.set_content(html_content, wait_until="networkidle")
            
            # Compile to PDF
            await page.pdf(
                path=str(output_pdf_path),
                width="1080px",
                height="1350px",
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
            )
            
            await browser.close()

        logger.info("✅ PDF Carousel Generated Successfully at: %s", str(output_pdf_path))
        return str(output_pdf_path)


# Singleton instance
carousel_generator = CarouselGenerator()

