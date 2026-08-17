"""
1. Configures SQLAlchemy engine, session factory (sessionmaker), and declarative base for ORM.
2. Supports SQLite for local zero-config development and PostgreSQL for production.
3. Provides the 'get_db' dependency function for injecting database sessions into FastAPI routes.
"""

