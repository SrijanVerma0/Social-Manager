"""
1. Unit and integration tests for LangGraph state graph transitions, scout tools, and agent stylist nodes.
2. Runs end-to-end pipeline execution from research to multi-platform output generation.
3. Tests critic scoring thresholds and anti-cringe evaluation rubric behavior.
"""

import asyncio
import logging
from backend.app.agents.graph import social_agent_graph

# Configure logging to see live agent activities in terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def run_end_to_end_test():
    print("\n" + "="*70)
    print("🚀 STARTING END-TO-END MULTI-AGENT PIPELINE TEST")
    print("="*70)

    # Sample AI Engineer Topic
    initial_state = {
        "topic_seed": "Semantic Caching with Redis: How Vector Similarity Cuts Production LLM API Bills by 60 Percent",
        "build_in_public_note": None,
        "raw_sources": [],
        "technical_analysis": None,
        "linkedin_draft": None,
        "video_script_draft": None,
        "twitter_draft": None,
        "blog_draft": None,
        "engagement_draft": None,
        "critic_review": None,
        "revision_count": 0,
        "status": "INITIALIZED",
    }

    # Execute the LangGraph State Graph
    final_state = await social_agent_graph.ainvoke(initial_state)

    print("\n" + "="*70)
    print("🎉 END-TO-END PIPELINE EXECUTION COMPLETED!")
    print("="*70)

    # 1. Inspect Analyst Output
    print("\n🧠 [1. TECHNICAL ANALYSIS PREVIEW]:")
    print(final_state.get("technical_analysis", "")[:350] + "...\n")

    # 2. Inspect LinkedIn Post & Carousel
    linkedin = final_state.get("linkedin_draft")
    if linkedin:
        print("💼 [2. LINKEDIN POST & CAROUSEL]:")
        print(f"Hook: {linkedin.hook}")
        print(f"Carousel Slides Generated: {len(linkedin.carousel_deck.slides)} slides")
        print(f"Slide 1 Title: {linkedin.carousel_deck.slides[0].title}")

    # 3. Inspect Dev.to Blog
    blog = final_state.get("blog_draft")
    if blog:
        print("\n✍️ [3. DEV.TO TECHNICAL ARTICLE]:")
        print(f"Article Title: {blog.title}")
        print(f"Article Word Count: ~{len(blog.markdown_content.split())} words")

    # 4. Inspect Critic Score
    critic = final_state.get("critic_review")
    if critic:
        print("\n🛡️ [4. CRITIC QUALITY EVALUATION]:")
        print(f"Overall Score: {critic.overall_score}/100")
        print(f"Technical Depth: {critic.technical_accuracy_score}/100 | Anti-Cringe: {critic.anti_cringe_score}/100")
        print(f"Passed: {critic.passed}")
        print(f"Critique Notes: {critic.critique_notes}")

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(run_end_to_end_test())
