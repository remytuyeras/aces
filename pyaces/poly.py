"""
This code defines a function and a class for polynomial operations, including modular arithmetic, polynomial division, and extended GCD computation. The primary functionalities are as follows:

Function:
1. reduction(a: int, b: int, mod: Optional[int] = None) -> Tuple[bool, int]:
   - Determines if a lead coefficient `a` can be reduced by another lead coefficient `b`. If reducible, it returns the quotient. If not, and a modulus `mod` is provided, it adjusts `a` using modular arithmetic to find a reducible value and returns the quotient.

Class:
2. class Polynomial:
   - A class for representing and manipulating polynomials with coefficients modulo an integer (`intmod`). This class includes methods for evaluating polynomials, performing arithmetic operations, and computing the greatest common divisor of polynomials.

Methods:
- Polynomial.__init__(self, coefs: list[int], intmod: Optional[int] = None):
   - Initializes the polynomial with the given list of coefficients, and optionally applies modular arithmetic with `intmod`.

- Polynomial.degree(self) -> int:
   - Returns the degree of the polynomial, i.e., the highest power with a non-zero coefficient.

- Polynomial.lead_coef(self) -> int:
   - Returns the leading coefficient of the polynomial.

- Polynomial.is_null(self) -> bool:
   - Returns `True` if the polynomial is the null polynomial (i.e., has no non-zero coefficients).

- Polynomial.__eq__(self, other: Polynomial) -> bool:
   - Checks if two polynomials are equal, considering the modulus if applicable.

- Polynomial.__neq__(self, other: Polynomial) -> bool:
   - Checks if two polynomials are not equal.

- Polynomial.__repr__(self) -> str:
   - Returns a string representation of the polynomial, showing its terms in standard polynomial form.

- Polynomial.mod(self, intmod: Optional[int] = None) -> Polynomial:
   - Returns a new polynomial where all coefficients are reduced modulo `intmod`.

- Polynomial.__mul__(self, other: Polynomial) -> Polynomial:
   - Multiplies two polynomials and returns the result, considering modular arithmetic if applicable.

- Polynomial.__add__(self, other: Polynomial) -> Polynomial:
   - Adds two polynomials and returns the result, considering modular arithmetic if applicable.

- Polynomial.__sub__(self, other: Polynomial) -> Polynomial:
   - Subtracts one polynomial from another and returns the result, considering modular arithmetic if applicable.

- Polynomial.__lshift__(self, other: Polynomial) -> Tuple[Polynomial, Polynomial, bool]: 
   - Performs Gröbner basis reduction using the leading coefficients. Returns the reduced polynomial, the quotient monomial, and a boolean flag indicating whether the division was successful.

- Polynomial.__mod__(self, other: Polynomial) -> Polynomial:  
   - Computes the remainder of the Euclidean division of two polynomials, ensuring the result is reduced to its minimal degree.

- Polynomial.divmod(self, other: Polynomial) -> Tuple[Polynomial, Polynomial]:  
   - Performs polynomial Euclidean division, returning both the quotient and the remainder.

- Polynomial.extended_gcd(self, other: Polynomial) -> Tuple[Polynomial, Polynomial, Polynomial]:  
   - Computes the extended greatest common divisor (GCD) of two polynomials. Returns the GCD along with coefficients `s` and `t` such that `s * self + t * other = GCD`.

- Polynomial.random(intmod: int, dim: int, anchor: Callable[[int, int], int] = lambda v, w: random.randrange(w)) -> Polynomial:  
   - Generates a random polynomial of degree `dim` with coefficients reduced modulo `intmod`. The optional `anchor` function defines the randomness source for coefficient generation.

- Polynomial.randshift(coef: int, intmod: int, dim: int) -> Polynomial:  
   - Generates a monomial of degree up to `dim` with a leading coefficient equal to `coef % intmod`.

- Polynomial.__call__(self, arg: int = 1) -> Optional[int]:
   - Evaluates the polynomial at the given point `arg` using standard polynomial evaluation, modulo `intmod` if applicable.
"""

# =======================================

from __future__ import annotations
import random
from typing import Optional, Tuple

# =======================================

