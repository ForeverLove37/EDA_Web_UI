#!/usr/bin/env python3
"""
Database initialization script
Run this directly to initialize the database without import issues
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from models import Base

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./phoenix.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

def init_db():
    """Initialize the database by creating all tables"""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    print(f"Database file: {SQLALCHEMY_DATABASE_URL}")

if __name__ == "__main__":
    init_db()