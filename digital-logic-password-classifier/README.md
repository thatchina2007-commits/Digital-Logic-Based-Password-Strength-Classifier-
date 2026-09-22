# Digital Logic Based Password Strength Classifier
### EC2201 Digital Logic Design Mini Project

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Course](https://img.shields.io/badge/Course-EC2201%20Digital%20Logic%20Design-purple.svg)](#)
[![Status](https://img.shields.io/badge/Project%20Status-Complete%20%26%20Verified-success.svg)](#)

A modern, responsive, cyber-themed web application developed for the **EC2201 Digital Logic Design** mini project curriculum. This application models password entropy and security evaluation deterministically through fundamental digital hardware concepts: **Boolean Variables**, **Truth Tables ($2^5=32$ states)**, **Full Adder & Half Adder Networks (Popcount)**, and **3-bit Magnitude Comparators**.

---

## 🔬 1. Digital Logic Foundation & Hardware Architecture

In computer architecture and VLSI design, passwords can be transformed into a 5-bit binary input vector:

$$\mathbf{X} = [A, B, C, D, E] \in \{0, 1\}^5$$

### Binary Attribute Definitions
- **$A$ (Length Criterion)**: $A = 1 \iff \text{length}(P) \ge 8$, else $0$.
- **$B$ (Uppercase Criterion)**: $B = 1 \iff \exists c \in P \text{ s.t. } c \in [A-Z]$, else $0$.
- **$C$ (Lowercase Criterion)**: $C = 1 \iff \exists c \in P \text{ s.t. } c \in [a-z]$, else $0$.
- **$D$ (Numerical Criterion)**: $D = 1 \iff \exists c \in P \text{ s.t. } c \in [0-9]$, else $0$.
- **$E$ (Special Symbol Criterion)**: $E = 1 \iff \exists c \in P \text{ s.t. } c \notin [A-Za-z0-9\s]$, else $0$.

### 5-Bit Adder (Popcount) Circuit
To compute the strength score $Score = A + B + C + D + E \in [0, 5]$, a tree of adders is synthesized:
1. **Stage 1**:
   - $\text{FA}_1(A, B, C) \implies S_{1a} = A \oplus B \oplus C, \quad C_{1a} = AB + C(A \oplus B)$
   - $\text{HA}_1(D, E) \implies S_{2a} = D \oplus E, \quad C_{2a} = DE$
2. **Stage 2 (LSB Generator)**:
   - $\text{HA}_2(S_{1a}, S_{2a}) \implies S_0 = S_{1a} \oplus S_{2a}, \quad C_3 = S_{1a} \cdot S_{2a}$
3. **Stage 3 (Carries Accumulator)**:
   - $\text{FA}_2(C_{1a}, C_{2a}, C_3) \implies S_1 = C_{1a} \oplus C_{2a} \oplus C_3, \quad S_2 = C_{1a} C_{2a} + C_3 (C_{1a} \oplus C_{2a})$

The net 3-bit binary output is $(S_2 S_1 S_0)_2$, where $\text{Value} = 4S_2 + 2S_1 + S_0$.

### 3-Bit Magnitude Comparator & Classification Decoder
Outputs are categorized through Boolean expressions:
- **Weak ($W$)**: $\text{Score} \in \{0, 1\} \implies W = S_2' \cdot S_1'$
- **Medium ($M$)**: $\text{Score} \in \{2, 3\} \implies M = S_2' \cdot S_1$
- **Strong ($S$)**: $\text{Score} = 4 \implies S = S_2 \cdot S_1' \cdot S_0'$
- **Very Strong ($V$)**: $\text{Score} = 5 \implies V = S_2 \cdot S_1' \cdot S_0 \equiv A \cdot B \cdot C \cdot D \cdot E$

---

## 🚀 2. Quick Setup & Execution

### Prerequisites
- Python 3.10+ installed
- Pip installed

### Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd "C:\Users\ASUS TUF\.gemini\antigravity\scratch\digital-logic-password-classifier"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask web server:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🌐 3. Website Pages & Modules

| Module / Page | URL Path | Key Functionality |
| :--- | :--- | :--- |
| **Home Page** | `/` | Hero section, interactive live preview, features overview, EC2201 syllabus mapping. |
| **About Project** | `/about` | Problem statement, EC2201 objectives, hardware circuit architecture diagram, workflow. |
| **Password Classifier** | `/classifier` | Live character-by-character analysis, 5-bit LED switches, adder trace, meter, screenshot report. |
| **Digital Logic Analysis** | `/logic-analysis` | Complete 32-row Truth table, K-Map SOP/POS formulas, interactive SVG gate schematics. |
| **Test Cases** | `/test-cases` | 10 Normal + 5 Edge test cases, batch test runner with pass/fail verification & timing. |
| **Dataset Management** | `/dataset` | Synthetic dataset generation (50-500 entries), CSV upload, interactive data table, CSV download. |
| **Dashboard** | `/dashboard` | Interactive Chart.js charts (Category distribution, Score histogram, attribute rates, security ratio). |
| **Report Generator** | `/report` | Formal project report sheet with printable styling, instant PDF and CSV downloads. |
| **Deliverables & Viva Hub** | `/deliverables` | Source code ZIP download, documentation, sample CSV, and comprehensive Viva Q&A guide. |

---

## 📊 4. Test Cases Verification

All 15 test cases (10 Normal + 5 Edge) have been verified:
- **Accuracy**: 100.0% (15/15 passed)
- **Edge Cases Tested**: Empty string ($m_0$), all-whitespace string, special symbols only, mono-character 128-char string, unicode/emoji input.

To re-run test suite via CLI:
```bash
python -c "import test_cases; r = test_cases.run_all_test_cases(); print(f'Passed {r[\"passed\"]}/{r[\"total\"]} tests ({r[\"accuracy_rate\"]}%)')"
```

---

## 👨‍💻 5. Academic & Viva Voce Quick Reference

### Sample Viva Questions:
1. **Q: Why convert password evaluation into a digital logic problem?**
   *A:* Traditional rules often use complex heuristics. Mapping criteria into Boolean variables $(A, B, C, D, E)$ allows deterministic combinational logic verification, verifiable truth tables, and hardware synthesis suitability (e.g., FPGA or ASIC security coprocessor).
2. **Q: What is the significance of the 32 minterms?**
   *A:* With 5 binary variables, there are exactly $2^5 = 32$ possible input states ($m_0$ to $m_{31}$). Each state represents a specific combination of criteria, mapping to an exact Hamming weight from 0 to 5.
3. **Q: How does the Popcount adder circuit work?**
   *A:* Full Adders and Half Adders perform bit addition of the 5 input bits to yield a 3-bit binary sum $(S_2 S_1 S_0)_2$. A 3-bit comparator then classifies the score into 4 security levels.

---
Developed for **EC2201 Digital Logic Design Mini Project** © 2026.
