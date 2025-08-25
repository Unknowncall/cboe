#!/usr/bin/env python3
"""
Script to initialize and seed the database for Vercel deployment
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the server directory to the path so we can import modules
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

from database import DatabaseManager
from utils import generate_request_id

def create_database():
    """Create and seed the database for deployment"""
    print("Creating database for Vercel deployment...")
    
    # Initialize database manager
    db_manager = DatabaseManager("trails.db")
    request_id = generate_request_id()
    
    # Initialize database structure
    print("Initializing database structure...")
    if not db_manager.init_database(request_id):
        print("ERROR: Failed to initialize database")
        return False
    
    # Seed with trail data
    print("Seeding database with trail data...")
    trails_count = db_manager.seed_trails(request_id)
    if trails_count == 0:
        print("ERROR: Failed to seed database")
        return False
    
    print(f"Successfully created database with {trails_count} trails")
    
    # Copy database to api directory for Vercel functions
    import shutil
    shutil.copy("trails.db", "api/trails.db")
    print("Database copied to api directory")
    
    return True

if __name__ == "__main__":
    if create_database():
        print("Database setup completed successfully!")
        sys.exit(0)
    else:
        print("Database setup failed!")
        sys.exit(1)