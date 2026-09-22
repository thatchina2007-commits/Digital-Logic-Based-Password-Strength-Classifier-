"""
logic_engine.py
EC2201 Digital Logic Design - Password Strength Classifier Core Engine
Implements Boolean attribute extraction, gate-level Full Adder & Half Adder circuit emulation,
3-bit magnitude comparator, 32-state Truth Table generation, and Karnaugh-map expressions.
"""

import re
from typing import Dict, Any, List, Tuple


def extract_binary_attributes(password: str) -> Dict[str, Any]:
    """
    Extracts 5 binary attributes from raw password input:
    A: Length >= 8 (0 or 1)
    B: Contains Uppercase letter [A-Z] (0 or 1)
    C: Contains Lowercase letter [a-z] (0 or 1)
    D: Contains Digit [0-9] (0 or 1)
    E: Contains Special Character (0 or 1)
    """
    p_str = "" if password is None else str(password)
    
    a = 1 if len(p_str) >= 8 else 0
    b = 1 if re.search(r'[A-Z]', p_str) is not None else 0
    c = 1 if re.search(r'[a-z]', p_str) is not None else 0
    d = 1 if re.search(r'[0-9]', p_str) is not None else 0
    # Any character not alphanumeric and not standard whitespace can be special, or standard symbols
    e = 1 if re.search(r'[^A-Za-z0-9\s]', p_str) is not None else 0

    return {
        "A": a,
        "B": b,
        "C": c,
        "D": d,
        "E": e,
        "length": len(p_str),
        "details": {
            "A_desc": f"Length ({len(p_str)}) >= 8",
            "B_desc": "Contains Uppercase [A-Z]",
            "C_desc": "Contains Lowercase [a-z]",
            "D_desc": "Contains Number [0-9]",
            "E_desc": "Contains Special Symbol [!@#$%^&*...]"
        }
    }


def simulate_half_adder(x: int, y: int) -> Tuple[int, int]:
    """
    Half Adder (HA):
    Sum = X XOR Y
    Carry = X AND Y
    """
    s = x ^ y
    c = x & y
    return s, c


def simulate_full_adder(x: int, y: int, cin: int) -> Tuple[int, int]:
    """
    Full Adder (FA):
    Sum = X XOR Y XOR Cin
    Cout = (X AND Y) OR (Cin AND (X XOR Y))
    """
    s = x ^ y ^ cin
    cout = (x & y) | (cin & (x ^ y))
    return s, cout


def simulate_popcount_circuit(a: int, b: int, c: int, d: int, e: int) -> Dict[str, Any]:
    """
    Hardware realization of 5-input population count (adder tree):
    Stage 1:
      FA1(A, B, C) -> S1a, C1a
      HA1(D, E)    -> S2a, C2a
    Stage 2:
      HA2(S1a, S2a)-> S0, C3   (S0 is LSB of final sum)
    Stage 3:
      FA2(C1a, C2a, C3) -> S1, S2 (S1 is bit 1, S2 is MSB bit 2)
    
    Total binary output: S2 S1 S0
    Integer value: 4*S2 + 2*S1 + S0 = A + B + C + D + E in [0, 5]
    """
    # Stage 1
    s1a, c1a = simulate_full_adder(a, b, c)
    s2a, c2a = simulate_half_adder(d, e)

    # Stage 2: Compute LSB S0
    s0, c3 = simulate_half_adder(s1a, s2a)

    # Stage 3: Compute S1 and S2 (Carries sum)
    s1, s2 = simulate_full_adder(c1a, c2a, c3)

    integer_score = (s2 << 2) | (s1 << 1) | s0

    circuit_trace = {
        "stage1": {
            "FA1": {"inputs": {"A": a, "B": b, "C": c}, "Sum": s1a, "Carry": c1a},
            "HA1": {"inputs": {"D": d, "E": e}, "Sum": s2a, "Carry": c2a}
        },
        "stage2": {
            "HA2": {"inputs": {"S1a": s1a, "S2a": s2a}, "S0": s0, "C3": c3}
        },
        "stage3": {
            "FA2": {"inputs": {"C1a": c1a, "C2a": c2a, "C3": c3}, "S1": s1, "S2": s2}
        },
        "binary_output": f"{s2}{s1}{s0}",
        "bits": {"S2": s2, "S1": s1, "S0": s0},
        "score": integer_score
    }

    return circuit_trace


