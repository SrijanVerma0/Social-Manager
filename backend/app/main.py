"""
1. Entry point for the FastAPI server; initializes CORS, middleware, and API router mounting.
2. Starts and stops background workers (APScheduler, Telegram Bot polling) via lifespan events.
3. Exposes health check endpoints and serves the REST API for the Next.js frontend.
"""

