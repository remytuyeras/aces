"""
This code defines a set of functions and a class for performing operations related to prime numbers, modular arithmetic, and prime factorization. Its primary functionalities are as follows:

Functions:
1. extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
   - Computes the extended greatest common divisor (GCD) of two integers `a` and `b`, returning the GCD along with the coefficients `s` and `t` that satisfy the equation `a * s + b * t = gcd(a, b)`.

2. randinverse(intmod: int) -> Tuple[int, int]:
   - Generates a random integer `a` that is coprime with `intmod` and computes its modular inverse using the extended GCD.

Class:
3. class Primes:
   - A class for managing prime numbers, including functionality to generate primes, cache results, perform prime factorization, and manage prime factors. The primary purpose of this class is to generate candidate `q` parameters used in the ACES cryptosystem.

Methods:
- Primes.__init__(self, upperbound: int, cache: bool = True):
   - Initializes the class, generates primes for numbers up to the given `upperbound`, and optionally caches the results.
   
- Primes.get_primes(upperbound: int, cache: list[int] = []) -> list[int]:
   - Generates a list of primes for numbers up to the given `upperbound`, leveraging any primes from the provided cache.

- Primes.factorize(self, n: int, limit: Optional[int] = None) -> Optional[dict[int, int]]:
   - Factorizes the integer `n` into its prime components using precomputed primes, returning a dictionary with prime factors and their multiplicities.

- Primes.add_units(self, n: int) -> None:
   - Adds a number and its prime factors to the `units` attribute, which is a dictionary used to store prime factors that should be excluded from the factorization of candidate `q` parameters.

- Primes.find_candidates(self, zero_divisors: list = []) -> list[dict[str,Any]]:
   - Finds candidate `q` parameters whose prime factorization does not include factors from the `units` attribute but contains primes from the `zero_divisors` list.
"""

# =======================================

import os
import json
import math
import random
from typing import Optional, Tuple, Any