def reduction(a: int, b: int, mod: Optional[int] = None) -> Tuple[bool, int]:
    """
    Determines whether the integer `a` can be reduced by the integer `b` and computes the corresponding quotient.

    Although `a` and `b` are treated as general integers, they are conceptually intended to represent lead coefficients in polynomial reductions. This function is particularly relevant in algorithms for computing Gröbner bases, where verifying and performing reductions on lead coefficients is a fundamental step. If `a` and `b` are not directly reducible, and a modulus `mod` is provided, the function employs modular arithmetic to adjust `a` within the modulus range to attempt a valid reduction.

    Inputs:
        - a (int): Lead coefficient to be checked for reduction.
        - b (int): Lead coefficient used for the reduction check.
        - mod (Optional[int]): Modulus to adjust `a` within the range [0, mod-1] if it is not directly reducible by `b`. Defaults to `None`.

    Outputs:
        - Tuple[bool, int]:
            - A tuple containing:
                1. `True` if `a` is reducible by `b`, or a valid reduction exists within the modulus range; `False` otherwise.
                2. The resulting quotient, either from `a // b` if directly reducible or based on modular adjustment.

    Notes:
        - If either `a` or `b` is zero, the function returns `(False, 0)` since no reduction is possible.
        - When `mod` is provided, the function adjusts `a` within the modulus range to find a reduction.

    Example:
        - For `a = 10`, `b = 5`, the output is `(True, 2)` because 10 is divisible by 5.
        - For `a = 10`, `b = 3`, `mod = 11`, the output is `(True, 7)` because, although `a % b = 1`, adding `mod` to `a % b` gives 12, which is divisible by `b`. This corresponds to observing that `a - 7 * b = -11`, which is congruent to 0 modulo `mod`.
    """

    reducible = False

    # If either `a` or `b` is zero, return reducibility status and 0 as quotient.
    if a == 0 or b == 0:
        return reducible, 0

    # Check if `a` is divisible by `b`.
    reducer = lambda a, b: (a % b) == 0
    reducible = reducer(a, b)
    quotient = a // b

    # If `a` is not divisible by `b` and `mod` is provided, attempt to find a valid reduction in the range of `mod`.
    if not reducible and mod is not None:
        a_ = a % b
        mod_ = mod % b

        # Iteratively add multiples of `mod` to `a % b` to find a valid quotient `a // b` modulo `mod`.
        for k in range(1,b):
            reducible = reducer(a_ + k * mod_, b)
            if reducible:
                quotient = (a + k * mod) // b
                break

    return reducible, quotient

# =======================================

