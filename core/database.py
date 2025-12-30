import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "typing.db"

DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
class DatabaseManager:
    def __init__(self):
        self.db_path = Path("data") /"typing.db"
        self.create_tables()
    
    def connect(self):
        connection=sqlite3.connect(self.db_path)
        return connection
    
    def create_tables(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS typing_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_date TEXT NOT NULL,
                gross_wpm REAL NOT NULL,
                net_wpm REAL NOT NULL,
                accuracy REAL NOT NULL
            )
        """)
        connection.commit()
        connection.close()
    
    def save_session(self, user_id, session_date: str, gross_wpm: float, net_wpm: float, accuracy: float):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO typing_sessions (user_id,session_date, gross_wpm, net_wpm, accuracy)
            VALUES (?, ?, ?, ?,?)
            """,
            (user_id,session_date, gross_wpm, net_wpm, accuracy)
        )

        connection.commit()
        connection.close()
    
    def get_all_sessions(self):
        connection=self.connect()
        cursor=connection.cursor()
        cursor.execute(
            """
            SELECT id, session_date, gross_wpm, net_wpm, accuracy
            FROM typing_sessions
            ORDER BY id ASC
            """
        )
        rows= cursor.fetchall()
        connection.close()
        return rows
    
    def get_summary_stats(self):
        connection= self.connect()
        cursor= connection.cursor()

        cursor.execute("""
            SELECT
                AVG(net_wpm),
                AVG(accuracy),
                COUNT(*)
            FROM typing_sessions
        """)

        avg_net_wpm, avg_accuracy, total_sessions = cursor.fetchone()
        connection.close()

        return avg_net_wpm, avg_accuracy, total_sessions
    
    def get_sessions_by_user(self, user_id):
        connection=self.connect()
        cursor=connection.cursor()

        cursor.execute("""
            SELECT id, session_date, gross_wpm, net_wpm, accuracy
            FROM typing_sessions
            WHERE user_id = ?
            ORDER BY id ASC
        """, (user_id,))

        rows=cursor.fetchall()
        connection.close()
        return rows
