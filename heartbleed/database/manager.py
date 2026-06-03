import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from ..config import DB_PATH
from ..core.models import Investigation, Profile, CorrelationResult, InputType, Workspace

class DatabaseManager:
    """Handles persistence for HeartBleed investigations and workspaces using SQLite."""
    
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
            
            # Workspaces Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT
                )
            """)
            
            # Workspace-Investigation mapping Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspace_investigations (
                    workspace_id INTEGER,
                    investigation_id INTEGER,
                    FOREIGN KEY(workspace_id) REFERENCES workspaces(id),
                    FOREIGN KEY(investigation_id) REFERENCES investigations(id),
                    PRIMARY KEY(workspace_id, investigation_id)
                )
            """)
            conn.commit()

    def save_investigation(self, investigation: Investigation) -> int:
        """Saves an investigation and its results as a JSON blob."""
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

    def create_workspace(self, name: str, description: Optional[str] = None) -> int:
        """Creates a new workspace."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO workspaces (name, description, created_at) VALUES (?, ?, ?)",
                (name, description, now)
            )
            conn.commit()
            return cursor.lastrowid

    def add_to_workspace(self, ws_id: int, inv_id: int):
        """Links an investigation to a workspace."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO workspace_investigations (workspace_id, investigation_id) VALUES (?, ?)",
                (ws_id, inv_id)
            )
            conn.commit()

    def get_workspace(self, ws_id: int) -> Optional[Workspace]:
        """Retrieves a workspace and its investigations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, created_at FROM workspaces WHERE id = ?", (ws_id,))
            ws_row = cursor.fetchone()
            if not ws_row:
                return None
            
            cursor.execute("SELECT investigation_id FROM workspace_investigations WHERE workspace_id = ?", (ws_id,))
            inv_ids = [r[0] for r in cursor.fetchall()]
            
            return Workspace(
                id=ws_row[0],
                name=ws_row[1],
                description=ws_row[2],
                created_at=datetime.fromisoformat(ws_row[3]),
                investigation_ids=inv_ids
            )

    def list_workspaces(self) -> List[dict]:
        """Lists all workspaces."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, created_at FROM workspaces ORDER BY id DESC")
            return [
                {"id": r[0], "name": r[1], "description": r[2], "created_at": r[3]}
                for r in cursor.fetchall()
            ]

    def clear_all(self):
        """Deletes all investigation records and workspaces from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM investigations")
            cursor.execute("DELETE FROM workspaces")
            cursor.execute("DELETE FROM workspace_investigations")
            conn.commit()
