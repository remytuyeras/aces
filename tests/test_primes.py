import sys

sys.path.insert(1, "./")
import pyaces as pyc


def test_primes():
    """
    Test for the Primes class in the pyaces module.

    This test demonstrates the functionality of the Primes class, including:
    1. Initializing the Primes class with an upper bound `B` to generate primes and precompute factorizations.
    2. Factorizing numbers to verify the correctness of the `factorize()` method.
    3. Using the `find_candidates()` method to find a prime number `q` such that:
    - q >= B
    - sqrt(q) matches sqrt(B)
    - q meets additional constraints, such as having specific units and zero divisors in Z_q.

    Inputs:
    - B: The upper bound for prime generation and factorizations.
    - x: Numbers to factorize.
    - zero_divisors: Prime elements to exclude as candidates for q in Z_q.

    Outputs:
    - Printed verification of `factorize()` correctness.
    - A prime `q` satisfying the specified criteria.
    """

    # Step 1: Initialize the Primes class with an upper bound `B`
    print("==== Primes.__init__() ====")
    B = 47601551  # The upper bound for generating primes and finding `q`
    primes = pyc.Primes(B)  # Initialize Primes with `B` as the upper bound
    print(f"B = {primes.upperbound}")
    print(f"factorize(B) = {primes.factorization}")

    # Step 2: Test the factorization functionality
    print("\n==== Primes.factorize() ====")
    # Test case 1: Factorize a composite number `x = 7 * 9 * 51`
    x = 7 * 9 * 51
    f = primes.factorize(x)
    print(f"factorize({x} < B) = {f}")
    # Verify the factorization result
    assert f == {3: 3, 7: 1, 17: 1}, "Error in factorize()"

    # Test case 2: Factorize another composite number `x = 7919 * 17`
    x = 7919 * 17
    f = primes.factorize(x)
    print(f"factorize({x} < B) = {f}")
    # Verify the factorization result
    assert f == {17: 1, 7919: 1}, "Error in factorize()"

    # Test case 3: Edge cases for factorization
    assert primes.factorize(0) is None, (
        "Error in factorize()"
    )  # Factorization of 0 should return None
    assert primes.factorize(1) == {}, (
        "Error in factorize()"
    )  # Factorization of 1 should return an empty dictionary

    # Step 3: Use the find_candidates() method to find a valid `q`
    print("\n==== Primes.find_candidates() ====")
    # Force 2 to be a unit in `Z_q`
    primes.add_units(2)
    print("(remove all q candidates that are multiples of 2)")

    # Force 11 and 13 to be zero divisors in `Z_q`
    candidates = primes.find_candidates(zero_divisors=[11, 13])

    # Select the last candidate `q` that satisfies the criteria
    print(f"candidate = {candidates[-1]}")
    upperbound = candidates[-1]["candidate_q"]

    # Validate the criteria for the selected candidate `q`
    print(
        f"int(sqrt(B)) = int(sqrt({B})) = int(sqrt({upperbound})) = int(sqrt(c['upperbound']))"
    )
    assert upperbound % 2 != 0, (
        "Error in add_units()"
    )  # Verify that `q` is not divisible by 2
    assert int(B**0.5) == int(upperbound**0.5), (
        "Error in find_candidates()"
    )  # Verify that `sqrt(q)` matches `sqrt(B)`
    assert upperbound % 11 == 0 and upperbound % 13 == 0, (
        "Error in find_candidates()"
    )  # Verify divisibility by 11 and 13


if __name__ == "__main__":
    test_primes()
