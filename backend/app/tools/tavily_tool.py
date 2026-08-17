"""
1. Wraps Tavily Search API for AI-optimized web queries, news aggregation, and official documentation lookups.
2. Extracts clean markdown content while filtering out boilerplate navigation and advertising noise.
3. Enables the Scout agent to search specific technical domains (e.g. HuggingFace, OpenAI, arXiv, Anthropic).
"""

from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from backend.app.core.config import settings


class TavilySearchTool:
    """
    Search tool providing noise-free web research for AI trend discovery.
    """
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes an AI-optimized search query.
        
        Args:
            query: The research search query.
            search_depth: "basic" or "advanced" (advanced performs deeper page parsing).
            max_results: Max number of high-relevance sources to return.
            include_domains: Specific domains to focus on (e.g. ['huggingface.co', 'arxiv.org']).
        """
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains or [],
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", "No Title"),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0.0),
                })
            return results

        except Exception as e:
            print(f"[TavilySearchTool Error]: {str(e)}")
            return []


# Singleton instance
tavily_tool = TavilySearchTool()