def comparator_classify(s2: int, s1: int, s0: int) -> Dict[str, Any]:
    """
    3-Bit Magnitude Comparator & Classification Decoder:
    Inputs: (S2, S1, S0) representing binary values 000_2 to 101_2 (0 to 5)
    
    Digital logic equations:
      Weak (W):       S2' AND S1'               -> (score 0 or 1)
      Medium (M):     S2' AND S1                -> (score 2 or 3)
      Strong (S):     S2 AND S1' AND S0'        -> (score 4)
      Very Strong (V): S2 AND S1' AND S0        -> (score 5)
    """
    score = (s2 << 2) | (s1 << 1) | s0

    w = 1 if (s2 == 0 and s1 == 0) else 0
    m = 1 if (s2 == 0 and s1 == 1) else 0
    s = 1 if (s2 == 1 and s1 == 0 and s0 == 0) else 0
    v = 1 if (s2 == 1 and s1 == 0 and s0 == 1) else 0

    if v == 1:
        category = "Very Strong"
        color = "emerald"
        hex_color = "#00f5a0"
        description = "Maximum resilience. Satisfies all 5 security logic conditions (A, B, C, D, E)."
        percentage = 100
    elif s == 1:
        category = "Strong"
        color = "cyan"
        hex_color = "#00d2ff"
        description = "High security. Fulfills 4 out of 5 criteria. Adding the 1 missing attribute achieves optimal security."
        percentage = 80
    elif m == 1:
        category = "Medium"
        color = "amber"
        hex_color = "#f6d365"
        description = "Moderate entropy. Fulfills 2-3 criteria. Vulnerable to targeted dictionary or pattern attacks."
        percentage = score * 20  # 40% or 60%
    else:
        category = "Weak"
        color = "rose"
        hex_color = "#ff416c"
        description = "Critical vulnerability. Fulfills <= 1 criterion. Trivial to crack via brute force or dictionary."
        percentage = max(10, score * 20)

    return {
        "score": score,
        "category": category,
        "color": color,
        "hex_color": hex_color,
        "percentage": percentage,
        "description": description,
        "decoder_signals": {
            "Weak_W": w,
            "Medium_M": m,
            "Strong_S": s,
            "VeryStrong_V": v
        }
    }


def evaluate_password(password: str) -> Dict[str, Any]:
    """
    Comprehensive pipeline:
    Raw String -> Binary Attributes -> Adder Circuit -> Comparator -> Final Category
    """
    attributes = extract_binary_attributes(password)
    a = attributes["A"]
    b = attributes["B"]
    c = attributes["C"]
    d = attributes["D"]
    e = attributes["E"]

    circuit = simulate_popcount_circuit(a, b, c, d, e)
    bits = circuit["bits"]
    classification = comparator_classify(bits["S2"], bits["S1"], bits["S0"])

    # Compute decimal minterm index: (A*16 + B*8 + C*4 + D*2 + E*1)
    minterm_idx = (a << 4) | (b << 3) | (c << 2) | (d << 1) | e

    # Recommendations for missing logic flags
    missing_criteria = []
    if a == 0:
        missing_criteria.append("Increase length to at least 8 characters (Activate Flag A)")
    if b == 0:
        missing_criteria.append("Include uppercase characters A-Z (Activate Flag B)")
    if c == 0:
        missing_criteria.append("Include lowercase characters a-z (Activate Flag C)")
    if d == 0:
        missing_criteria.append("Include numerical digits 0-9 (Activate Flag D)")
    if e == 0:
        missing_criteria.append("Include special symbols like @, #, $, ! (Activate Flag E)")

    return {
        "password_masked": mask_password(password),
        "length": attributes["length"],
        "attributes": {
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "E": e
        },
        "attribute_details": attributes["details"],
        "circuit_trace": circuit,
        "score": classification["score"],
        "category": classification["category"],
        "color": classification["color"],
        "hex_color": classification["hex_color"],
        "percentage": classification["percentage"],
        "description": classification["description"],
        "decoder_signals": classification["decoder_signals"],
        "minterm": f"m{minterm_idx}",
        "minterm_idx": minterm_idx,
        "missing_criteria": missing_criteria
    }


