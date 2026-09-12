#!/usr/bin/env python3
"""
Database Initialization Script for Rakt-Sathi
Run this once to set up the database schema
"""

import mysql.connector
from mysql.connector import Error
import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "auth_plugin": "mysql_native_password"
}

def init_database():
    """Initialize the database schema."""
    try:
        # Read the SQL schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Execute schema statements
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except Error as e:
                    print(f"⚠️ Warning: {e}")
        
        connection.commit()
        print("\n✅ Database schema initialized successfully!")
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Initializing Rakt-Sathi Database Schema...")
    init_database()
