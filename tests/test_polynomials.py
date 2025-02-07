import sys
sys.path.insert(1, "./")
import pyaces as pyc

"""
Test for the Polynomial class in the pyaces module.

This test demonstrates the functionality of the Polynomial class, including:

1. Testing the `divmod()` method for polynomial division:
   - Verifying that the polynomials `a` and `b` satisfy the equation `a = bq + r`, where `q` is the quotient and `r` is the remainder.
   - Ensuring the remainder satisfies `bq + r - a = Polynomial([])`.

2. Testing the `extended_gcd()` method for computing the extended greatest common divisor:
   - Verifying that the polynomials `u`, `v`, and `w` satisfy the equation `u = a * v + w * b`.
   - Ensuring that `(a * v + w * b) % f = Polynomial([])` for a composite polynomial `f`.

Inputs:
- Polynomials `a`, `b`, `p_0`, `p_1`, `p_2`, and `p_3`.

Outputs:
- Printed verification of each step, showing intermediate results and values.
- Assertions to ensure correctness of computations, gcd conditions, and modular arithmetic properties.
"""

# Step 1: Test the `divmod()` method
print("==== Polynomial.divmod() ====")
a = pyc.Polynomial([1, 1, 0, 1, 0, 1, 0, 1, 0, 1])
b = pyc.Polynomial([1, 0, 1, 1, 0, 1, 1, 1, 1, 1])
print(f"a = {a}")
print(f"b = {b}")
print("~~~~~ compute a = bq + r ~~~~~")
q, r = a.divmod(b)
print("q =", q)
print("r =", r)
print("bq + r =", b * q + r)

# Verify the divmod equation
assert b * q + r == a, "Error in divmod()"
print("bq + r - a =", b * q + r - a)
assert b * q + r - a == pyc.Polynomial([]), "Error in __sub__()"

# Step 2: Test the `extended_gcd()` method
print("\n==== Polynomial.extended_gcd() ====")

# Create composite polynomial `f` from p_0, p_1, p_2, and p_3
p_0 = pyc.Polynomial([14, 1])
p_1 = pyc.Polynomial([45, 3])
p_2 = pyc.Polynomial([1, 6])
p_3 = pyc.Polynomial([25, 2])
f = p_0 * p_1 * p_2 * p_3

# Define `a` and `b` as multiples of `f`
a_ = pyc.Polynomial([1, 1, 0, 1, 2])
b_ = pyc.Polynomial([0, 1, 1, 0, 3])
a = f * a_
b = f * b_

# Display inputs
print(f"f = {f}")
print(f"a = {f} * {a_}")
print(f"  = {a}")
print(f"b = {f} * {b_}")
print(f"  = {b}")

# Compute extended GCD
print("~~~~~ compute u = a * v + w * b ~~~~~")
u, v, w = a.extended_gcd(b)
print(f"u = {u}")
print(f"v = {v}")
print(f"w = {w}")
print(f"a * v + w * b = {a * v + w * b}")

# Verify the extended GCD equation
assert a * v + w * b == u, "Error in extended_gcd()"

# Verify modular condition
print(f"a * v + w * b (mod f) = {(a * v + w * b) % f}")
assert (a * v + w * b) % f == pyc.Polynomial([]), "Error in __sub__() or __mod__()"
