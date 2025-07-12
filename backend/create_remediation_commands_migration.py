#!/usr/bin/env python3
"""
Database migration script to add remediation_commands column to vulnerabilities table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add remediation_commands column to vulnerabilities table"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'vulnerabilities' 
                AND column_name = 'remediation_commands'
            """))
            
            if result.fetchone():
                logger.info("Column 'remediation_commands' already exists in vulnerabilities table")
                return
            
            # Add the new column
            logger.info("Adding remediation_commands column to vulnerabilities table...")
            connection.execute(text("""
                ALTER TABLE vulnerabilities 
                ADD COLUMN remediation_commands JSON
            """))
            connection.commit()
            
            logger.info("Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()