import os
from pathlib import Path

# Mapping of file paths to their 3-line explanatory comments/docstrings
FILE_STRUCTURE = {
    # Backend Core & Config
    "backend/requirements.txt": (
        "# 1. Lists all required Python dependencies for FastAPI, LangGraph, LiteLLM, SQLAlchemy, and Playwright.\n"
        "# 2. Ensures consistent environment setup across local development and production deployments.\n"
        "# 3. Maintained with pinned version constraints to prevent breaking dependency conflicts."
    ),
    "backend/.env.example": (
        "# 1. Template for required environment variables and API keys (OpenRouter, Tavily, Telegram, Social APIs).\n"
        "# 2. Never commit actual secret keys; copy this file to '.env' and fill in your private credentials.\n"
        "# 3. Loaded securely at startup by backend/app/core/config.py using Pydantic BaseSettings."
    ),
    "backend/app/__init__.py": (
        '"""\n'
        "1. Initializes the core FastAPI application package.\n"
        "2. Exposes core package-level metadata and initialization logic.\n"
        "3. Marks the app directory as an importable Python module.\n"
        '"""\n'
    ),
    "backend/app/main.py": (
        '"""\n'
        "1. Entry point for the FastAPI server; initializes CORS, middleware, and API router mounting.\n"
        "2. Starts and stops background workers (APScheduler, Telegram Bot polling) via lifespan events.\n"
        "3. Exposes health check endpoints and serves the REST API for the Next.js frontend.\n"
        '"""\n'
    ),
    "backend/app/core/__init__.py": (
        '"""\n'
        "1. Core application configuration and infrastructure module.\n"
        "2. Encapsulates environment settings, security routines, and database lifecycle management.\n"
        "3. Provides singleton application settings accessible throughout the codebase.\n"
        '"""\n'
    ),
    "backend/app/core/config.py": (
        '"""\n'
        "1. Defines application settings using Pydantic BaseSettings to parse environment variables.\n"
        "2. Manages API keys (OpenRouter, Tavily, LinkedIn, Twitter, Telegram) and database connection strings.\n"
        "3. Validates configuration on application startup to fail fast on missing required credentials.\n"
        '"""\n'
    ),
    "backend/app/core/database.py": (
        '"""\n'
        "1. Configures SQLAlchemy engine, session factory (sessionmaker), and declarative base for ORM.\n"
        "2. Supports SQLite for local zero-config development and PostgreSQL for production.\n"
        "3. Provides the 'get_db' dependency function for injecting database sessions into FastAPI routes.\n"
        '"""\n'
    ),

    # Database Models
    "backend/app/models/__init__.py": (
        '"""\n'
        "1. Database models package exporting all SQLAlchemy ORM entity definitions.\n"
        "2. Ensures all model classes are imported for Alembic migrations and Base.metadata registration.\n"
        "3. Centralizes data model imports across the backend application.\n"
        '"""\n'
    ),
    "backend/app/models/post.py": (
        '"""\n'
        "1. SQLAlchemy ORM model representing generated posts across all target social platforms.\n"
        "2. Tracks post content, platform type (LinkedIn/X/Devto/Medium), approval status, and scheduled time.\n"
        "3. Stores visual asset paths (PDF carousels, images) and live published URLs / platform IDs.\n"
        '"""\n'
    ),
    "backend/app/models/campaign.py": (
        '"""\n'
        "1. SQLAlchemy model grouping related multi-platform posts generated from a single topic or scout run.\n"
        "2. Stores the raw technical summary, source citations (arXiv, GitHub, Tavily), and critic evaluation score.\n"
        "3. Maintains relationships between the parent research topic and child platform-specific post entities.\n"
        '"""\n'
    ),

    # Pydantic Schemas (DTOs)
    "backend/app/schemas/__init__.py": (
        '"""\n'
        "1. Pydantic schemas package for request validation and response serialization (DTOs).\n"
        "2. Ensures strict type-safety across FastAPI API routes and agent state transitions.\n"
        "3. Bridges external JSON payloads with internal Python domain models.\n"
        '"""\n'
    ),
    "backend/app/schemas/post_schema.py": (
        '"""\n'
        "1. Pydantic models for Post CRUD operations, status updates (Approve, Edit, Reject), and schedule requests.\n"
        "2. Defines validation rules for platform-specific character limits, thread arrays, and carousel metadata.\n"
        "3. Serializes database Post models into clean JSON responses for the frontend dashboard.\n"
        '"""\n'
    ),
    "backend/app/schemas/agent_schema.py": (
        '"""\n'
        "1. Pydantic schemas defining structured outputs from LLM agent nodes (e.g. SlideDeckSchema, TweetThreadSchema).\n"
        "2. Enforces schema validation on model outputs to guarantee reliable JSON parsing from OpenRouter models.\n"
        "3. Structures critic evaluation results (technical depth score, anti-cringe check, feedback notes).\n"
        '"""\n'
    ),

    # LangGraph & Multi-Agent Team
    "backend/app/agents/__init__.py": (
        '"""\n'
        "1. Multi-agent orchestration package powering autonomous research, content generation, and evaluation.\n"
        "2. Contains individual specialized agent nodes, state definitions, and LLM provider routing logic.\n"
        "3. Compiles the modular LangGraph workflow for executing autonomous content pipelines.\n"
        '"""\n'
    ),
    "backend/app/agents/state.py": (
        '"""\n'
        "1. Defines the 'AgentState' TypedDict that acts as the central blackboard memory passed across LangGraph nodes.\n"
        "2. Holds raw scraped articles, validated technical summaries, platform drafts, visual metadata, and critic reviews.\n"
        "3. Ensures immutable and observable state updates throughout the multi-agent graph execution cycle.\n"
        '"""\n'
    ),
    "backend/app/agents/llm_router.py": (
        '"""\n'
        "1. Implements multi-tier LLM routing via OpenRouter to optimize cost, latency, and reasoning capability.\n"
        "2. Routes extraction and scraping tasks to fast/economic models (DeepSeek-V3, Claude 3.5 Haiku).\n"
        "3. Routes high-stakes architectural analysis and senior tone crafting to flagship models (Claude 3.5 Sonnet, GPT-4o).\n"
        '"""\n'
    ),
    "backend/app/agents/graph.py": (
        '"""\n'
        "1. Builds and compiles the LangGraph StateGraph connecting Scout, Analyst, Stylists, and Critic agents.\n"
        "2. Defines conditional routing edges based on critic quality scores and platform generation targets.\n"
        "3. Exposes an async invocation interface used by background schedulers and API trigger endpoints.\n"
        '"""\n'
    ),
    "backend/app/agents/scout_agent.py": (
        '"""\n'
        "1. Autonomous Scout agent responsible for gathering daily breakthrough AI news, papers, and trending repos.\n"
        "2. Invokes Tavily search, arXiv paper extraction, and GitHub API tools to discover high-signal topics.\n"
        "3. Filters out marketing hype and extracts raw technical facts, benchmarks, and architectural novelties.\n"
        '"""\n'
    ),
    "backend/app/agents/analyst_agent.py": (
        '"""\n'
        "1. Technical Analyst agent that deep-dives into raw scouted materials to verify architecture claims and code.\n"
        "2. Formulates senior-level technical breakdowns, pseudocode examples, trade-off comparisons, and core takeaways.\n"
        "3. Produces a structured technical summary that serves as the single source of truth for platform stylists.\n"
        '"""\n'
    ),
    "backend/app/agents/linkedin_agent.py": (
        '"""\n'
        "1. LinkedIn Authority Stylist agent that transforms technical summaries into high-impact thought leadership posts.\n"
        "2. Crafts strong non-cringe hooks, actionable takeaways, and slide-by-slide outlines for PDF carousels.\n"
        "3. Enforces senior AI engineer voice: zero generic fluff, high information density, and professional authority.\n"
        '"""\n'
    ),
    "backend/app/agents/twitter_agent.py": (
        '"""\n'
        "1. X (Twitter) Thread Master agent that breaks complex AI engineering topics into punchy 4-7 tweet threads.\n"
        "2. Formats hook tweets, diagram placeholders, code snippets, and concise summaries within 280-character constraints.\n"
        "3. Optimizes threads for high virality among AI founders, researchers, and senior software engineers.\n"
        '"""\n'
    ),
    "backend/app/agents/blog_agent.py": (
        '"""\n'
        "1. Longform Technical Writer agent generating 1,200-2,000 word markdown tutorials for Dev.to and Medium.\n"
        "2. Structures articles with clear headings, mermaid architecture diagrams, runnable code blocks, and SEO tags.\n"
        "3. Showcases deep technical mastery to attract recruiter inbound messages and freelance client inquiries.\n"
        '"""\n'
    ),
    "backend/app/agents/critic_agent.py": (
        '"""\n'
        "1. Quality Evaluator and Anti-Cringe Rubric agent acting as the final gatekeeper before the approval queue.\n"
        "2. Scores drafts on technical accuracy, clarity, originality, and adherence to the Senior AI Engineer persona.\n"
        "3. Rejects hallucinated or low-effort drafts back to stylist nodes with specific correction feedback.\n"
        '"""\n'
    ),

    # External Information Tools
    "backend/app/tools/__init__.py": (
        '"""\n'
        "1. Tools package providing external data retrieval capabilities to LangGraph agent nodes.\n"
        "2. Encapsulates external search APIs, academic paper registries, and code repository scrapers.\n"
        "3. Formats raw tool outputs into clean, token-efficient markdown context for LLM prompts.\n"
        '"""\n'
    ),
    "backend/app/tools/tavily_tool.py": (
        '"""\n'
        "1. Wraps Tavily Search API for AI-optimized web queries, news aggregation, and official documentation lookups.\n"
        "2. Extracts clean markdown content while filtering out boilerplate navigation and advertising noise.\n"
        "3. Enables the Scout agent to search specific technical domains (e.g. HuggingFace, OpenAI, arXiv, Anthropic).\n"
        '"""\n'
    ),
    "backend/app/tools/arxiv_tool.py": (
        '"""\n'
        "1. Queries the official arXiv API for newly published AI, Machine Learning (cs.AI, cs.LG, cs.CL) research papers.\n"
        "2. Parses paper titles, authors, abstract summaries, and PDF download links for technical extraction.\n"
        "3. Provides cutting-edge research material to position your personal brand at the forefront of AI innovation.\n"
        '"""\n'
    ),
    "backend/app/tools/github_tool.py": (
        '"""\n'
        "1. Interfaces with GitHub REST API to fetch trending AI repositories, release notes, and commit activity.\n"
        "2. Identifies explosive open-source libraries, star velocity, and architectural patterns in trending codebases.\n"
        "3. Feeds real-world code implementation topics into the content generation pipeline.\n"
        '"""\n'
    ),

    # Visual Asset & Carousel Generators
    "backend/app/visual/__init__.py": (
        '"""\n'
        "1. Visual Asset package handling automated image, diagram, and PDF slide generation.\n"
        "2. Transforms structured agent JSON into aesthetic, high-resolution media assets for LinkedIn and Twitter.\n"
        "3. Uses headless browser rendering and SVG template engines for pixel-perfect typography.\n"
        '"""\n'
    ),
    "backend/app/visual/carousel_generator.py": (
        '"""\n'
        "1. Compiles structured slide deck JSON into modern multi-page PDF carousels tailored for LinkedIn uploads.\n"
        "2. Injects dynamic text, syntax-highlighted code, and slide counters into an HTML/CSS layout rendered via Playwright.\n"
        "3. Generates sleek dark-mode slides that drive massive engagement and dwell time on LinkedIn algorithms.\n"
        '"""\n'
    ),
    "backend/app/visual/diagram_generator.py": (
        '"""\n'
        "1. Converts Mermaid flowchart and architecture code strings into high-resolution PNG and SVG graphics.\n"
        "2. Generates code snippet snapshot cards with custom dark themes for Twitter thread attachments.\n"
        "3. Embeds visual architecture proofs directly into longform technical blogs and social posts.\n"
        '"""\n'
    ),
    "backend/app/visual/templates/carousel_template.html": (
        "<!-- 1. Jinja2 / HTML5 template for rendering pixel-perfect multi-slide LinkedIn PDF carousels. -->\n"
        "<!-- 2. Features sleek dark-mode typography (Inter font), code highlighting, brand watermark, and slide numbers. -->\n"
        "<!-- 3. Rendered to multi-page PDF by carousel_generator.py using headless browser automation. -->"
    ),

    # Social Platform Publishing Clients
    "backend/app/publishers/__init__.py": (
        '"""\n'
        "1. Social Platform Publishing package wrapping external social network REST and GraphQL APIs.\n"
        "2. Provides a unified, polymorphic publishing interface across all target platforms.\n"
        "3. Handles platform authentication, media uploads, rate limiting, and response tracking.\n"
        '"""\n'
    ),
    "backend/app/publishers/base.py": (
        '"""\n'
        "1. Abstract Base Class ('BasePublisher') defining the standard interface for all social platform clients.\n"
        "2. Enforces implementation of 'publish_text', 'publish_media', 'publish_thread', and 'verify_credentials'.\n"
        "3. Provides standardized error handling, retry logic, and publishing result data classes.\n"
        '"""\n'
    ),
    "backend/app/publishers/linkedin_client.py": (
        '"""\n'
        "1. LinkedIn API v2 client supporting single text posts, image attachments, and multi-page PDF carousel documents.\n"
        "2. Implements the 3-step LinkedIn media upload protocol (registerUpload -> uploadBinary -> createPost).\n"
        "3. Returns the published post URL and URN identifier for tracking live engagement.\n"
        '"""\n'
    ),
    "backend/app/publishers/twitter_client.py": (
        '"""\n'
        "1. X (Twitter) API v2 client using OAuth 1.0a / OAuth 2.0 to post standalone tweets and chained threads.\n"
        "2. Uploads media attachments (PNG diagrams, code cards) via Twitter v1.1 media endpoints before tweeting.\n"
        "3. Automatically links successive tweets using 'in_reply_to_tweet_id' to publish seamless threads.\n"
        '"""\n'
    ),
    "backend/app/publishers/devto_client.py": (
        '"""\n'
        "1. Dev.to API client for publishing full-length technical markdown articles with tags and canonical URLs.\n"
        "2. Supports publishing in 'draft' mode for final review or direct 'published' status.\n"
        "3. Sets SEO metadata, cover images, and cross-links back to your personal portfolio and social profiles.\n"
        '"""\n'
    ),
    "backend/app/publishers/medium_client.py": (
        '"""\n'
        "1. Medium API integration for cross-posting longform AI engineering case studies and technical articles.\n"
        "2. Handles markdown-to-Medium format conversion and canonical URL assignment to avoid SEO duplication.\n"
        "3. Expands your reach to engineering leaders, recruiters, and tech executives on the Medium platform.\n"
        '"""\n'
    ),

    # Human-in-the-Loop Bot & Job Scheduler
    "backend/app/bot/__init__.py": (
        '"""\n'
        "1. Telegram Bot package providing mobile Human-in-the-Loop review and 1-click publishing controls.\n"
        "2. Allows you to monitor, review, edit, and approve posts directly from your smartphone.\n"
        "3. Connects incoming Telegram webhook/polling callbacks directly to the FastAPI post database.\n"
        '"""\n'
    ),
    "backend/app/bot/telegram_bot.py": (
        '"""\n'
        "1. Telegram bot implementation sending notifications with draft previews and inline interactive buttons.\n"
        "2. Handles callback queries for '[✅ Approve]', '[✏️ Edit]', '[❌ Reject]', and '[📄 Preview PDF]'.\n"
        "3. Updates post status in the database upon approval and triggers automatic scheduling or instant publishing.\n"
        '"""\n'
    ),
    "backend/app/scheduler/__init__.py": (
        '"""\n'
        "1. Background Job Scheduler package managing recurring autonomous runs and scheduled post publishing.\n"
        "2. Powered by AsyncIOScheduler to handle time-based triggers without blocking the main event loop.\n"
        "3. Ensures posts are published during peak platform engagement windows (e.g. 8:30 AM / 5:00 PM).\n"
        '"""\n'
    ),
    "backend/app/scheduler/job_scheduler.py": (
        '"""\n'
        "1. Configures APScheduler cron jobs for daily automated AI trend scouting and post publishing queues.\n"
        "2. Scans the database for posts marked 'APPROVED' whose scheduled time has arrived and triggers publishers.\n"
        "3. Provides methods to dynamically add, modify, pause, or remove scheduled publishing jobs via the API.\n"
        '"""\n'
    ),

    # REST API Routes
    "backend/app/api/__init__.py": (
        '"""\n'
        "1. REST API package organizing all route endpoints exposed to the Next.js frontend and external webhooks.\n"
        "2. Modularizes endpoints by versioning (v1) and functional domain (posts, ingestion, settings, analytics).\n"
        "3. Provides centralized route aggregation and dependency injection for security and database sessions.\n"
        '"""\n'
    ),
    "backend/app/api/v1/__init__.py": (
        '"""\n'
        "1. API v1 router aggregator combining all v1 route modules into a single FastAPI APIRouter.\n"
        "2. Prepends the '/api/v1' prefix to all post, ingestion, settings, and analytics endpoints.\n"
        "3. Included in the root FastAPI app in backend/app/main.py.\n"
        '"""\n'
    ),
    "backend/app/api/v1/posts.py": (
        '"""\n'
        "1. FastAPI route handlers for CRUD operations on posts: listing queues, editing drafts, and status changes.\n"
        "2. Exposes endpoints for 1-click Approve, Reject, Reschedule, and Instant Publish actions from the dashboard.\n"
        "3. Returns paginated post lists filtered by status (DRAFT, APPROVED, PUBLISHED) and platform.\n"
        '"""\n'
    ),
    "backend/app/api/v1/ingestion.py": (
        '"""\n'
        "1. Endpoints for triggering on-demand research runs and ingesting 'Build-in-Public' project notes or audio logs.\n"
        "2. Accepts custom topic seeds, GitHub repository URLs, or project updates and launches the LangGraph agent team.\n"
        "3. Streams execution progress updates back to the frontend via WebSockets or Server-Sent Events (SSE).\n"
        '"""\n'
    ),
    "backend/app/api/v1/settings.py": (
        '"""\n'
        "1. API endpoints for managing platform credentials, publishing time windows, and agent persona configurations.\n"
        "2. Allows updating API keys securely and toggling automated scout schedules from the admin dashboard.\n"
        "3. Validates connection credentials against LinkedIn, Twitter, Dev.to, and Telegram on save.\n"
        '"""\n'
    ),
    "backend/app/api/v1/analytics.py": (
        '"""\n'
        "1. API endpoints serving post performance analytics, engagement metrics, and reach growth statistics.\n"
        "2. Aggregates views, likes, retweets, comments, and profile visits across connected social platforms.\n"
        "3. Feeds visual analytics charts and milestone trackers on the Next.js admin dashboard.\n"
        '"""\n'
    ),

    # Backend Tests
    "backend/tests/__init__.py": (
        '"""\n'
        "1. Automated test suite package for backend unit and integration testing.\n"
        "2. Contains test fixtures, mock API clients, and database session overrides for Pytest.\n"
        "3. Ensures high code quality, regression prevention, and CI/CD readiness.\n"
        '"""\n'
    ),
    "backend/tests/test_agents.py": (
        '"""\n'
        "1. Unit and integration tests for LangGraph state graph transitions, scout tools, and agent stylist nodes.\n"
        "2. Uses mock LLM responses to verify deterministic schema outputs (SlideDeckSchema, TweetThreadSchema).\n"
        "3. Tests critic scoring thresholds and anti-cringe evaluation rubric behavior.\n"
        '"""\n'
    ),
    "backend/tests/test_publishers.py": (
        '"""\n'
        "1. Unit tests for LinkedIn, Twitter, Dev.to, and Medium API client implementations with mocked HTTP calls.\n"
        "2. Verifies proper payload structuring, media upload sequences, and error handling on rate limits (429).\n"
        "3. Ensures robust publishing failure recovery and database status tracking.\n"
        '"""\n'
    ),

    # Frontend Admin Dashboard (Next.js)
    "frontend/package.json": (
        "{\n"
        '  "// 1": "Defines Next.js frontend dependencies (React 18+, TypeScript, Tailwind CSS, Lucide Icons, Axios).",\n'
        '  "// 2": "Configures development, build, and linting scripts for the admin dashboard application.",\n'
        '  "// 3": "Ensures modern, type-safe fullstack web application standards for production deployment."\n'
        "}\n"
    ),
    "frontend/src/app/page.tsx": (
        "// 1. Next.js Dashboard overview page displaying active campaigns, high-level analytics, and quick-action buttons.\n"
        "// 2. Features a 'Build-in-Public' quick ingestion box to convert raw project notes into multi-platform posts.\n"
        "// 3. Displays real-time status of the LangGraph autonomous scout pipeline and upcoming scheduled posts."
    ),
    "frontend/src/app/queue/page.tsx": (
        "// 1. Post Queue & Approval Workspace for reviewing agent-generated drafts across LinkedIn, X, and Dev.to.\n"
        "// 2. Provides inline rich text editing, critic score breakdown inspection, and 1-click Approve/Reject actions.\n"
        "// 3. Includes interactive live visualizers for LinkedIn PDF carousels and Twitter thread cards."
    ),
    "frontend/src/app/calendar/page.tsx": (
        "// 1. Visual Publishing Calendar page showing scheduled, pending, and past published posts on a monthly/weekly grid.\n"
        "// 2. Supports drag-and-drop rescheduling across optimal platform engagement time windows.\n"
        "// 3. Helps maintain a consistent, high-frequency posting cadence to rapidly grow your AI engineer presence."
    ),
    "frontend/src/app/settings/page.tsx": (
        "// 1. Settings configuration page for managing OpenRouter model routing, API tokens, and Telegram bot alerts.\n"
        "// 2. Allows fine-tuning the Senior AI Engineer persona prompt, anti-cringe thresholds, and niche focus areas.\n"
        "// 3. Provides platform connection diagnostic tools to test API key validity in real-time."
    ),
    "frontend/src/components/Sidebar.tsx": (
        "// 1. Persistent navigation sidebar component providing seamless routing across Dashboard, Queue, Calendar, and Settings.\n"
        "// 2. Built with sleek dark-mode styling, active route highlighting, and status indicator for running background agents.\n"
        "// 3. Reusable across all pages in the Next.js App Router layout."
    ),
    "frontend/src/components/PostCard.tsx": (
        "// 1. Card component displaying individual post drafts with platform badges (LinkedIn, X, Dev.to), tags, and metrics.\n"
        "// 2. Renders critic quality score badge, action buttons (Approve, Edit, Reject, Schedule), and copy-to-clipboard.\n"
        "// 3. Supports expandable view for detailed slide deck inspection and thread breakdown."
    ),
    "frontend/src/components/CarouselPreview.tsx": (
        "// 1. Interactive carousel previewer component simulating the native LinkedIn PDF document slide viewer.\n"
        "// 2. Allows flipping through generated slides, zooming into code snippets, and verifying visual aesthetics.\n"
        "// 3. Provides a direct download button to inspect the compiled high-resolution PDF file."
    ),
    "frontend/src/components/ThreadPreview.tsx": (
        "// 1. Interactive X (Twitter) thread previewer component simulating native tweet cards with reply connector lines.\n"
        "// 2. Displays character count indicators per tweet, code image card attachments, and thread ordering (1/N).\n"
        "// 3. Enables inline editing of individual tweets before pushing to the approval queue."
    ),
    "frontend/src/lib/api.ts": (
        "// 1. Frontend API client utility configuring Axios / Fetch for communication with the FastAPI backend.\n"
        "// 2. Encapsulates typed methods for fetching posts, approving drafts, triggering agent runs, and saving settings.\n"
        "// 3. Centralizes error handling, base URL configuration, and request/response interceptors."
    ),
}


def build_scaffold():
    root = Path(".")
    created_files = 0
    created_dirs = 0

    print("Initializing project folder structure and files...")

    for file_path_str, comment_content in FILE_STRUCTURE.items():
        file_path = root / file_path_str
        parent_dir = file_path.parent

        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            created_dirs += 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(comment_content + "\n")
        created_files += 1

    print(f"Successfully created {created_files} files across {created_dirs} directories!")


if __name__ == "__main__":
    build_scaffold()
