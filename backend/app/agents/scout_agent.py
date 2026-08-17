"""
1. Autonomous Scout agent responsible for gathering daily breakthrough AI news, papers, and trending repos.
2. Invokes Tavily search, arXiv paper extraction, and GitHub API tools to discover high-signal topics.
3. Filters out marketing hype and extracts raw technical facts, benchmarks, and architectural novelties.
"""

import logging
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.llm_router import llm_router, ModelTier
from backend.app.tools.tavily_tool import tavily_tool
from backend.app.tools.arxiv_tool import arxiv_tool
from backend.app.tools.github_tool import github_tool

logger = logging.getLogger(__name__)

SCOUT_SYSTEM_PROMPT = """
You are a Lead AI Research Scout for a Senior AI Systems Engineer.
Your job is to identify high-signal, breakthrough engineering topics from raw sources.

STRICT FILTERING RULES:
1. Reject generic marketing hype, beginner prompt-engineering tips, or toy 10-line chatbots.
2. Discard non-English repositories or papers without clear technical documentation.
3. Prioritize:
   - Novel Agent State Architectures (LangGraph, Multi-Agent routing, memory checkpointers)
   - Computer Vision & Multimodal (OpenCV video pipelines, Vision-Language Models, real-time spatial AI)
   - Inference Optimization (vLLM, Speculative Decoding, Quantization, CUDA kernels)
   - Advanced RAG (GraphRAG, Chunking, Hybrid Vector-Graph Retrieval)
   - Reasoning Models (DeepSeek R1 architectures, Test-Time Compute, Reinforcement Learning)

Return a concise, high-density bulleted extraction of the core technical novelty, architectural claims, and verifiable facts.
"""


async def scout_node(state: AgentState) -> Dict[str, Any]:
    """
    Scout Node in the LangGraph workflow.
    Gathers raw materials from arXiv, Tavily, and GitHub, then filters high-signal topics.
    """
    logger.info("Initiating AI Research & Trend Ingestion...")
    
    raw_sources = []
    topic_seed = state.get("topic_seed")
    build_in_public = state.get("build_in_public_note")

    # Priority 1: User's personal Build-in-Public note
    if build_in_public:
        logger.info("Processing personal Build-in-Public note: %s...", build_in_public[:60])
        raw_sources.append({
            "source_type": "build_in_public",
            "title": "Personal Engineering Milestone",
            "content": build_in_public,
        })
        # Enrich with Tavily search for related architectures/benchmarks
        enrich_results = tavily_tool.search(f"{build_in_public} architecture benchmarks", max_results=2)
        raw_sources.extend(enrich_results)

    # Priority 2: User provided custom topic seed
    elif topic_seed:
        logger.info("Researching targeted topic: %s...", topic_seed)
        tavily_results = tavily_tool.search(f"{topic_seed} AI architecture technical breakdown", max_results=3)
        arxiv_results = arxiv_tool.search_papers(query=f"{topic_seed} OR cat:cs.CV", max_results=2)
        raw_sources.extend(tavily_results)
        raw_sources.extend(arxiv_results)

    # Priority 3: Fully autonomous daily scout discovery
    else:
        logger.info("Running autonomous daily scan across arXiv (AI, CL, CV), Tavily, and GitHub...")
        arxiv_papers = arxiv_tool.search_papers(query="cat:cs.AI OR cat:cs.CL OR cat:cs.CV", max_results=3)
        tavily_news = tavily_tool.search("Latest open source LLM agent architecture computer vision breakthrough 2026", max_results=2)
        github_repos = github_tool.search_repositories(query="llm OR agent OR opencv stars:>200", max_results=2)
        
        raw_sources.extend(arxiv_papers)
        raw_sources.extend(tavily_news)
        raw_sources.extend(github_repos)

    logger.info("Gathered %d candidate sources.", len(raw_sources))
    
    return {
        "raw_sources": raw_sources,
        "status": "SCOUTED",
        "revision_count": state.get("revision_count", 0),
    }
