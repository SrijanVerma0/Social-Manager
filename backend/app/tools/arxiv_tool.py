"""
1. Queries the official arXiv API for newly published AI, Machine Learning (cs.AI, cs.LG, cs.CL) research papers.
2. Parses paper titles, authors, abstract summaries, and PDF download links for technical extraction.
3. Provides cutting-edge research material to position your personal brand at the forefront of AI innovation.
"""

from typing import List, Dict, Any, Optional
import arxiv


class ArxivScoutTool:
    """
    Scrapes and filters latest AI / Machine Learning research papers from arXiv.
    """
    def __init__(self):
        self.client = arxiv.Client()

    def search_papers(
        self,
        query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV",
        max_results: int = 5,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate,
    ) -> List[Dict[str, Any]]:
        """
        Fetches latest research papers matching the technical domain query.
        
        Args:
            query: arXiv search query or category (e.g. 'LLM reasoning agents' or 'cat:cs.AI').
            max_results: Max number of recent papers to retrieve.
            sort_by: Default to latest submitted papers.
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_by,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []
            for result in self.client.results(search):
                papers.append({
                    "title": result.title.replace("\n", " ").strip(),
                    "authors": [author.name for author in result.authors[:4]],
                    "summary": result.summary.replace("\n", " ").strip(),
                    "published": result.published.strftime("%Y-%m-%d"),
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "entry_id": result.entry_id,
                })
            return papers

        except Exception as e:
            print(f"[ArxivScoutTool Error]: {str(e)}")
            return []


# Singleton instance
arxiv_tool = ArxivScoutTool()
