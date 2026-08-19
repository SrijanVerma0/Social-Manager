import asyncio
import logging
from backend.app.agents.graph import social_agent_graph

# Logging setup taaki saare agents ka progress dikhe
logging.basicConfig(level=logging.INFO, format="%(message)s")

async def run_test():
    print("\n🚀 Starting E2E Workflow: Scout -> Stylists -> Critic -> Database Saver...\n")
    
    initial_state = {
        "topic": "Why Cursor IDE is better than VS Code for AI Engineering",
        "revision_count": 0
    }
    
    # Run the graph
    final_state = await social_agent_graph.ainvoke(initial_state)
    
    print("\n✅ Workflow Finished Successfully!")
    if final_state.get('critic_review'):
        print(f"🎯 Final Critic Score: {final_state['critic_review'].overall_score}/100")

    print("💾 Check your 'social_manager.db' SQLite file, data save ho gaya hoga!")

if __name__ == "__main__":
    asyncio.run(run_test())
