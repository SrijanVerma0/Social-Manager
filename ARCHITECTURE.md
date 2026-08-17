# Autonomous AI Engineer Brand Engine: Multi-Agent Social Presence System

## 1. Executive Summary & Objective
- **Goal:** In 6 months, land a High-Ticket AI Engineer Role / Freelance AI Consulting Clients.
- **Strategy:** Build & operate an autonomous, production-grade Multi-Agent System (LangGraph + FastAPI + Next.js + HITL Telegram Bot) that:
  1. Autonomously scouts breakthrough AI news, papers, and GitHub repos (Tavily, arXiv, GitHub APIs).
  2. Synthesizes technical insights into multi-platform assets (LinkedIn Carousels, X Threads, Dev.to Blogs).
  3. Produces a **1-2 Min Video Creator Kit** (60-90s teleprompter script + runnable screen code) for daily video updates.
  4. Generates **Thoughtful Engagement Comments** under top AI founders' posts to drive organic inbound profile visits.
  5. Implements **Smart Human-in-the-Loop (HITL)** via Telegram Bot & Next.js dashboard with 1-click Approve/Publish.
  6. Operates at ultra-low cost (~₹2 to ₹5 per day / ~$1-2 per month) via Multi-Tier OpenRouter LLM routing.

---

## 2. System Architecture & Multi-Agent State Graph

```
[Autonomous Scout / Project Voice Note]
                 │
                 ▼
      [Tavily + arXiv + GitHub Tools]
                 │
                 ▼
     [1. Scout Agent (Fast LLM)]
                 │
                 ▼
 [2. Technical Analyst & Fact-Checker (DeepSeek R1 / Sonnet)]
                 │
  ┌──────────────┼──────────────┬──────────────┬──────────────┐
  ▼              ▼              ▼              ▼              ▼
[LinkedIn     [Twitter/X      [Dev.to /      [1-2 Min Video [Thoughtful
 Specialist    Thread Master   Medium Writer  Script & Code  Engagement
 & Carousel]   & Code Cards]   Longform]      Walkthrough]   Commenter]
  │              │              │              │              │
  └──────────────┴──────────────┼──────────────┴──────────────┘
                                ▼
         [Visual Engine: Playwright HTML-to-PDF & Diagrams]
                                │
                                ▼
         [3. Senior Persona Critic & Anti-Cringe Rubric]
                                │
                        (Quality >= 85%)
                                │
                                ▼
            [HITL: Telegram Bot + Next.js Dashboard]
                                │
                           (Approved)
                                │
                                ▼
          [Publishing Scheduler: LinkedIn, X, Dev.to APIs]
```

---

## 3. The 5 Core Multi-Agent Deliverables Per Topic / Campaign

1. **LinkedIn Authority Package:**
   - Hook-driven, non-cringe technical breakdown text.
   - Auto-compiled **5-8 Slide Dark-Mode PDF Carousel** (rendered via Playwright HTML/CSS).
2. **1-2 Min Video Creator Kit (YouTube Shorts / LinkedIn / X):**
   - 60-90s Teleprompter script with timestamps:
     - `[00:00 - 00:15]` **Hook:** The core bottleneck.
     - `[00:15 - 00:45]` **Architecture:** Why standard approaches fail.
     - `[00:45 - 01:15]` **Code Walkthrough:** On-screen logic explanation.
     - `[01:15 - 01:30]` **Takeaway / CTA:** "Repo in comments".
   - Clean, runnable Python snippet to display on your screen while recording.
3. **X / Twitter Thread Master:**
   - 4-7 chained tweets with syntax-highlighted code cards and clear takeaways.
4. **Dev.to / Medium Longform Tutorial:**
   - 1,500+ word deep-dive markdown article with headers, code blocks, and diagrams.
5. **Thoughtful Engagement Assistant:**
   - Respectful, value-additive technical comments to drop on top AI founders' posts.

---

## 4. LLM Routing & Cost Optimization Strategy
- **Extraction & Scraping:** Cheap/Fast models (DeepSeek-V3 / Claude 3.5 Haiku) via OpenRouter (~$0.002/run).
- **Deep Architecture & Reasoning:** DeepSeek-R1 / Claude 3.5 Sonnet (~$0.020/run).
- **Visuals (PDF Carousels & Diagrams):** Headless Chromium (Playwright) + SVG/Mermaid = **$0 (Free)**.
- **Estimated Total Cost:** ~₹2.50 to ₹5 per day (~₹80 to ₹150 per month).

---

## 5. Technology Stack
- **Backend:** Python 3.12, FastAPI, LangGraph, LangChain Core, LiteLLM, SQLAlchemy, aiosqlite, APScheduler, python-telegram-bot, Playwright.
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Package Manager:** `uv` (Fastest Python toolchain).

---

## 6. Directory Layout
```
Social-Manager/
├── ARCHITECTURE.md          # Master Project Blueprint (This file)
├── template.py              # File scaffold generator
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph Nodes (Scout, Analyst, Stylists, VideoScript, Engagement, Critic)
│   │   ├── api/v1/          # FastAPI REST endpoints
│   │   ├── bot/             # Telegram HITL 1-click Approval Bot
│   │   ├── core/            # Config, Settings & DB Session
│   │   ├── models/          # SQLAlchemy ORM Models
│   │   ├── publishers/      # LinkedIn, Twitter, Dev.to API Clients
│   │   ├── scheduler/       # APScheduler Cron Worker
│   │   ├── schemas/         # Pydantic Schemas & LLM DTOs
│   │   ├── tools/           # Tavily, arXiv, GitHub API Tools
│   │   ├── visual/          # HTML-to-PDF Carousel & Diagram Generator
│   │   └── main.py          # FastAPI App Entrypoint
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── src/app/             # Next.js Admin Dashboard
```

---

## 7. Next Account Continuity Instructions
When opening a new session in Antigravity or a new account:
> *"Please read `ARCHITECTURE.md` in the project root. We have scaffolded the architecture and are building the system step-by-step with the user coding with your guidance."*
