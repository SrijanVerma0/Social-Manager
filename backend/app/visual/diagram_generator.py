"""
1. Renders Mermaid diagram syntax strings into high-resolution PNG architecture charts.
2. Uses Playwright headless Chromium with Mermaid.js to compile flowcharts, sequence diagrams, and system designs.
3. Produces high-contrast dark-mode graphics ready for Twitter thread cards and LinkedIn technical deep-dives.
"""

import logging
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

VISUAL_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = VISUAL_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class DiagramGenerator:
    """
    Converts Mermaid diagram code into crisp dark-mode PNG images.
    """

    async def render_mermaid_to_png(
        self,
        mermaid_code: str,
        filename: Optional[str] = None,
        width: int = 1200,
        height: int = 800,
    ) -> str:
        """
        Renders Mermaid graph code to a standalone PNG image using Mermaid.js inside Playwright.
        
        Returns:
            Absolute file path to the generated PNG image.
        """
        if not filename:
            filename = "architecture_diagram.png"

        output_png_path = OUTPUT_DIR / filename
        logger.info("📐 Rendering Mermaid diagram to PNG: %s", str(output_png_path))

        html_canvas = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 40px;
                    background: #060a14;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }}
                .mermaid {{
                    background: #0b1120;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 16px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'dark',
                    themeVariables: {{
                        darkMode: true,
                        background: '#0b1120',
                        primaryColor: '#6366f1',
                        primaryTextColor: '#f8fafc',
                        primaryBorderColor: '#818cf8',
                        lineColor: '#38bdf8',
                        secondaryColor: '#06b6d4',
                        tertiaryColor: '#1e293b'
                    }}
                }});
            </script>
        </body>
        </html>
        """

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": width, "height": height})
            await page.set_content(html_canvas, wait_until="networkidle")
            
            # Wait for Mermaid to render SVG
            await page.wait_for_selector(".mermaid svg", timeout=10000)
            
            # Take clean screenshot of the diagram card
            element = await page.query_selector(".mermaid")
            if element:
                await element.screenshot(path=str(output_png_path))
            else:
                await page.screenshot(path=str(output_png_path))

            await browser.close()

        logger.info("✅ Architecture Diagram PNG Saved at: %s", str(output_png_path))
        return str(output_png_path)


# Singleton instance
diagram_generator = DiagramGenerator()
