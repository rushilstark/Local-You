#!/usr/bin/env python3
"""
⚡ EXTREME LOCAL GPT v4 — Persistent Conversation Memory
SQLite-backed conversation history that survives restarts.

NEW in v4 — v3 only had session-based (in-memory) conversation.
"""

import sqlite3
import time
import json
from pathlib import Path
from typing import List, Dict, Optional

from core.config import AppConfig, Color


class ConversationMemory:
    """
    Persistent conversation memory using SQLite.

    - Stores all messages across sessions
    - Supports multiple conversation sessions
    - Searchable by content
    - Auto-loads last session on startup
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.db_path = config.memory.conversations_db_path
        self.current_session_id = None

        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()
        self._start_new_session()

    def _init_db(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at REAL NOT NULL,
                    ended_at REAL,
                    topic TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id)
            """)

    def _start_new_session(self):
        """Start a new conversation session."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (started_at) VALUES (?)",
                (time.time(),)
            )
            self.current_session_id = cursor.lastrowid

    def add_message(self, role: str, content: str):
        """Add a message to the current session."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (self.current_session_id, role, content, time.time()),
            )

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from current session."""
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                """SELECT role, content, timestamp FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (self.current_session_id, limit),
            ).fetchall()

        # Return in chronological order
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in reversed(rows)
        ]

    def get_all_sessions(self) -> List[Dict]:
        """Get all conversation sessions."""
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                """SELECT s.id, s.started_at, s.topic,
                          COUNT(m.id) as message_count
                   FROM sessions s
                   LEFT JOIN messages m ON m.session_id = s.id
                   GROUP BY s.id
                   ORDER BY s.started_at DESC""",
            ).fetchall()

        return [
            {
                "id": row[0],
                "started_at": row[1],
                "topic": row[2],
                "message_count": row[3],
            }
            for row in rows
        ]

    def load_session(self, session_id: int) -> List[Dict]:
        """Load messages from a specific session."""
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                """SELECT role, content, timestamp FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp ASC""",
                (session_id,),
            ).fetchall()

        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in rows
        ]

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search messages across all sessions."""
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                """SELECT role, content, timestamp, session_id FROM messages
                   WHERE content LIKE ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (f"%{query}%", limit),
            ).fetchall()

        return [
            {
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "session_id": row[3],
            }
            for row in rows
        ]

    def session_count(self) -> int:
        """Total number of sessions."""
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()
        return row[0] if row else 0

    def message_count(self) -> int:
        """Total messages in current session."""
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (self.current_session_id,),
            ).fetchone()
        return row[0] if row else 0