# =======================================

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Computes the extended greatest common divisor (GCD) of two integers `a` and `b`.
    
    This function uses the extended Euclidean algorithm to find integers `s` and `t` such that `a * s + b * t = gcd(a, b)`. The output includes the GCD of `a` and `b`, along with the coefficients `s` and `t`.

    Inputs:
        - a (int): An integer.
        - b (int): Another integer.

    Outputs:
        - Tuple[int, int, int]: A tuple (gcd, s, t), where:
            - gcd: The greatest common divisor of `a` and `b`.
            - s: Coefficient such that `a * s + b * t = gcd(a, b)`.
            - t: Coefficient such that `a * s + b * t = gcd(a, b)`.

    Example:
        extended_gcd(30, 20) returns (10, 1, -1), where 10 is gcd(30, 20), 
        and 1, -1 are coefficients satisfying 30*1 + 20*(-1) = 10.
    """
    # Initialize variables for the extended Euclidean algorithm
    r = [a, b]
    s = [1, 0]
    t = [0, 1]
    # Extended Euclidean algorithm
    while not(0 in r):
        r1 = r[-1]
        r0 = r[-2]
        # Compute the quotient `q` and the remainder `r2` of the division r0/r1.
        q, r2 = divmod(r0, r1)
        r.append(r2)
        s.append(s[-2] - q * s[-1])
        t.append(t[-2] - q * t[-1])
    
    # Return the GCD (second-to-last remainder) and the coefficients `s` and `t`.
    return (r[-2], s[-2], t[-2])

# =======================================

def randinverse(intmod: int) -> Tuple[int, int]:
    """
    Generates a random integer `a` within the range [1, intmod-1] that is coprime with `intmod`, and computes its modular multiplicative inverse.

    This function repeatedly selects random integers until it finds one that is coprime with the given modulus `intmod` (i.e., gcd(a, intmod) = 1). It then uses the extended Euclidean algorithm to compute the modular inverse of `a`.

    Inputs:
        - intmod (int): An integer modulus, must be positive.

    Outputs:
        - Tuple[int, int]: A tuple (a, inva), where:
            - a: A random integer coprime with `intmod`.
            - inva: The modular inverse of `a` modulo `intmod`, such that `(a * inva) % intmod = 1`.

    Example:
        randinverse(7) could return (3, 5), where 3 is coprime with 7, and 3 * 5 ≡ 1 (mod 7).
    """

    # Select a random integer `a` in the range [1, intmod-1].
    a = random.randrange(1, intmod)

    # Keep generating random integers until gcd(a, intmod) = 1 (i.e., `a` is coprime with `intmod`).
    while math.gcd(a, intmod) != 1:
        a = random.randrange(1, intmod)

    # Compute the modular inverse of `a` using the extended Euclidean algorithm.
    _, inva, _ = extended_gcd(a, intmod)

    # Return the random integer `a` and its modular inverse modulo `intmod`.
    return (a, inva % intmod)

# =======================================

class Primes(object):
    """
    A class for managing prime numbers and their properties. This class provides functionality for generating prime factors of numbers up to a specified upper bound, caching results for reuse, performing prime factorization, and handling related operations. The primary purpose of this class is to generate candidate `q` parameters used in the ACES cryptosystem.

    Attributes:
        - upperbound (int): An upper bound on the numbers from which the class collects prime factors to build candidate `q` parameters.
        - cache (bool): A boolean indicating whether to cache primes in a file.
        - primes (list): A list containing all prime factors of numbers up to `upperbound`.
        - factorization (dict): A dictionary containing the prime factorization of numbers up to `upperbound`.
        - units (dict): A dictionary used to store prime factors that should be coprime with the `q` parameters generated by the `find_candidates` method.

    Methods:
        - get_primes(...): A static method to generate prime factors for numbers up to the specified upper bound.
        - factorize(...): Factorizes a given number into its prime components.
        - add_units(...): Adds a number and its prime factors to the `units` attribute.
        - find_candidates(...): Finds candidate `q` parameters that are not divisible by certain factors (stored in the `units` dictionary).
    """

    def __init__(self, upperbound: int, cache: bool = True):
        """
        Initializes the `Primes` class, generating prime factors for numbers up to the specified `upperbound`. Optionally caches the primes to a file for reuse.

        Inputs:
            - upperbound (int): An upper bound on the numbers from which the class collects prime factors. Only the prime factors of numbers up to this value will be considered.
            - cache (bool, optional): A boolean flag indicating whether to enable caching of primes. Default is `True`. If set to `True`, previously computed primes will be saved to a file and reused in future initializations if available.

        This method initializes several class attributes:
            - self.upperbound: The upper bound for prime factor computation.
            - self.cache: A boolean flag indicating whether caching is enabled.
            - self.primes: A list of primes for numbers up to `upperbound`.
            - self.factorization: A dictionary containing the factorization of numbers up to `upperbound`.
            - self.units: A dictionary used to store prime factors to be avoided in the generation of `q` parameters.
        """
        # Store the upper bound for prime factor computation.
        self.upperbound = upperbound
        # Flag for caching primes to a file (enabled by default).
        self.cache = cache
        # Notify that primes are being generated.
        print("getting primes...")  

        # Initialize a list to hold previously cached primes.
        previous = []  

        # Check if a cached primes file exists, and load it if available.
        if self.cache and os.path.exists(f".aces.cache_primes.json"):
            with open(f".aces.cache_primes.json", "r") as f:
                # Load the cached JSON object.
                json_object = json.load(f)
                # Extract previously cached primes from the file.
                previous = json_object["primes"]  

        # Generate primes for numbers up to `upperbound`, using the previously cached primes (if available).
        self.primes = Primes.get_primes(upperbound, previous)
        # Notify that prime generation is complete.
        print("primes obtained")  

        # If caching is enabled, check if the cache needs to be updated.
        if self.cache:
            # Assume the cache needs an update.
            need_update = True  
            
            # If the cache file exists, check if it covers the range up to the current upperbound.
            if os.path.exists(f".aces.cache_primes.json"):
                # Retrieve the cached upper bound.
                cached_ub = json_object["upperbound"]
                # If the cache is already valid, no need to update.
                if self.upperbound <= cached_ub:
                    need_update = False  
            
            # If an update is needed, write the new primes to the cache file.
            if need_update:
                with open(f".aces.cache_primes.json", "w") as f:
                    json_update = {"upperbound": self.upperbound, "primes": self.primes}
                    # Save the updated primes to the cache.
                    json.dump(json_update, f)  

        # Factorize the value `upperbound`, storing the result in `self.factorization`.
        self.factorization = self.factorize(upperbound)

        # Initialize the `self.units` dictionary to store factors to be avoided in the generation of `q` parameters.
        self.units = {}


    @staticmethod
    def get_primes(upperbound: int, cache: list[int] =[]) -> list[int]:
        """
        Generates a list of prime factors for numbers up to a given upper bound using trial division.

        This method builds on any previously provided list of primes (via `cache`) to optimize prime generation by skipping known non-prime numbers. 

        Inputs:
            - upperbound (int): The maximum integer (inclusive) for which prime factors are generated.
            - cache (list, optional): A list of previously generated primes. Defaults to an empty list.

        Outputs:
            - list: A list of prime numbers for numbers up to `upperbound`.
        """
        # Initialize the list of primes with the previously cached primes, if provided.
        previous = cache  

        # Determine the starting point for prime generation:
        #   - If `cache` is provided, start from the next integer after the last cached prime.
        #   - Otherwise, start from 2, the smallest prime number.
        i = max(2, previous[-1]) if previous else 2  

        # Iterate over integers from the starting point (`i`) up to the square root of the upper bound.
        # The range limit is chosen because any composite number `n` must have at least one divisor smaller than or equal to `sqrt(n)`.
        for k in range(i, int(math.sqrt(upperbound)) + 1):
            # Assume `k` is prime until proven otherwise.
            is_prime = True  

            # Check if `k` is divisible by any of the previously identified primes. If divisible, `k` is not a prime, and we exit the loop early.
            for p in previous:
                # `k` is divisible by a smaller prime `p`.
                if k % p == 0:  
                    is_prime = False
                    # Stop further checks; `k` is confirmed non-prime.
                    break  

            # If no divisors were found, `k` is a prime number.
            if is_prime:
                # Add `k` to the list of primes.
                previous.append(k)  

        # Return the updated list of primes, including both cached and newly identified primes.
        return previous

    def factorize(self, n: int, limit: Optional[int] = None) -> Optional[dict[int, int]]:
        """
        Factorizes a given number into its prime components.

        This method decomposes the integer `n` into its prime factors and their multiplicities. It uses the precomputed list of primes (`self.primes`) for efficient factorization. An optional `limit` can restrict the value of prime factors considered during the process.

        Inputs:
            - n (int): The number to factorize. Must be greater than 0.
            - limit (Optional[int]): An upper bound on the prime factors to consider. Defaults to `(sqrt(self.upperbound) + 1)^2` if not provided.

        Outputs:
            - Optional[Dict[int, int]]:
                - A dictionary where keys are prime factors of `n` and values are their respective multiplicities.
                - Returns `None` if `n` is invalid (e.g., non-positive or exceeding the valid range).

        Notes:
            - Assumes `self.primes` contains a precomputed list of prime numbers.
            - The factorization process:
                1. Handles the smallest prime factor `2` separately.
                2. Iterates through primes up to the specified `limit` or the square root of `n`.
                3. If `n` remains greater than 1 after processing smaller primes, it is added as a prime factor.
            - If `limit` is specified, it acts as a strict upper bound for the prime factors considered.

        Example:
            For `n = 60`, with `self.primes = [2, 3, 5, 7, ...]`:
                - If `limit = 5`, the result is `{2: 2, 3: 1, 5: 1}` (i.e., 60 = 2^2 * 3^1 * 5^1).
                - If `limit = 3`, the result is `{2: 2, 3: 1}`.
        """
        # Initialize the factorization dictionary to None.
        expression = None  
        
        # Define the upper bound for factorization:
        #   - Use the provided `limit` if specified.
        #   - Otherwise, default to `(sqrt(self.upperbound) + 1)^2`.
        bound = limit if limit is not None else int(math.sqrt(self.upperbound) + 1) ** 2  

        # Only proceed if `n` is within the valid range (0 < n < bound).
        if 0 < n < bound:
            # Initialize the dictionary to store prime factors and their multiplicities.
            expression = {}  

            # Handle factorization for 2 (the smallest prime) separately.
            while n % 2 == 0:
                # Increment the multiplicity of 2 in the factorization.
                expression.setdefault(2, 0)
                expression[2] += 1
                # Reduce `n` by dividing it by 2.
                n //= 2  

            # Factorize using the list of primes up to the specified limit or sqrt(n).
            for p in self.primes:
                # If a limit is provided and the current prime exceeds it, stop.
                if limit is not None and p > limit:
                    break
                # Stop the loop early if the current prime exceeds sqrt(n), since no further factors will be found below `sqrt(n)` at this stage.
                if p > math.sqrt(n):
                    break

                # Divide `n` by the prime `p` repeatedly until it is no longer divisible.
                while n % p == 0:
                    # Increment the multiplicity of `p` in the factorization.
                    expression.setdefault(p, 0)
                    expression[p] += 1
                    # Reduce `n` by dividing it by `p`.
                    n //= p  

            # If the remaining `n` after processing all smaller primes is greater than 2, then it is itself a prime and should be added to the factorization.
            if n > 2:
                expression.setdefault(n, 0)
                expression[n] += 1  

        # Return the dictionary containing the prime factorization of `n`.
        return expression

    def add_units(self, n: int) -> None:
        """
        Factorizes a number and adds its prime factors to the `units` dictionary.

        The `units` dictionary stores prime factors that must be coprime with candidate `q` parameters, ensuring these factors are excluded from their prime compositions.

        Inputs:
            - n (int): The number to be factorized. Its prime factors will be added to the `units` dictionary.

        Outputs:
            - None: Updates the `units` dictionary in place.
        """
        # Factorize the number `n`.
        expression = self.factorize(n)  
        if expression is not None:
            # Iterate over the prime factors of `n`.
            for k in expression.keys():
                # If the factor `k` is not already in `units`, initialize it as an empty list.
                self.units.setdefault(k, [])
                # Add the number `n` to the list of numbers for factor `k`.
                self.units[k].append(n)  


    def find_candidates(self, zero_divisors: list = []) -> list[dict[str,Any]]:
        """
        Identifies candidate `q` parameters that meet specific factorization criteria.

        This method iterates over numbers from the `upperbound` to a calculated limit, factoring each number. Candidates are selected based on the following conditions:
            1. They possess all the prime factors specified in `zero_divisors`.
            2. They do not contain any prime factor present in the `units` dictionary.
            3. They are greater than or equal to `self.upperbound`

        The resulting candidates are sorted using multiple criteria to prioritize certain types of numbers.

        Inputs:
            - zero_divisors (list, optional): A list of prime factors that all candidates must have. Default is an empty list. If provided, the method ensures that all candidate `q` parameters are divisible by these factors.

        Outputs:
            - list[dict]: A sorted list of candidate numbers, where each candidate is represented as a dictionary containing metadata about its factorization.
                The list is sorted by:
                1. The number of factors in the factorization (ascending).
                2. The candidate number (ascending).
                3. The smallest prime factor (ascending).
                4. The largest prime factor (ascending).
        """
        # Calculate the upper bound limit for `q` parameters such that the integer parts of their square roots are less than or equal to sqrt(self.upperbound).
        limit = (int(math.sqrt(self.upperbound)) + 1) ** 2
        # Initialize the list of candidates.
        output = []  

        # Iterate through numbers from upperbound to the limit.
        for k in range(self.upperbound, limit):
            # Factorize the number `k`.
            expression = self.factorize(k, limit)
            # Assume the number is a valid candidate initially. 
            possible = True  

            # Check if zero_divisors is provided.
            if zero_divisors != []:  
                for zd in zero_divisors:
                    # Ensure divisibility by zero_divisors.
                    if zd not in expression.keys():
                        # Mark as invalid if the candidate is not divisible by one of the zero_divisors.
                        possible = False
                        break
            
            # Iterate over the prime factors of the candidate number.
            for f in expression.keys():
                # Ensure that the candidate's factors are not in `units`.
                if f in self.units.keys():
                    # Mark as invalid if the candidate has a factor in `units`.
                    possible = False  
                    break
            
            # If the number is still valid, add it as a candidate.
            if possible:
                # Get the full factorization for the candidate `q` parameter.
                g = self.factorize(k, limit)  
                json_object = {
                    "candidate_q": k,  # The candidate `q` parameter.
                    "factor_count": len(g.keys()),  # The number of prime factors.
                    "min_factor": min(g.keys()),  # The smallest prime factor.
                    "max_factor": max(g.keys()),  # The largest prime factor.
                    "factorization": g,  # The full factorization of the candidate number.
                }
                # Add the candidate to the output list.
                output.append(json_object)  

        # Sort the list of candidates based on multiple criteria: number of factors, number itself, min/max factors.
        return sorted(output, key=lambda x: [
            x["factor_count"],
            x["candidate_q"],
            x["min_factor"],
            x["max_factor"],
        ])

