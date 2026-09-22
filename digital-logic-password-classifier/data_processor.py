"""
data_processor.py
Data processing, synthetic password dataset generation, CSV parsing,
and statistical analytics using Pandas and NumPy for EC2201 Digital Logic Project.
"""

import io
import csv
import random
import string
from collections import Counter
from typing import List, Dict, Any, Tuple
import numpy as np
import logic_engine
import database

# Character sets
UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


def generate_synthetic_passwords(
    total_count: int = 50,
    weak_pct: float = 0.25,
    medium_pct: float = 0.35,
    strong_pct: float = 0.25,
    very_strong_pct: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Generates realistic synthetic passwords tailored to specific digital logic criteria.
    Ensures a realistic mix of Weak, Medium, Strong, and Very Strong entries.
    """
    count_weak = int(total_count * weak_pct)
    count_med = int(total_count * medium_pct)
    count_strong = int(total_count * strong_pct)
    count_vstrong = max(1, total_count - (count_weak + count_med + count_strong))

    passwords = []

    # 1. Weak Passwords (Score 0 or 1): Short pins, single character sets
    weak_templates = [
        lambda: "".join(random.choices(DIGITS, k=random.randint(4, 6))),
        lambda: "".join(random.choices(LOWER, k=random.randint(4, 7))),
        lambda: "".join(random.choices(UPPER, k=random.randint(4, 6))),
        lambda: "pass" + "".join(random.choices(DIGITS, k=2)),
        lambda: "test"
    ]
    for _ in range(count_weak):
        pwd = random.choice(weak_templates)()
        passwords.append(pwd)

    # 2. Medium Passwords (Score 2 or 3): Moderate length, 2 or 3 criteria
    med_templates = [
        lambda: "".join(random.choices(LOWER, k=random.randint(8, 12))), # A, C (Score 2)
        lambda: "".join(random.choices(LOWER + DIGITS, k=random.randint(8, 11))), # A, C, D (Score 3)
        lambda: "".join(random.choices(UPPER + LOWER, k=random.randint(8, 10))), # A, B, C (Score 3)
        lambda: "Secure" + "".join(random.choices(LOWER, k=3)), # A, B, C (Score 3)
        lambda: "".join(random.choices(LOWER, k=6)) + "".join(random.choices(DIGITS, k=3)) # A, C, D (Score 3)
    ]
    for _ in range(count_med):
        pwd = random.choice(med_templates)()
        passwords.append(pwd)

    # 3. Strong Passwords (Score 4): 4 out of 5 criteria met
    strong_templates = [
        # Missing symbols: A, B, C, D
        lambda: "".join(random.choices(UPPER, k=2)) + "".join(random.choices(LOWER, k=6)) + "".join(random.choices(DIGITS, k=2)),
        # Missing uppercase: A, C, D, E
        lambda: "".join(random.choices(LOWER, k=6)) + "_" + "".join(random.choices(DIGITS, k=3)),
        # Missing numbers: A, B, C, E
        lambda: "Super" + "".join(random.choices(LOWER, k=4)) + "@" + "".join(random.choices(LOWER, k=2))
    ]
    for _ in range(count_strong):
        pwd = random.choice(strong_templates)()
        passwords.append(pwd)

    # 4. Very Strong Passwords (Score 5): All 5 criteria met (Length >= 8, A-Z, a-z, 0-9, Symbol)
    vstrong_templates = [
        lambda: random.choice(UPPER) + "".join(random.choices(LOWER, k=4)) + random.choice(SYMBOLS) + "".join(random.choices(DIGITS, k=3)) + random.choice(SYMBOLS),
        lambda: "DLD#" + "".join(random.choices(LOWER, k=4)) + "$" + "".join(random.choices(DIGITS, k=3)),
        lambda: "Logic" + "".join(random.choices(SYMBOLS, k=2)) + "".join(random.choices(UPPER, k=2)) + "".join(random.choices(DIGITS, k=4)),
        lambda: "".join(random.choices(UPPER + LOWER + DIGITS + SYMBOLS, k=random.randint(12, 16)))
    ]
    for _ in range(count_vstrong):
        pwd = random.choice(vstrong_templates)()
        # Ensure it has all 5
        while not all(logic_engine.extract_binary_attributes(pwd)[k] == 1 for k in ["A", "B", "C", "D", "E"]):
            pwd = random.choice(UPPER) + "".join(random.choices(LOWER, k=4)) + random.choice(SYMBOLS) + "".join(random.choices(DIGITS, k=3)) + random.choice(SYMBOLS)
        passwords.append(pwd)

    # Shuffle passwords
    random.shuffle(passwords)

    # Evaluate each password through the digital logic engine
    evaluated_items = []
    for pwd in passwords:
        res = logic_engine.evaluate_password(pwd)
        evaluated_items.append({
            "password_raw": pwd,
            "password_masked": res["password_masked"],
            "length": res["length"],
            "attributes": res["attributes"],
            "score": res["score"],
            "category": res["category"],
            "minterm": res["minterm"],
            "color": res["color"]
        })

    return evaluated_items


def parse_csv_dataset(file_content: str) -> List[Dict[str, Any]]:
    """
    Parses an uploaded CSV file containing password records.
    Supports either single-column ('password') or raw rows.
    """
    passwords = []
    stream = io.StringIO(file_content.strip())
    reader = csv.reader(stream)

    first_row = next(reader, None)
    if not first_row:
        return []

    # Check if header exists
    pwd_col_idx = 0
    headers_lower = [col.strip().lower() for col in first_row]
    if "password" in headers_lower:
        pwd_col_idx = headers_lower.index("password")
    else:
        # First row is actual data
        if first_row[0].strip():
            passwords.append(first_row[0].strip())

    for row in reader:
        if row and len(row) > pwd_col_idx and row[pwd_col_idx].strip():
            passwords.append(row[pwd_col_idx].strip())

    # Limit to reasonable upper bound (e.g. 1000 items)
    passwords = passwords[:1000]

    evaluated_items = []
    for pwd in passwords:
        res = logic_engine.evaluate_password(pwd)
        evaluated_items.append({
            "password_raw": pwd,
            "password_masked": res["password_masked"],
            "length": res["length"],
            "attributes": res["attributes"],
            "score": res["score"],
            "category": res["category"],
            "minterm": res["minterm"],
            "color": res["color"]
        })

    return evaluated_items


def generate_csv_string(items: List[Dict[str, Any]], mask: bool = False) -> str:
    """Generates formatted CSV string for download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Password", "Length", "A (Len>=8)", "B (Upper)", "C (Lower)", "D (Digit)", "E (Symbol)", "Score (0-5)", "Strength Category", "Minterm"])

    for i, it in enumerate(items, 1):
        pwd = it["password_masked"] if mask else it.get("password_raw", it.get("password_masked", ""))
        attrs = it.get("attributes", {})
        a = attrs.get("A", it.get("a", 0))
        b = attrs.get("B", it.get("b", 0))
        c = attrs.get("C", it.get("c", 0))
        d = attrs.get("D", it.get("d", 0))
        e = attrs.get("E", it.get("e", 0))

        writer.writerow([
            i,
            pwd,
            it["length"],
            a,
            b,
            c,
            d,
            e,
            it["score"],
            it["category"],
            it["minterm"]
        ])

    return output.getvalue()


def compute_analytics(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Uses Pandas & NumPy to calculate comprehensive statistical metrics
    for Chart.js and summary metric cards on the Dashboard.
    """
    if not items:
        return {
            "total": 0,
            "categories": {"Weak": 0, "Medium": 0, "Strong": 0, "Very Strong": 0},
            "percentages": {"Weak": 0, "Medium": 0, "Strong": 0, "Very Strong": 0},
            "avg_length": 0.0,
            "secure_percentage": 0.0,
            "attributes_rate": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0},
            "scores_histogram": [0, 0, 0, 0, 0, 0]
        }

    total = len(items)
    lengths = []
    scores = []
    categories = []
    a_vals = []
    b_vals = []
    c_vals = []
    d_vals = []
    e_vals = []

    for it in items:
        lengths.append(it["length"])
        scores.append(it["score"])
        categories.append(it["category"])
        attrs = it.get("attributes", {})
        a_vals.append(attrs.get("A", it.get("a", 0)))
        b_vals.append(attrs.get("B", it.get("b", 0)))
        c_vals.append(attrs.get("C", it.get("c", 0)))
        d_vals.append(attrs.get("D", it.get("d", 0)))
        e_vals.append(attrs.get("E", it.get("e", 0)))

    cat_counts = Counter(categories)
    weak_cnt = int(cat_counts.get("Weak", 0))
    med_cnt = int(cat_counts.get("Medium", 0))
    strong_cnt = int(cat_counts.get("Strong", 0))
    vstrong_cnt = int(cat_counts.get("Very Strong", 0))

    avg_len = float(np.round(np.mean(lengths), 2)) if total > 0 else 0.0
    secure_ratio = float(np.round(((strong_cnt + vstrong_cnt) / total) * 100, 1)) if total > 0 else 0.0

    attr_rate = {
        "A": float(np.round((sum(a_vals) / total) * 100, 1)),
        "B": float(np.round((sum(b_vals) / total) * 100, 1)),
        "C": float(np.round((sum(c_vals) / total) * 100, 1)),
        "D": float(np.round((sum(d_vals) / total) * 100, 1)),
        "E": float(np.round((sum(e_vals) / total) * 100, 1)),
    }

    score_counts = Counter(scores)
    scores_hist = [int(score_counts.get(s, 0)) for s in range(6)]

    return {
        "total": total,
        "categories": {
            "Weak": weak_cnt,
            "Medium": med_cnt,
            "Strong": strong_cnt,
            "Very Strong": vstrong_cnt
        },
        "percentages": {
            "Weak": round((weak_cnt / total) * 100, 1),
            "Medium": round((med_cnt / total) * 100, 1),
            "Strong": round((strong_cnt / total) * 100, 1),
            "Very Strong": round((vstrong_cnt / total) * 100, 1)
        },
        "avg_length": avg_len,
        "secure_percentage": secure_ratio,
        "attributes_rate": attr_rate,
        "scores_histogram": scores_hist
    }


def seed_sample_dataset():
    """Generates and writes a default sample dataset CSV file in sample_data directory."""
    sample_file = "C:\\Users\\ASUS TUF\\.gemini\\antigravity\\scratch\\digital-logic-password-classifier\\sample_data\\sample_passwords.csv"
    items = generate_synthetic_passwords(total_count=60)
    csv_str = generate_csv_string(items, mask=False)
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(csv_str)
    # Also save to SQLite dataset table
    database.save_dataset("Default EC2201 Benchmark Dataset", items)
    return sample_file
