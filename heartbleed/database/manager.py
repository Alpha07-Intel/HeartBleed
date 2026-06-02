import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from ..config import DB_PATH
from ..core.models import Investigation, Profile, CorrelationResult, InputType

class DatabaseManager:
    """Handles persistence for HeartBleed investigations using SQLite."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Investigations Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    input_type TEXT,
                    input_value TEXT,
                    data_json TEXT
                )
            """)
            conn.commit()

    def save_investigation(self, investigation: Investigation) -> int:
        """Saves an investigation and its results as a JSON blob for the MVP."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            data = investigation.json()
            cursor.execute(
                "INSERT INTO investigations (timestamp, input_type, input_value, data_json) VALUES (?, ?, ?, ?)",
                (investigation.timestamp.isoformat(), investigation.input_type.value, investigation.input_value, data)
            )
            conn.commit()
            investigation.id = cursor.lastrowid
            return investigation.id

    def get_investigation(self, inv_id: int) -> Optional[Investigation]:
        """Retrieves a saved investigation by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data_json FROM investigations WHERE id = ?", (inv_id,))
            row = cursor.fetchone()
            if row:
                return Investigation.parse_raw(row[0])
        return None

    def list_investigations(self, limit: int = 10) -> List[dict]:
        """Lists recent investigations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, input_type, input_value FROM investigations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return [
                {"id": r[0], "timestamp": r[1], "type": r[2], "value": r[3]}
                for r in cursor.fetchall()
            ]
