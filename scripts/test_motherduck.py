#!/usr/bin/env python3
"""
Test script to verify MotherDuck connection
"""

import os
import duckdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MOTHERDUCK_DB = os.getenv('MOTHERDUCK_DB', 'github')

def test_motherduck_connection():
    """Test the MotherDuck connection"""
    print("🧪 Testing MotherDuck connection...")
    
    try:
        # Try to connect to MotherDuck
        if MOTHERDUCK_TOKEN:
            connection_string = f'md:{MOTHERDUCK_DB}?motherduck_token={MOTHERDUCK_TOKEN}'
            print(f"🔐 Using token authentication for database: {MOTHERDUCK_DB}")
        else:
            connection_string = f'md:{MOTHERDUCK_DB}'
            print(f"🌐 Using browser authentication for database: {MOTHERDUCK_DB}")
        
        conn = duckdb.connect(connection_string)
        print("✅ Successfully connected to MotherDuck!")
        
        # Test basic functionality
        result = conn.execute("SELECT 1 as test_value").fetchone()
        print(f"✅ Basic query test: {result}")
        
        # Show databases
        print("\n📊 Available databases:")
        databases = conn.execute("SHOW DATABASES").fetchall()
        for db in databases:
            print(f"  - {db[0]}")
        
        # Check if our tables exist
        print(f"\n📋 Tables in {MOTHERDUCK_DB} database:")
        try:
            tables = conn.execute("SHOW TABLES").fetchall()
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  No tables found - run the sync scripts to populate data")
        except Exception as e:
            print(f"  Could not list tables: {e}")
        
        conn.close()
        print("\n🎉 MotherDuck connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing MotherDuck connection: {e}")
        return False

if __name__ == '__main__':
    success = test_motherduck_connection()
    if not success:
        exit(1)