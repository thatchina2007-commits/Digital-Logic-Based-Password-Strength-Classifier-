"""
test_cases.py
Pre-defined test suite for EC2201 Digital Logic Design:
- 10 Normal Test Cases covering all 4 strength categories (Weak, Medium, Strong, Very Strong)
- 5 Edge / Fault Test Cases (empty, whitespace, all-symbols, ultra-long, unicode/emojis)
"""

from typing import List, Dict, Any
import logic_engine

NORMAL_TEST_CASES = [
    {
        "id": "TC_N01",
        "name": "Single Digit Pin",
        "password": "7",
        "expected_score": 1,
        "expected_category": "Weak",
        "description": "Short numeric input (length < 8). Only Flag D is active.",
        "type": "Normal"
    },
    {
        "id": "TC_N02",
        "name": "Sequential Numbers",
        "password": "123456",
        "expected_score": 1,
        "expected_category": "Weak",
        "description": "Short numeric sequence (length < 8). Only Flag D is active.",
        "type": "Normal"
    },
    {
        "id": "TC_N03",
        "name": "Single Word Lowercase",
        "password": "secret",
        "expected_score": 1,
        "expected_category": "Weak",
        "description": "Short dictionary word without uppercase/numbers/symbols. Only Flag C is active.",
        "type": "Normal"
    },
    {
        "id": "TC_N04",
        "name": "Common Dictionary Word",
        "password": "password",
        "expected_score": 2,
        "expected_category": "Medium",
        "description": "Length >= 8 and lowercase. Flags A and C are active.",
        "type": "Normal"
    },
    {
        "id": "TC_N05",
        "name": "Uppercase and Lowercase Word",
        "password": "DigitalLogic",
        "expected_score": 3,
        "expected_category": "Medium",
        "description": "Length >= 8, Uppercase, and Lowercase. Flags A, B, and C are active.",
        "type": "Normal"
    },
    {
        "id": "TC_N06",
        "name": "Word with Numbers",
        "password": "welcome2026",
        "expected_score": 3,
        "expected_category": "Medium",
        "description": "Length >= 8, Lowercase, and Numbers. Flags A, C, and D are active.",
        "type": "Normal"
    },
    {
        "id": "TC_N07",
        "name": "Upper, Lower and Number",
        "password": "AdminLogin2026",
        "expected_score": 4,
        "expected_category": "Strong",
        "description": "Length >= 8, Uppercase, Lowercase, and Numbers. Missing only special character. Flags A, B, C, D are active.",
        "type": "Normal"
    },
    {
        "id": "TC_N08",
        "name": "Word with Symbols and Digits",
        "password": "cyber_vault_99",
        "expected_score": 4,
        "expected_category": "Strong",
        "description": "Length >= 8, Lowercase, Numbers, and Special character. Missing uppercase. Flags A, C, D, E are active.",
        "type": "Normal"
    },
    {
        "id": "TC_N09",
        "name": "Full Entropy Secure Password",
        "password": "Logic#Design$2026",
        "expected_score": 5,
        "expected_category": "Very Strong",
        "description": "All 5 digital logic criteria satisfied (A, B, C, D, E = 1). Binary 101_2.",
        "type": "Normal"
    },
    {
        "id": "TC_N10",
        "name": "Complex Hardware Key",
        "password": "EC2201!DLD*Project",
        "expected_score": 5,
        "expected_category": "Very Strong",
        "description": "Optimal password complexity meeting all requirements with high entropy.",
        "type": "Normal"
    }
]

EDGE_TEST_CASES = [
    {
        "id": "TC_E01",
        "name": "Empty Input String",
        "password": "",
        "expected_score": 0,
        "expected_category": "Weak",
        "description": "Zero length null input. All binary flags A=B=C=D=E=0. Tests minterm m0.",
        "type": "Edge"
    },
    {
        "id": "TC_E02",
        "name": "Whitespaces Only",
        "password": "        ",
        "expected_score": 1,
        "expected_category": "Weak",
        "description": "8 spaces. Only Flag A (Length >= 8) is active. Flags B, C, D, E remain 0.",
        "type": "Edge"
    },
    {
        "id": "TC_E03",
        "name": "Special Symbols Only",
        "password": "!@#$%^&*()_+",
        "expected_score": 2,
        "expected_category": "Medium",
        "description": "Only symbols with length >= 8. Flags A and E are active. B, C, D are 0.",
        "type": "Edge"
    },
    {
        "id": "TC_E04",
        "name": "Extreme Length Monoculture",
        "password": "A" * 128,
        "expected_score": 2,
        "expected_category": "Medium",
        "description": "128 identical uppercase characters. Satisfies Length (A) and Uppercase (B), but lacks diversity.",
        "type": "Edge"
    },
    {
        "id": "TC_E05",
        "name": "Unicode & Emojis Boundary",
        "password": "Admin🔑Lock#99",
        "expected_score": 5,
        "expected_category": "Very Strong",
        "description": "Contains Upper, Lower, Numbers, Special characters and Unicode glyphs. Evaluates robustly.",
        "type": "Edge"
    }
]


def run_all_test_cases() -> Dict[str, Any]:
    """
    Executes all 15 test cases through the logic engine and generates
    detailed pass/fail verification and timing logs.
    """
    all_cases = NORMAL_TEST_CASES + EDGE_TEST_CASES
    results = []
    passed_count = 0

    for tc in all_cases:
        eval_result = logic_engine.evaluate_password(tc["password"])
        actual_score = eval_result["score"]
        actual_category = eval_result["category"]

        is_passed = (actual_score == tc["expected_score"]) and (actual_category == tc["expected_category"])
        if is_passed:
            passed_count += 1

        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "type": tc["type"],
            "password_sample": tc["password"] if len(tc["password"]) < 25 else tc["password"][:12] + "..." + tc["password"][-8:],
            "length": eval_result["length"],
            "inputs": eval_result["attributes"],
            "binary_vector": f"{eval_result['attributes']['A']}{eval_result['attributes']['B']}{eval_result['attributes']['C']}{eval_result['attributes']['D']}{eval_result['attributes']['E']}",
            "minterm": eval_result["minterm"],
            "adder_binary": eval_result["circuit_trace"]["binary_output"],
            "expected_score": tc["expected_score"],
            "actual_score": actual_score,
            "expected_category": tc["expected_category"],
            "actual_category": actual_category,
            "status": "PASS" if is_passed else "FAIL",
            "description": tc["description"]
        })

    total = len(all_cases)
    return {
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "accuracy_rate": round((passed_count / total) * 100, 1),
        "results": results,
        "normal_cases_count": len(NORMAL_TEST_CASES),
        "edge_cases_count": len(EDGE_TEST_CASES)
    }
