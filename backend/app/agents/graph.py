"""
1. Builds and compiles the LangGraph StateGraph connecting Scout, Analyst, Stylists, and Critic agents.
2. Defines conditional routing edges based on critic quality scores and platform generation targets.
3. Exposes an async invocation interface used by background schedulers and API trigger endpoints.
"""

import asyncio
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from backend.app.agents.state import AgentState
from backend.app.agents.scout_agent import scout_node
from backend.app.agents.analyst_agent import analyst_node
from backend.app.agents.linkedin_agent import linkedin_node
from backend.app.agents.blog_agent import blog_node
from backend.app.agents.critic_agent import critic_node
from backend.app.agents.db_saver_agent import save_to_db_node


logger = logging.getLogger(__name__)


async def parallel_stylists_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes active platform stylists (LinkedIn + Dev.to Blog) concurrently in parallel.
    """
    logger.info("⚡ Executing LinkedIn & Dev.to Blog Agents concurrently in parallel...")
    
    # Run ONLY LinkedIn and Blog agents in parallel (saves maximum tokens)
    results = await asyncio.gather(
        linkedin_node(state),
        blog_node(state),
    )

    combined_state_update = {}
    for res in results:
        combined_state_update.update(res)

    logger.info("✅ LinkedIn & Dev.to Drafts Generated Successfully!")
    return combined_state_update


def should_revise(state: AgentState) -> Literal["stylists", "__end__"]:
    """
    Conditional edge deciding whether to route back for revision or finish.
    """
    critic_review = state.get("critic_review")
    revision_count = state.get("revision_count", 0)

    if critic_review and critic_review.passed:
        logger.info("🎉 Workflow Complete: Content Approved by Critic Gatekeeper!")
        return "save_to_db"

    if revision_count >= 3:
        logger.warning("⚠️ Max Revisions reached. Forcing completion to avoid infinite loop.")
        return "save_to_db"

    logger.info("🔄 Routing back to Stylists for Revision Loop (Attempt %d)...", revision_count)
    return "stylists"


def build_social_manager_graph():
    """
    Constructs and compiles the complete multi-agent LangGraph workflow.
    """
    builder = StateGraph(AgentState)

    # 1. Add Nodes
    builder.add_node("scout", scout_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("stylists", parallel_stylists_node)
    builder.add_node("critic", critic_node)
    builder.add_node("save_to_db", save_to_db_node)

    # 2. Define Linear Edges
    builder.add_edge(START, "scout")
    builder.add_edge("scout", "analyst")
    builder.add_edge("analyst", "stylists")
    builder.add_edge("stylists", "critic")
    builder.add_edge("save_to_db", END)

    # 3. Define Conditional Cyclic Edge (The Self-Correction Loop)
    builder.add_conditional_edges(
        "critic",
        should_revise,
        {
            "stylists": "stylists",
            "save_to_db": "save_to_db",
            END: END,
        }
    )

    # Compile Graph
    graph = builder.compile()
    return graph


# Export compiled graph instance
social_agent_graph = build_social_manager_graph()