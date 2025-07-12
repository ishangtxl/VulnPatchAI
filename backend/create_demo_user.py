#!/usr/bin/env python3
"""
Script to create demo user for VulnPatch AI
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

def create_demo_user():
    """Create demo user if it doesn't exist"""
    
    db: Session = SessionLocal()
    auth_service = AuthService(db)
    
    try:
        # Check if demo user already exists
        existing_user = auth_service.get_user_by_email("demo@vulnpatch.ai")
        if existing_user:
            print("✅ Demo user already exists!")
            return
        
        # Create demo user
        user_data = UserCreate(
            email="demo@vulnpatch.ai",
            password="demo123",
            full_name="Demo User",
            role="admin"
        )
        
        user = auth_service.create_user(user_data)
        print(f"✅ Demo user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Password: demo123")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()