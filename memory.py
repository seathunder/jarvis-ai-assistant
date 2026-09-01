import sqlite3
import os
from datetime import datetime
from config import logger

DB_FILE = 'jarvis.db'

def init_db():
    """Initializes the SQLite database with required tables."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Table for storing conversation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for storing episodic memory (entities, facts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity TEXT,
                fact TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def save_message(user_id, role, content):
    """Saves a message to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
            (user_id, role, content)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving message: {e}")
    finally:
        if conn:
            conn.close()

def get_recent_messages(user_id, limit=10):
    """Retrieves recent messages for context."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
            (user_id, limit)
        )
        rows = cursor.fetchall()
        # Return in chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return []
    finally:
        if conn:
            conn.close()
