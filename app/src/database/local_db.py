import os
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "snapclass_local.db"


def _get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_local_db():
    conn = _get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_embedding TEXT,
                voice_embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                section TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS subject_students (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                PRIMARY KEY(student_id, subject_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS attendance_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                is_present INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_logs_subject ON attendance_logs(subject_id);
            CREATE INDEX IF NOT EXISTS idx_logs_student ON attendance_logs(student_id);
        """)
    conn.close()


init_local_db()


class LocalResponse:
    def __init__(self, data: Any):
        self.data = data


class LocalQueryBuilder:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.action = "select"  # select, insert, delete
        self.select_columns = "*"
        self.filters: List[tuple] = []  # (col, val)
        self.insert_data: Optional[Union[Dict, List[Dict]]] = None

    def select(self, columns: str = "*"):
        self.action = "select"
        self.select_columns = columns
        return self

    def insert(self, data: Union[Dict, List[Dict]]):
        self.action = "insert"
        self.insert_data = data
        return self

    def delete(self):
        self.action = "delete"
        return self

    def eq(self, column: str, value: Any):
        self.filters.append((column, value))
        return self

    def execute(self) -> LocalResponse:
        conn = _get_connection()
        try:
            if self.action == "insert":
                return self._execute_insert(conn)
            elif self.action == "delete":
                return self._execute_delete(conn)
            else:
                return self._execute_select(conn)
        finally:
            conn.close()

    def _execute_insert(self, conn: sqlite3.Connection) -> LocalResponse:
        records = (
            self.insert_data
            if isinstance(self.insert_data, list)
            else [self.insert_data]
        )
        inserted_list = []

        with conn:
            for rec in records:
                rec_copy = dict(rec)
                # Handle JSON serialization for biometrics
                for json_col in ["face_embedding", "voice_embedding"]:
                    if json_col in rec_copy and rec_copy[json_col] is not None:
                        if not isinstance(rec_copy[json_col], str):
                            rec_copy[json_col] = json.dumps(rec_copy[json_col])

                cols = list(rec_copy.keys())
                placeholders = [":" + c for c in cols]
                sql = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                cursor = conn.cursor()
                cursor.execute(sql, rec_copy)
                last_id = cursor.lastrowid

                # Retrieve inserted row
                pk = "log_id" if self.table_name == "attendance_logs" else \
                     "student_id" if self.table_name == "students" else \
                     "teacher_id" if self.table_name == "teachers" else \
                     "subject_id" if self.table_name == "subjects" else None

                if pk and last_id:
                    cursor.execute(f"SELECT * FROM {self.table_name} WHERE {pk} = ?", (last_id,))
                    row = cursor.fetchone()
                    if row:
                        inserted_list.append(self._deserialize_row(self.table_name, dict(row)))
                else:
                    inserted_list.append(rec)

        return LocalResponse(data=inserted_list if isinstance(self.insert_data, list) else inserted_list[:1])

    def _execute_delete(self, conn: sqlite3.Connection) -> LocalResponse:
        where_clauses = [f"{col} = ?" for col, _ in self.filters]
        values = [val for _, val in self.filters]
        sql = f"DELETE FROM {self.table_name}"
        if where_clauses:
            sql += f" WHERE {' AND '.join(where_clauses)}"
        with conn:
            conn.execute(sql, values)
        return LocalResponse(data=[])

    def _execute_select(self, conn: sqlite3.Connection) -> LocalResponse:
        cursor = conn.cursor()

        # Handle special teacher attendance query:
        # attendance_logs.select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id)
        if self.table_name == "attendance_logs" and any("teacher_id" in f[0] for f in self.filters):
            teacher_id = next(f[1] for f in self.filters if "teacher_id" in f[0])
            sql = """
                SELECT a.*, s.subject_id as s_id, s.subject_code as s_code,
                       s.name as s_name, s.section as s_section, s.teacher_id as s_teacher_id
                FROM attendance_logs a
                INNER JOIN subjects s ON a.subject_id = s.subject_id
                WHERE s.teacher_id = ?
            """
            cursor.execute(sql, (teacher_id,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = {
                    "log_id": r["log_id"],
                    "student_id": r["student_id"],
                    "subject_id": r["subject_id"],
                    "timestamp": r["timestamp"],
                    "is_present": bool(r["is_present"]),
                    "subjects": {
                        "subject_id": r["s_id"],
                        "subject_code": r["s_code"],
                        "name": r["s_name"],
                        "section": r["s_section"],
                        "teacher_id": r["s_teacher_id"],
                    }
                }
                results.append(item)
            return LocalResponse(data=results)

        # Standard WHERE clauses
        where_clauses = []
        values = []
        for col, val in self.filters:
            where_clauses.append(f"{col} = ?")
            values.append(val)

        sql = f"SELECT * FROM {self.table_name}"
        if where_clauses:
            sql += f" WHERE {' AND '.join(where_clauses)}"

        cursor.execute(sql, values)
        raw_rows = [self._deserialize_row(self.table_name, dict(r)) for r in cursor.fetchall()]

        # Process joins / nested relations expected by the frontend
        if self.table_name == "subjects" and "subject_students(count)" in self.select_columns:
            for sub in raw_rows:
                sid = sub["subject_id"]
                cursor.execute("SELECT COUNT(*) as count FROM subject_students WHERE subject_id = ?", (sid,))
                count_val = cursor.fetchone()["count"]
                sub["subject_students"] = [{"count": count_val}]

                cursor.execute("SELECT timestamp FROM attendance_logs WHERE subject_id = ?", (sid,))
                sub["attendance_logs"] = [{"timestamp": r["timestamp"]} for r in cursor.fetchall()]

        elif self.table_name == "subject_students":
            if "students(*)" in self.select_columns:
                for row in raw_rows:
                    cursor.execute("SELECT * FROM students WHERE student_id = ?", (row["student_id"],))
                    st_row = cursor.fetchone()
                    row["students"] = self._deserialize_row("students", dict(st_row)) if st_row else None
            if "subjects(*)" in self.select_columns:
                for row in raw_rows:
                    cursor.execute("SELECT * FROM subjects WHERE subject_id = ?", (row["subject_id"],))
                    sub_row = cursor.fetchone()
                    row["subjects"] = dict(sub_row) if sub_row else None

        elif self.table_name == "attendance_logs":
            if "subjects(*)" in self.select_columns:
                for row in raw_rows:
                    cursor.execute("SELECT * FROM subjects WHERE subject_id = ?", (row["subject_id"],))
                    sub_row = cursor.fetchone()
                    row["subjects"] = dict(sub_row) if sub_row else None
            # Ensure is_present is boolean
            for row in raw_rows:
                if "is_present" in row:
                    row["is_present"] = bool(row["is_present"])

        return LocalResponse(data=raw_rows)

    def _deserialize_row(self, table: str, row: Dict) -> Dict:
        if table == "students":
            for col in ["face_embedding", "voice_embedding"]:
                if row.get(col):
                    try:
                        row[col] = json.loads(row[col])
                    except Exception:
                        pass
        elif table == "attendance_logs":
            if "is_present" in row:
                row["is_present"] = bool(row["is_present"])
        return row


class LocalDatabaseClient:
    """Mock client mimicking Supabase table queries backed by local SQLite."""
    def table(self, table_name: str) -> LocalQueryBuilder:
        return LocalQueryBuilder(table_name)
