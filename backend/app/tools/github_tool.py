"""
1. Interfaces with GitHub REST API to fetch trending AI repositories, release notes, and commit activity.
2. Identifies explosive open-source libraries, star velocity, and architectural patterns in trending codebases.
3. Feeds real-world code implementation topics into the content generation pipeline.
"""

from typing import List, Dict, Any, Optional
import requests
from backend.app.core.config import settings


class GithubTrendingTool:
    """
    Scrapes trending and breakthrough open-source AI repositories from GitHub.
    """
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    def search_repositories(
        self,
        query: str = "llm OR agent OR rag stars:>100",
        sort: str = "updated",
        order: str = "desc",
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Searches GitHub for top active AI/LLM repositories.
        
        Args:
            query: GitHub search query string.
            sort: 'stars', 'forks', or 'updated'.
            order: 'desc' or 'asc'.
            max_results: Max repos to return.
        """
        try:
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": max_results,
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"[GithubTrendingTool Error]: Status {response.status_code} - {response.text}")
                return []

            data = response.json()
            repos = []
            for item in data.get("items", []):
                repos.append({
                    "name": item.get("full_name", ""),
                    "url": item.get("html_url", ""),
                    "description": item.get("description", "No description"),
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "language": item.get("language", "Unknown"),
                    "topics": item.get("topics", []),
                    "updated_at": item.get("updated_at", ""),
                })
            return repos

        except Exception as e:
            print(f"[GithubTrendingTool Error]: {str(e)}")
            return []


# Singleton instance
github_tool = GithubTrendingTool()