def mask_password(password: str) -> str:
    """Masks all but the first and last character for privacy while showing length."""
    if not password:
        return "[Empty]"
    p = str(password)
    if len(p) <= 2:
        return "*" * len(p)
    return p[0] + ("*" * (len(p) - 2)) + p[-1]


def generate_truth_table() -> List[Dict[str, Any]]:
    """
    Generates the complete 2^5 = 32 row truth table for EC2201 presentation.
    Variables: A, B, C, D, E.
    Outputs: S2, S1, S0, Score, Category, Minterm
    """
    rows = []
    for i in range(32):
        a = (i >> 4) & 1
        b = (i >> 3) & 1
        c = (i >> 2) & 1
        d = (i >> 1) & 1
        e = i & 1

        circuit = simulate_popcount_circuit(a, b, c, d, e)
        bits = circuit["bits"]
        classification = comparator_classify(bits["S2"], bits["S1"], bits["S0"])

        rows.append({
            "minterm": f"m{i}",
            "index": i,
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "E": e,
            "S2": bits["S2"],
            "S1": bits["S1"],
            "S0": bits["S0"],
            "score": classification["score"],
            "category": classification["category"],
            "color": classification["color"],
            "hex_color": classification["hex_color"]
        })
    return rows


def get_boolean_analysis() -> Dict[str, Any]:
    """
    Returns canonical SOP / POS formulas and K-Map grouping for viva discussion.
    """
    # Minterms partitioned by category
    table = generate_truth_table()
    weak_minterms = [r["index"] for r in table if r["category"] == "Weak"]
    medium_minterms = [r["index"] for r in table if r["category"] == "Medium"]
    strong_minterms = [r["index"] for r in table if r["category"] == "Strong"]
    very_strong_minterms = [r["index"] for r in table if r["category"] == "Very Strong"]

    return {
        "inputs": [
            {"var": "A", "meaning": "Length >= 8"},
            {"var": "B", "meaning": "Contains Uppercase letter [A-Z]"},
            {"var": "C", "meaning": "Contains Lowercase letter [a-z]"},
            {"var": "D", "meaning": "Contains Number [0-9]"},
            {"var": "E", "meaning": "Contains Special Character"}
        ],
        "adder_equations": {
            "half_adder": "Sum = X ⊕ Y, Carry = X · Y",
            "full_adder": "Sum = X ⊕ Y ⊕ Cin, Cout = (X · Y) + (Cin · (X ⊕ Y))",
            "score_binary": "Score = (S2 · 2²) + (S1 · 2¹) + (S0 · 2⁰)"
        },
        "comparator_equations": {
            "weak": "W = S2' · S1'",
            "medium": "M = S2' · S1",
            "strong": "S = S2 · S1' · S0'",
            "very_strong": "V = S2 · S1' · S0 = A · B · C · D · E"
        },
        "minterm_canonical_sop": {
            "weak": f"Σ m({', '.join(map(str, weak_minterms))})",
            "medium": f"Σ m({', '.join(map(str, medium_minterms))})",
            "strong": f"Σ m({', '.join(map(str, strong_minterms))})",
            "very_strong": f"Σ m({', '.join(map(str, very_strong_minterms))})"
        },
        "minterm_counts": {
            "weak": len(weak_minterms),
            "medium": len(medium_minterms),
            "strong": len(strong_minterms),
            "very_strong": len(very_strong_minterms),
            "total": 32
        }
    }
