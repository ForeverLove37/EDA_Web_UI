#!/usr/bin/env python3
"""
Script to create a default user for testing
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
import models, auth

def create_default_user():
    """Create a default user for testing"""
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
    
    if existing_user:
        print("Default user already exists:")
        print(f"Email: {existing_user.email}")
        print(f"Name: {existing_user.full_name}")
        db.close()
        return
    
    # Create new user
    hashed_password = auth.get_password_hash("admin123")
    new_user = models.User(
        email="admin@example.com",
        hashed_password=hashed_password,
        full_name="Admin User"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("Default user created successfully!")
    print(f"Email: admin@example.com")
    print(f"Password: admin123")
    print(f"Name: Admin User")
    
    db.close()

if __name__ == "__main__":
    create_default_user()