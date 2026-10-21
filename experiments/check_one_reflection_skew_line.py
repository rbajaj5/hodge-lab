#!/usr/bin/env python3
"""Independent F_11 line substitution check for one-reflection-skew.

Uses the exact term list from the protected record.
Variables: X0, X1, X2, Y0, Y1, Y2.
Line: [s : t : 6s+2t : 3s+2t : 2s : 7s+8t] over F_11.
"""
from sympy import symbols

s, t = symbols("s t")
X0, X1, X2, Y0, Y1, Y2 = symbols("X0 X1 X2 Y0 Y1 Y2")

# Exact terms from record.json (coefficient, multi-degree in X0,X1,X2,Y0,Y1,Y2)
terms = [
    ("1", [6, 0, 0, 0, 0, 0]),
    ("1", [3, 1, 0, 1, 1, 0]),
    ("1/7", [1, 1, 0, 3, 1, 0]),
    ("-1/7", [1, 1, 0, 1, 3, 0]),
    ("1", [0, 6, 0, 0, 0, 0]),
    ("1", [0, 3, 1, 1, 1, 0]),
    ("1", [0, 0, 6, 0, 0, 0]),
    ("1", [0, 0, 0, 6, 0, 0]),
    ("1", [0, 0, 0, 0, 6, 0]),
    ("1", [0, 0, 0, 0, 0, 6]),
]

vars_ = [X0, X1, X2, Y0, Y1, Y2]
line = [s, t, 6*s + 2*t, 3*s + 2*t, 2*s, 7*s + 8*t]
subs = dict(zip(vars_, line))

# Build 7F (integer coefficients)
F7 = 0
for coeff_str, multi in terms:
    if coeff_str == "1":
        coeff = 1
    elif coeff_str == "1/7":
        coeff = 1
    elif coeff_str == "-1/7":
        coeff = -1
    else:
        raise ValueError(coeff_str)
    monom = 1
    for v, e in zip(vars_, multi):
        monom *= v**e
    if coeff_str in ("1/7", "-1/7"):
        F7 += coeff * monom
    else:
        F7 += 7 * coeff * monom

F_on_line = F7.subs(subs).expand()

# Extract coefficients of s^6 ... t^6
monoms = [(6, 0), (5, 1), (4, 2), (3, 3), (2, 4), (1, 5), (0, 6)]
coeffs_mod11 = []
for a, b in monoms:
    c = F_on_line.coeff(s, a).coeff(t, b)
    coeffs_mod11.append(int(c % 11))

print("7F coefficients mod 11 (s^6, s^5 t, ..., t^6):", coeffs_mod11)
print("All zero?", all(c == 0 for c in coeffs_mod11))
if any(coeffs_mod11):
    raise ValueError("The proposed line is not contained in the sextic over F_11")

# Source A = X0**3 * Y0**3
A = X0**3 * Y0**3
A_on_line = A.subs(subs).expand()
coeffs_A = []
for a, b in monoms:
    c = A_on_line.coeff(s, a).coeff(t, b)
    coeffs_A.append(int(c % 11))
print("A restriction mod 11:", coeffs_A)
print("Identically zero?", all(c == 0 for c in coeffs_A))
print("Value at [1:0]:", int(A_on_line.subs({s: 1, t: 0}) % 11))
print("A polynomial:", A_on_line)
if coeffs_A != [5, 10, 3, 8, 0, 0, 0]:
    raise ValueError("Unexpected source restriction on the fixed line")
print("PASS: exact line incidence and source restriction")
