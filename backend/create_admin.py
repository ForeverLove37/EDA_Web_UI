#!/usr/bin/env python3
"""
Script to create an admin account with hardcoded password
Run this script anytime you need to reset or create the admin account
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import engine, get_db
import models
from auth import get_password_hash

def create_admin_account():
    """Create admin account with hardcoded credentials"""
    
    # Hardcoded admin credentials
    ADMIN_EMAIL = "admin@phoenix.com"
    ADMIN_PASSWORD = "Admin123!"  # Strong password
    ADMIN_NAME = "System Administrator"
    
    # Create database session
    db = Session(bind=engine)
    
    try:
        # Check if admin already exists
        existing_admin = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
        
        if existing_admin:
            print(f"Admin account already exists: {ADMIN_EMAIL}")
            print("Updating password...")
            existing_admin.hashed_password = get_password_hash(ADMIN_PASSWORD)
            db.commit()
            print("Admin password updated successfully!")
        else:
            # Create new admin user
            hashed_password = get_password_hash(ADMIN_PASSWORD)
            admin_user = models.User(
                email=ADMIN_EMAIL,
                hashed_password=hashed_password,
                full_name=ADMIN_NAME,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Admin account created successfully!")
        
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print("You can now login with these credentials")
        
    except Exception as e:
        print(f"Error creating admin account: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_account()