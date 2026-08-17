"""
1. API v1 router aggregator combining all v1 route modules into a single FastAPI APIRouter.
2. Prepends the '/api/v1' prefix to all post, ingestion, settings, and analytics endpoints.
3. Included in the root FastAPI app in backend/app/main.py.
"""

