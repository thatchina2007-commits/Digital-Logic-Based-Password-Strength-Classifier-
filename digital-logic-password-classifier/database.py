"""
database.py
SQLite database manager for EC2201 Digital Logic Password Strength Classifier.
Stores live user evaluations, uploaded/generated datasets, and analytics history.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logic_engine

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital_logic.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes schema and seeds baseline dataset if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password_masked TEXT NOT NULL,
        length INTEGER NOT NULL,
        a INTEGER NOT NULL,
        b INTEGER NOT NULL,
        c INTEGER NOT NULL,
        d INTEGER NOT NULL,
        e INTEGER NOT NULL,
        score INTEGER NOT NULL,
        category TEXT NOT NULL,
        minterm TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        total_records INTEGER NOT NULL,
        weak_count INTEGER NOT NULL,
        medium_count INTEGER NOT NULL,
        strong_count INTEGER NOT NULL,
        very_strong_count INTEGER NOT NULL,
        avg_length REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        password_masked TEXT NOT NULL,
        length INTEGER NOT NULL,
        a INTEGER NOT NULL,
        b INTEGER NOT NULL,
        c INTEGER NOT NULL,
        d INTEGER NOT NULL,
        e INTEGER NOT NULL,
        score INTEGER NOT NULL,
        category TEXT NOT NULL,
        minterm TEXT NOT NULL,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Check if baseline data exists
    cursor.execute("SELECT COUNT(*) FROM evaluations")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_baseline_evaluations(conn)

    conn.close()


def seed_baseline_evaluations(conn: sqlite3.Connection):
    """Seeds initial diverse password evaluations for immediate dashboard presentation."""
    samples = [
        "12345",
        "qwerty",
        "password",
        "welcome1",
        "Admin@123",
        "CyberSecurity#2026",
        "hello",
        "iloveyou",
        "supersecret",
        "Python3.12!",
        "EC2201$DLD",
        "Matrix_Reloaded_99",
        "LogicGate@FullAdder#1",
        "root",
        "admin",
        "Sunshine#2024",
        "WinterIsComing!",
        "AI_Robotics_42",
        "alpha123",
        "DeltaForce!",
        "Omega#Secure#Code7",
        "simplepass",
        "11111111",
        "P@ssw0rd2026",
        "BooleanAlgebra$101"
    ]

    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for pwd in samples:
        res = logic_engine.evaluate_password(pwd)
        cursor.execute("""
        INSERT INTO evaluations (password_masked, length, a, b, c, d, e, score, category, minterm, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res["password_masked"],
            res["length"],
            res["attributes"]["A"],
            res["attributes"]["B"],
            res["attributes"]["C"],
            res["attributes"]["D"],
            res["attributes"]["E"],
            res["score"],
            res["category"],
            res["minterm"],
            now_str
        ))

    conn.commit()


def save_evaluation(eval_result: Dict[str, Any]) -> int:
    """Saves a single password evaluation result to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO evaluations (password_masked, length, a, b, c, d, e, score, category, minterm, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_result["password_masked"],
        eval_result["length"],
        eval_result["attributes"]["A"],
        eval_result["attributes"]["B"],
        eval_result["attributes"]["C"],
        eval_result["attributes"]["D"],
        eval_result["attributes"]["E"],
        eval_result["score"],
        eval_result["category"],
        eval_result["minterm"],
        now_str
    ))
    eval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return eval_id


def get_recent_evaluations(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns the most recent password evaluations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, password_masked, length, a, b, c, d, e, score, category, minterm, created_at
    FROM evaluations
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_dataset(name: str, items: List[Dict[str, Any]]) -> int:
    """Saves an entire dataset batch and computes summary metadata."""
    if not items:
        return 0

    total_records = len(items)
    weak_count = sum(1 for it in items if it["category"] == "Weak")
    medium_count = sum(1 for it in items if it["category"] == "Medium")
    strong_count = sum(1 for it in items if it["category"] == "Strong")
    very_strong_count = sum(1 for it in items if it["category"] == "Very Strong")
    avg_length = round(sum(it["length"] for it in items) / total_records, 2)

    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO datasets (name, total_records, weak_count, medium_count, strong_count, very_strong_count, avg_length, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, total_records, weak_count, medium_count, strong_count, very_strong_count, avg_length, now_str))
    dataset_id = cursor.lastrowid

    for it in items:
        cursor.execute("""
        INSERT INTO dataset_items (dataset_id, password_masked, length, a, b, c, d, e, score, category, minterm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id,
            it["password_masked"],
            it["length"],
            it["attributes"]["A"] if isinstance(it["attributes"], dict) else it["a"],
            it["attributes"]["B"] if isinstance(it["attributes"], dict) else it["b"],
            it["attributes"]["C"] if isinstance(it["attributes"], dict) else it["c"],
            it["attributes"]["D"] if isinstance(it["attributes"], dict) else it["d"],
            it["attributes"]["E"] if isinstance(it["attributes"], dict) else it["e"],
            it["score"],
            it["category"],
            it["minterm"]
        ))

    conn.commit()
    conn.close()
    return dataset_id


def get_all_datasets() -> List[Dict[str, Any]]:
    """Lists all saved datasets."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, total_records, weak_count, medium_count, strong_count, very_strong_count, avg_length, created_at
    FROM datasets
    ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dataset_items(dataset_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches items for a specific dataset."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, password_masked, length, a, b, c, d, e, score, category, minterm
    FROM dataset_items
    WHERE dataset_id = ?
    LIMIT ?
    """, (dataset_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
