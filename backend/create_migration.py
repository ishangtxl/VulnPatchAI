#!/usr/bin/env python3
"""
Script to create database migration
"""
import os
import sys
from alembic.config import Config
from alembic import command

def create_migration(message="Auto migration"):
    """Create database migration"""
    
    # Set up Alembic config
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Create migration
        command.revision(
            alembic_cfg, 
            autogenerate=True, 
            message=message
        )
        print(f"✅ Migration '{message}' created successfully!")
        
        # Apply migration
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migration applied successfully!")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "Auto migration"
    create_migration(message)