class Polynomial(object):
    """
    A class representing polynomials with coefficients over integers, optionally reduced modulo a given integer.

    This class provides methods for common polynomial operations, including arithmetic, modular reduction, and extended GCD computation. It is designed for use in both theoretical and applied mathematics, supporting modular arithmetic and advanced functionality like Gröbner basis reduction.

    Attributes:
        - coefs (list[int]): A list of integers representing the coefficients of the polynomial. The `i`-th element corresponds to the coefficient of the `x^i` term.
        - intmod (Optional[int]): An optional modulus. If specified, all coefficients are reduced modulo this value.

    Core Methods:
        - degree(...): Returns the degree of the polynomial, defined as the highest power of `x` with a non-zero coefficient.
        - lead_coef(...): Returns the leading coefficient of the polynomial (coefficient of the highest degree term).
        - is_null(...): Checks if the polynomial is the null polynomial (all coefficients are zero).
        - __repr__(...): Returns a string representation of the polynomial in human-readable form.

    Arithmetic Methods:
        - __add__(...): Adds two polynomials.
        - __sub__(...): Subtracts one polynomial from another.
        - __mul__(...): Multiplies two polynomials.
        - __mod__(...): Computes the remainder of division by another polynomial.
        - divmod(...): Performs polynomial division, returning the quotient and remainder.

    Advanced Methods:
        - extended_gcd(...): Computes the extended GCD of two polynomials, returning the GCD and Bézout coefficients.
        - __lshift__(...): Performs Gröbner basis reduction using leading coefficients.

    Utility Methods:
        - mod(...): Returns a new polynomial with coefficients reduced modulo the specified integer.
        - random(...): Generates a random polynomial of specified degree with coefficients modulo `intmod`.
        - randshift(...): Generates a monomial of specified degree with a given leading coefficient.

   Example:
        A polynomial can be created and manipulated as follows:
        - `p1 = Polynomial([1, 0, 3], 5)` creates a polynomial `1 + 0x + 3x^2` modulo 5.
        - `p1.degree()` returns `2`, the degree of the polynomial.
        - `p1 * Polynomial([1, 1])` multiplies the polynomials `p1` and `Polynomial([1, 1])`.
    """

    def __init__(self, coefs: list[int], intmod: Optional[int] = None):
        """
        Initializes a polynomial with the given coefficients and optional modulus.

        Inputs:
            - coefs (list[int]): A list of integer coefficients representing the polynomial.
            - intmod (Optional[int]): A modulus for reducing the polynomial coefficients.
        """
        self.intmod = intmod
        # Reduce coefficients modulo intmod if provided, otherwise leave them unchanged.
        self.coefs = [(c % self.intmod if self.intmod is not None else c) for c in coefs]

    def degree(self) -> int:
        """
        Returns the degree of the polynomial.

        The degree is determined by finding the highest non-zero coefficient.

        Outputs:
            - int: The degree of the polynomial.
        """
        for i, c in enumerate(self.coefs[::-1]):
            if c != 0:
                return len(self.coefs) - i - 1
        return 0

    def lead_coef(self) -> int:
        """
        Returns the leading coefficient of the polynomial.

        The leading coefficient is the coefficient of the term with the highest degree.

        Outputs:
            - int: The leading coefficient of the polynomial.
        """
        for i, c in enumerate(self.coefs[::-1]):
            if c != 0:
                return c
        return 0

    def is_null(self) -> bool:
        """
        Checks if the polynomial is the null polynomial.

        A polynomial is considered null if all its coefficients are zero.

        Outputs:
            - bool: `True` if the polynomial is null, `False` otherwise.
        """
        return self.lead_coef() == 0

    def __eq__(self, other: Polynomial) -> bool:
        """
        Checks if the current polynomial is equal to another polynomial.

        The polynomials are considered equal if their degrees and corresponding coefficients are the same.

        Inputs:
            - other (Polynomial): The polynomial to compare against.

        Outputs:
            - bool: `True` if the polynomials are equal, `False` otherwise.
        """
        mod = None if self.intmod != other.intmod else self.intmod
        mod_coef = lambda x, y: ((x - y) % mod) == 0 if mod is not None else x == y
        d_self = self.degree()
        d_other = other.degree()
        truth = [
            mod_coef(self.coefs[k] if 0 <= k < len(self.coefs) else 0,
                     other.coefs[k] if 0 <= k < len(other.coefs) else 0)
            for k in range(max(d_self, d_other) + 1)
        ]
        return all(truth)

    def __neq__(self, other: Polynomial) -> bool:
        """
        Checks if the current polynomial is not equal to another polynomial.

        Inputs:
            - other (Polynomial): The polynomial to compare against.

        Outputs:
            - bool: `True` if the polynomials are not equal, `False` otherwise.
        """
        return not (self == other)

    def __repr__(self) -> str:
        """
        Returns a string representation of the polynomial.

        The polynomial is represented as a sum of terms, where each term is displayed in the format "[coefficient]^degree". The terms are listed in descending order of their degree, skipping terms with a coefficient of 0. If all coefficients are 0, the polynomial is represented as "Null".

        The modulo, if specified during the creation of the polynomial, is displayed
        in parentheses at the end of the representation.

        Example Outputs:
            - For a polynomial with no modulo:
            [36]^4+[1500]^3+[20859]^2+[97935]^1+[15750]^0 (None)
            
            - For a polynomial with a modulo of 10:
            [6]^4+[0]^3+[9]^2+[5]^1+[0]^0 (10)

            - For a null polynomial with modulo 7:
            Null (7)

            - For a single-term polynomial with modulo 5:
            [2]^4 (5)

        Outputs:
            - str: The string representation of the polynomial.
        """
        # Join the non-zero coefficients and their corresponding degrees into terms. The format of each term is "[coefficient]^degree".
        s = "+".join([f"[{c}]^{k}" for k, c in enumerate(self.coefs) if k <= self.degree() and c != 0][::-1])
        
        # Return the formatted string. If no terms exist, return "Null". Append the modulo (if any) in parentheses at the end.
        return (s if s != "" else "Null") + f" ({self.intmod})"


    def mod(self, intmod: Optional[int] = None) -> Polynomial:
        """
        Returns a new polynomial with coefficients reduced modulo `intmod`.

        If `intmod` is not provided, the current polynomial is returned without changes.

        Inputs:
            - intmod (Optional[int]): The modulus to reduce the coefficients. Defaults to `None`.

        Outputs:
            - Polynomial: A new polynomial with reduced coefficients modulo `intmod`.
        """
        if intmod is None:
            return Polynomial(self.coefs, None)
        else:
            return Polynomial([(x % intmod) for x in self.coefs], intmod)

    def __mul__(self, other: Polynomial) -> Polynomial:
        """
        Multiplies the current polynomial by another polynomial.

        The result is a new polynomial with the coefficients obtained by multiplying the terms of the polynomials.

        Inputs:
            - other (Polynomial): The polynomial to multiply with.

        Outputs:
            - Polynomial: A new polynomial representing the product of the two polynomials.
        """
        mod = None if self.intmod != other.intmod else self.intmod
        mod_coef = lambda x, y: (x * y) % mod if mod is not None else x * y
        d_self = self.degree()
        d_other = other.degree()
        coefs = [
            sum([(mod_coef(c, other.coefs[n - k]) if 0 <= n - k < len(other.coefs) else 0) for k, c in enumerate(self.coefs)])
            for n in range(d_self + d_other + 1)
        ]
        return Polynomial(coefs, mod)

    def __add__(self, other: Polynomial) -> Polynomial:
        """
        Adds the current polynomial to another polynomial.

        The result is a new polynomial with coefficients that are the sum of the corresponding coefficients.

        Inputs:
            - other (Polynomial): The polynomial to add.

        Outputs:
            - Polynomial: A new polynomial representing the sum of the two polynomials.
        """
        mod = None if self.intmod != other.intmod else self.intmod
        mod_coef = lambda x, y: (x + y) % mod if mod is not None else x + y
        d_self = self.degree()
        d_other = other.degree()
        coefs = [
            mod_coef(self.coefs[k] if 0 <= k < len(self.coefs) else 0,
                     other.coefs[k] if 0 <= k < len(other.coefs) else 0)
            for k in range(max(d_self, d_other) + 1)
        ]
        return Polynomial(coefs, mod)

    def __sub__(self, other: Polynomial) -> Polynomial:
        """
        Subtracts another polynomial from the current polynomial.

        The result is a new polynomial with coefficients that are the difference of the corresponding coefficients.

        Inputs:
            - other (Polynomial): The polynomial to subtract.

        Outputs:
            - Polynomial: A new polynomial representing the difference of the two polynomials.
        """
        mod = None if self.intmod != other.intmod else self.intmod
        mod_coef = lambda x, y: (x - y) % mod if mod is not None else x - y
        d_self = self.degree()
        d_other = other.degree()
        coefs = [
            mod_coef(self.coefs[k] if 0 <= k < len(self.coefs) else 0,
                     other.coefs[k] if 0 <= k < len(other.coefs) else 0)
            for k in range(max(d_self, d_other) + 1)
        ]
        return Polynomial(coefs, mod)

    def __lshift__(self, other: Polynomial) -> Tuple[Polynomial, Polynomial, bool]:
        """
        Performs Gröbner basis reduction using the leading coefficients of two polynomials and returns the reduced polynomial, quotient monomial, and a success flag.

        This method applies a reduction algorithm based on the leading coefficients of two polynomials. It uses the leading term of the current polynomial and the leading term of the divisor polynomial to perform a division-like step and reduces the current polynomial. The quotient monomial represents the term by which the divisor's leading term is multiplied, and the method returns a success flag to indicate whether the reduction was successful.

        Inputs:
            - other (Polynomial): The polynomial whose leading coefficient is used for the reduction.

        Outputs:
            - Tuple[Polynomial, Polynomial, bool]:
                - The first element is the reduced polynomial after the Gröbner basis reduction.
                - The second element is the quotient monomial, which represents the factor by which the divisor's leading term was multiplied during reduction.
                - The third element is a boolean flag indicating whether the reduction was successful.

        Notes:
            - The reduction is based on the leading coefficients of the polynomials involved. If the division-like step cannot be performed due to conditions like incompatible degrees, the method returns the original polynomial along with a zero polynomial as the quotient monomial.
            - If both polynomials share the same modulus (`intmod`), modular arithmetic is applied during the reduction process.

        Example:
            For two polynomials `A(x) = x^3 + 2x^2 + 3x + 4` and `B(x) = x^2 + 1`, the reduction might result in:

            Reduced Polynomial: `2x^2 + 2x + 4`
            Quotient Monomial: `x^3 / x^2 = x`
            Success Flag: `True`

        Special Cases:
            - If the degree of the current polynomial is smaller than the degree of the divisor, reduction cannot occur, and the method will return the original polynomial along with a zero quotient monomial.
            - If the reduction is unsuccessful for other reasons (e.g., irreducible terms), the method returns the original polynomial and a zero quotient.
        """
        mod = None if self.intmod != other.intmod else self.intmod

        # Perform reduction using the leading coefficients to determine if the division-like reduction is possible.
        reducible, q = reduction(self.lead_coef(), other.lead_coef(), mod)

        # If the reduction is not possible, return the current polynomial with a zero polynomial as the quotient.
        if not reducible:
            return self, Polynomial([0], mod), False

        # Determine the degrees of the polynomials.
        d_self = self.degree()
        d_other = other.degree()

        # If the degree of the current polynomial is smaller than the degree of the divisor, reduction cannot occur.
        if d_self < d_other:
            return self, Polynomial([0], mod), False

        # Calculate the degree difference and set up a lambda function for modular coefficient adjustments.
        deg_diff = d_self - d_other
        mod_coef = lambda x, y: (x - q * y) % mod if mod is not None else x - q * y

        # Adjust the coefficients of the current polynomial based on the reduction step.
        coefs = [
            (mod_coef(c, other.coefs[k - deg_diff]) if 0 <= k - deg_diff < len(other.coefs) else c)
            for k, c in enumerate(self.coefs)
        ]

        # Return the reduced polynomial, the quotient monomial, and the success flag.
        return Polynomial(coefs, mod), Polynomial([0] * deg_diff + [q], mod), True

    def __mod__(self, other: Polynomial) -> Polynomial:
        """
        Computes the remainder of the Euclidean division of the current polynomial by another polynomial.

        This method computes the remainder of polynomial division by utilizing a (Gröbner basis-like) reduction (`<<`) operation. It repeatedly performs reduction until the degree of the remainder is smaller than that of the divisor. The result is the final remainder obtained at the end of the Euclidean division process.

        Inputs:
            - other (Polynomial): The polynomial by which to compute the modulus of the current polynomial.

        Outputs:
            - Polynomial: The remainder after the Euclidean division of the current polynomial by the other.

        Notes:
            - This method uses the `__lshift__` method for polynomial reduction, repeating the process until the degree of the remainder is smaller than that of the divisor.
            - The modulus operation ensures that the result is a polynomial of lower degree than the divisor, adhering to the principles of polynomial Euclidean division.
        """
        # Perform the (Gröbner basis-like) reduction and extract the remainder.
        r, _, t = self << other
        while t:
            r, _, t = r << other

        # Return the final remainder after all reduction steps.
        return r

    def divmod(self, other: Polynomial) -> Tuple[Polynomial, Polynomial]:
        """
        Computes both the quotient and remainder of the Euclidean division of the current polynomial by another polynomial.

        This method performs polynomial division by repeatedly applying the (Gröbner basis-like) reduction (`<<`) operation. It computes both the quotient and remainder, continuing the reduction process until the remainder is smaller than the divisor. The final quotient and remainder are returned.

        Inputs:
            - other (Polynomial): The polynomial by which to divide the current polynomial.

        Outputs:
            - Tuple[Polynomial, Polynomial]:
                - The first element is the quotient polynomial after Euclidean division.
                - The second element is the remainder polynomial after Euclidean division.

        Notes:
            - The method continues to reduce the remainder by the divisor until no further reduction is possible, in line with the Euclidean division process.
            - The quotient is accumulated throughout the reduction steps.
        """
        # Perform the (Gröbner basis-like) reduction and get the initial remainder, quotient, and success flag.
        remainder, q, t = self << other
        quotient = q

        # Continue reducing the remainder by the divisor until no further reduction is possible.
        while t:
            remainder, q, t = remainder << other
            quotient = quotient + q

        # Return the quotient and the final remainder.
        return quotient, remainder

    def extended_gcd(self, other: Polynomial) -> Tuple[Polynomial, Polynomial, Polynomial]:
        """
        Computes a multiple of the greatest common divisor (GCD) of two polynomials.

        This method computes a multiple of the GCD of the current polynomial and another polynomial, as well as the coefficients that express this multiple as a linear combination of the two polynomials. The extended GCD algorithm uses the Euclidean algorithm and tracks the coefficients during the process.

        Inputs:
            - other (Polynomial): The polynomial to compute the GCD with.

        Outputs:
            - Tuple[Polynomial, Polynomial, Polynomial]:
                - The first element is a multiple of the GCD of the two polynomials.
                - The second element is the coefficient of the first polynomial in the linear combination (for the multiple).
                - The third element is the coefficient of the second polynomial in the linear combination (for the multiple).

        Notes:
            - The method uses polynomial division and tracks the coefficients throughout the Euclidean algorithm to find the GCD multiple.
            - The returned coefficients express a multiple of the GCD as a linear combination of the input polynomials.

        Example:
            For polynomials `A(x)` and `B(x)`, the method will return a multiple of the GCD of `A(x)` and `B(x)`, along with the coefficients that express this multiple as a linear combination of `A(x)` and `B(x)`.
        """
        mod = None if self.intmod != other.intmod else self.intmod
        
        # Initialize the polynomials representing the trivial scalars 0 and 1, respectively.
        poly_0 = Polynomial([0], mod)
        poly_1 = Polynomial([1], mod)

        # Initialize lists to store the polynomials and coefficients during the extended Euclidean algorithm.
        r = [self, other]
        s = [poly_1, poly_0]  
        t = [poly_0, poly_1]

        reducible = True
        while reducible:
            r1: Polynomial = r[-1]
            r0: Polynomial = r[-2]
            
            # Perform division and get quotient and remainder.
            q, r2 = r0.divmod(r1)

            # If the division successfully reduces the remainder (i.e., r0 != r2), continue the algorithm.
            if r2 != r0:
                r.append(r2)
                # Update the coefficients for the first polynomial.
                s.append(s[-2] - q * s[-1])
                # Update the coefficients for the second polynomial.  
                t.append(t[-2] - q * t[-1])
                # Continue if the remainder is not zero.
                reducible = not(r2.is_null())  
            else:
                # Special case when the division leads to no valid reduction. In this case, the leading coefficients of r1 and r0 could not reduce further, so we multiply r0 with the leading coefficient of r1 to force progress in the algorithm.
                lead_r1 = Polynomial([r1.lead_coef()], mod)
                r0 = lead_r1 * r[-2]
                
                # The line below effectively repeats the reduction chain, but this time the reduction is forced by the multiplication with the leading coefficient of r1, ensuring the algorithm progresses.
                q, r2 = r0.divmod(r1)
                
                r.append(r2)
                # Update the coefficients for the first polynomial.
                s.append(lead_r1 * s[-2] - q * s[-1])
                # Update the coefficients for the second polynomial.
                t.append(lead_r1 * t[-2] - q * t[-1])  
                # Continue if division reduces the remainder.
                reducible = r2 != r0 and not(r2.is_null())

        # Return the GCD and the coefficients for the linear combination.
        return (r[-2], s[-2], t[-2])

    @staticmethod
    def random(intmod: int, dim: int, anchor = lambda v,w : random.randrange(w)) -> Polynomial:
        """
        Generates a random polynomial with coefficients modulo `intmod`.

        This method creates a polynomial of degree `dim - 1` with randomly selected coefficients, each chosen by the `anchor` function, which defaults to generating random integers in the range `[0, intmod)`.

        Inputs:
            - intmod (int): The modulus for the coefficients of the polynomial.
            - dim (int): The degree of the polynomial plus one (i.e., number of coefficients).
            - anchor (function, optional): A function used to generate each coefficient. The default generates random integers in the range `[0, intmod)`.

        Outputs:
            - Polynomial: A polynomial object where each coefficient is an integer selected by `anchor`, modulo `intmod`.

        Example:
            - Calling `random(5, 3)` might generate a polynomial like `Polynomial([3, 1, 4], 5)`.
        """
        return Polynomial([anchor(i, intmod) for i in range(dim)], intmod)

    @staticmethod
    def randshift(coef, intmod: int, dim: int) -> Polynomial:
        """
        Generates a polynomial that can be used to randomly shift the coefficient of another polynomial.

        This method creates a polynomial with a degree between `0` and `dim`, where the coefficient at the highest degree term is set to `coef % intmod`. The degree of the polynomial is determined randomly, and the polynomial may have zero coefficients for lower degrees. This polynomial can be used to "shift" the coefficient of another polynomial by using the value `coef` at a degree determined randomly.

        Inputs:
            - coef (int): The coefficient to be used for the highest degree term, modulo `intmod`.
            - intmod (int): The modulus applied to the coefficients of the polynomial.
            - dim (int): The maximum possible degree of the polynomial plus one (i.e., the number of coefficients to be generated).

        Outputs:
            - Polynomial: A polynomial object with the leading coefficient equal to `coef % intmod`, and lower degree terms set to zero. This polynomial can be used to shift the coefficient of another polynomial at a random degree.

        Example:
            - Calling `randshift(4, 5, 4)` might generate a polynomial like `Polynomial([0, 0, 0, 4], 5)`, where the highest degree term is `4 % 5 = 4`, and the polynomial has a degree between `0` and `3` (i.e., four coefficients, including zeros for lower degrees).
        """
        # Randomly determine the number of zero coefficients before the leading term.
        degree_shift = [0] * (random.randrange(dim))  
        
        # Create and return the polynomial with the shifted degree and specified leading coefficient.
        return Polynomial(degree_shift + [coef % intmod], intmod)


    def __call__(self, arg: int = 1) -> Optional[int]:
        """
        Evaluates the polynomial at a given value of `arg` using Horner's method.

        This method calculates the value of the polynomial at `arg` by applying Horner's algorithm, which rewrites the polynomial in a nested form for more efficient evaluation. Each coefficient is multiplied by `arg` raised to the appropriate power, and the result is computed modulo `intmod` if specified.

        Inputs:
            - arg (int, optional): The value at which the polynomial is to be evaluated. Defaults to 1.

        Outputs:
            - int: The value of the polynomial evaluated at `arg`, modulo `intmod` if specified. Returns `None` if the list of coefficients is empty.

        Notes:
            - Horner's method minimizes the number of multiplications and additions needed to evaluate the polynomial.
            - If `intmod` is specified, the result is taken modulo `intmod` at each step to prevent overflow and maintain consistency with the specified modulus.
            
        Example:
            - For the polynomial `Polynomial([1, 2, 3], 7)` and `arg = 2`, the result would be `3*2^2 + 2*2^1 + 1*2^0 = 17 % 7 = 3`, computed efficiently using Horner's method.
        """
        output = 0
        # Iterate over the coefficients in descending order, from the polynomial's degree to 0.
        for i, c in enumerate(self.coefs[:self.degree()+1][::-1]):
            # Apply Horner's method: evaluate the polynomial in nested form.
            output = (output * arg + c) % self.intmod if self.intmod is not None else output * arg + c
        # Return the value of the polynomial evaluated at `arg`.
        return output
