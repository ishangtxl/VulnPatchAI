#!/usr/bin/env python3
"""
Create database migration for MFA fields
"""
import subprocess
import sys

def create_migration():
    """Create alembic migration for MFA fields"""
    try:
        # Create migration
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Add MFA fields to User table"
        ], cwd="backend", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print(result.stdout)
        else:
            print("❌ Error creating migration:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_migration()