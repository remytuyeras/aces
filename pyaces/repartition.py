"""
This code defines the Repartition class, which facilitates the construction and manipulation of repartition-related parameters within the ACES cryptosystem. The class's primary function is to compute the images `x_i(\omega)` that are associated with the secret key `x = (x_1, \dots, x_n)`, ensuring that ACES satisfies homomorphic properties. To achieve this, it computes necessary parameters, including `sigma`, `lambda`, `mu`, and `\ell`, all of which are essential for maintaining efficient and secure homomorphic operations in the ACES cryptosystem.

Class:
1. class Repartition:
   - Provides a set of methods aimed at generating the images of a secret key for ACES, ensuring that these images are compatible with a specific repartition structure.

Methods:
- Repartition.__init__(self, n: int, p: int, upperbound: int):
   - Initializes the class instance with parameters related to `sigma`, `lambda`, `mu`, and `\ell`, which are needed to construct a homomorphic ACES scheme. These parameters are built alongside the images `x_i(\omega)` of an intended secret key `x = (x_1, \dots, x_n)` for ACES. These images are accessible via the attribute `self.x_images` and are intended for initializing an ACES encryption scheme.

- Repartition.construct(self, new_sigma: bool = True, new_mus: bool = True) -> None:
   - Calls `self.construct_lambdas(new_sigma = True, new_mus = True)` to initiate the construction, starting from scratch by default.

- Repartition.reconstruct_sigma(self, trivial_factor: bool = False, trivial_sigma: bool = False) -> None:
    - Recomputes the repartition `sigma` (see `Repartition.construct_sigma`) with an option to simplify certain cryptographic features related to its underlying mapping rules

- Repartition.construct_mus(self) -> bool:
   - Constructs the images of the secret key and the associated `mu` parameters, ensuring that they satisfy a Bézout identity combining the images of the secret key and of those of the repartition `sigma`. Returns a success status (True/False) based on whether the Bézout identity results in a gcd of 1.

- Repartition.construct_lambdas(self, new_sigma: bool = True, new_mus: bool = True) -> None:
   - Constructs the images of the secret key along with the associated 3-tensor `lambda` and optionally regenerates `sigma` and `mu` parameters.

- Repartition.construct_sigma(self, trivial_factor: bool = False, trivial_sigma: bool = False) -> None:
   - Constructs a `sigma` function with balanced fiber sizes, serving as the repartition structure for the homomorphic version of ACES.

- Repartition.sigma_q_divisor(self, i: int, j: int) -> int:
   - Returns the divisor used to define the ratio `\sigma[q]_{i, j}` for given inputs (i, j).

- Repartition.sigma_q(self, i: int, j: int) -> int:
   - Computes the ratio `\sigma[q]_{i, j}` for given inputs (i, j) and returns the computed value.

- Repartition.construct_ell(self) -> None:
   - Generates the `\ell` matrix used to characterize the 3-tensor `lambda`.
"""

# =======================================

from .arith import Primes, extended_gcd
import random

# =======================================

class Repartition(object):
    """
    A class for constructing and managing the repartition-related elements necessary for homomorphic operations in ACES-based schemes. This class focuses on computing key parameters such as `sigma`, `lambda`, `mus`, and `\ell`, which are integral to constructing secure homomorphic ACES-based schemes. It also facilitates the creation and handling of images corresponding to the secret key, ensuring compatibility with the repartition structure.

    Attributes:
        - self.n (int): Represents the dimension or size of the secret key.
        - self.primes (Primes): An instance of the `Primes` class for managing prime numbers up to an `upperbound` value.
        - self.candidate (dict): Stores the selected candidate for the `q` parameter, including its factorization.
        - self.q (int): The `candidate_q` value from the selected candidate.
        - self.factors (list[int]): The prime factorization of `q`, including the trivial factor 1.
        - self.n0 (int): The number of prime factors of the selected `q`.
        - self.sigma_done (bool): Flag indicating whether the `sigma` construction is completed.
        - self.sigma_img (Optional[list[int]]): Stores the image of `sigma`, initially set to `None`.
        - self.sigma_fibers (Optional[dict[int, list[int]]]): Stores the fibers of `sigma`, initially set to `None`.
        - self.ell (Optional[list[list[int]]]): A matrix used in the 3-tensor construction `lambda`, initially `None`.
        - self.mus (list[int]): A list for storing the `mu` parameters.
        - self.lambdas (list[list[list[int]]]): A list for storing the `lambda` parameters.
        - self.x_images (list[int]): Stores the images of the secret key.

    Methods:
        - construct(...): Begins the construction of repartition-related parameters, invoking the `construct_lambdas` method.
        - reconstruct_sigma(...): Recomputes the repartition `sigma` with options for simplifying its mapping rules.
        - construct_mus(...): Computes the `mu` parameters and regenerates the secret key images to ensure compatibility.
        - construct_lambdas(...): Computes the 3-tensor `lambda` and regenerates the secret key images, optionally recalculating `sigma` and `mu` parameters.
        - sigma_q_divisor(...): Returns the divisor used to define the ratio `\sigma[q]_{i, j}` for given inputs (i, j).
        - sigma_q(...): Returns the ratio `\sigma[q]_{i, j}` for given inputs (i, j).
        - construct_ell(...): Returns the random matrix `\ell` whose coefficients serve to obscure secret key information within the characterization of the 3-tensor `lambda`.
        - construct_sigma(...): Computes the repartition `sigma`.
    """

    def __init__(self, n: int, p: int, upperbound: int):
        """
        Initializes the main class, setting up the foundational components for cryptographic operations and repartition management.

        This constructor configures the internal state of the class by initializing prime numbers, selecting candidates for the parameter `q`, and preparing attributes needed for further operations such as constructing repartitions, computing noise parameters, and generating secret key information.

        Inputs:
            - n (int): The dimension or size of the secret key, which also determines the size of the repartition.
            - p (int): A number whose prime factors are excluded from potential `q` candidates by adding them to the `units` dictionary.
            - upperbound (int): An upper bound on the numbers whose prime factors are considered to build candidate `q` parameters.

        Attributes:
            - self.n (int): Stores the input parameter `n`.
            - self.primes (Primes): An instance of the `Primes` class for managing prime numbers up to `upperbound`.
            - self.candidate (dict): A selected candidate for the parameter `q`, including its value and factorization.
            - self.q (int): The value of the selected candidate `q`.
            - self.factors (list[int]): A list of prime factors of `q`, including the trivial factor 1.
            - self.n0 (int): The count of prime factors of `q`, excluding the trivial factor 1.
            - self.sigma_done (bool): A flag indicating whether the `sigma` construction has been completed.
            - self.sigma_img (Optional[list[int]]): The image of the `sigma` function, initialized as `None`.
            - self.sigma_fibers (Optional[dict[int, list[int]]]): The fibers of the `sigma` function, initialized as `None`.
            - self.ell (Optional[list[list[int]]]): Constructs the `\ell` matrix used to characterize the 3-tensor `lambda`, initialized as `None`.
            - self.mus (list[int]): A list of parameters `mu` derived from the repartition `sigma`.
            - self.lambdas (list[list[list[int]]]): A 3-tensor `lambda`, generated based on the repartition `sigma` and matrix `\ell`.
            - self.x_images (list[int]): A list of values encoding the vector `x(\omega)`, which represents the image of secret key `x` at the parameter `\omega`.

        Notes:
            - The `Primes` instance handles prime generation and filtering based on the input `p` and `upperbound`.
            - The selected `q` candidate is chosen from the list of filtered candidates, with its factorization stored for later computations.
            - The 3-tensor `lambda` is referred to as "lambdas" in the code because "lambda" is already a reserved keyword in Python.
        """
        # Store the input parameter `n`.
        self.n = n
        
        # Initialize the Primes instance with the specified upperbound.
        self.primes = Primes(upperbound)
        
        # Add the prime factors of `p` to the units dictionary to exclude them from `q` candidates.
        self.primes.add_units(p)
        
        # Find candidates for the `q` parameter.
        candidates = self.primes.find_candidates()
        
        # Select the last candidate (assumed to be the most suitable in the context).
        self.candidate = candidates[-1]
        
        # Extract the `candidate_q` value from the selected candidate.
        self.q = self.candidate["candidate_q"]
        
        # Extract the prime factors of `q`, including the trivial choice 1 (as described in the paper).
        self.factors = [1] + list(self.candidate["factorization"].keys())
        
        # Extract the number of prime factors for the selected `q`.
        self.n0 = self.candidate["factor_count"]
        
        # Initialize flags and placeholders for `sigma` construction.
        self.sigma_done = False
        self.sigma_img = None
        self.sigma_fibers = None
        
        # Initialize noise parameter for the 3-tensor as `None`.
        self.ell = None
        
        # Initialize empty lists for repartition-related parameters.
        self.mus = []
        self.lambdas = []
        self.x_images = []

    def construct(self, new_sigma: bool = True, new_mus: bool = True) -> None:
        """
        Constructs the necessary parameters (`lambdas` and `x_images`) for the cryptographic model.

        This method regenerates parameters based on the provided flags.

        Inputs:
            - new_sigma (bool, optional): If `True`, regenerates the `sigma` parameter. Defaults to `True`.
            - new_mus (bool, optional): If `True`, regenerates the `mus` parameter. Defaults to `True`.

        Outputs:
            - None: Updates `self.lambdas` and `self.x_images` in place.
        """
        # Construct the `lambdas` and `x_images` based on the flags for `sigma` and `mus`.
        self.construct_lambdas(new_sigma=new_sigma, new_mus=new_mus)

    def reconstruct_sigma(self, trivial_factor: bool = False, trivial_sigma: bool = False) -> None:
        """
        Reconstructs the `sigma` parameter with optional constraints on triviality.

        This method resets the `sigma` attributes (`sigma_done`, `sigma_img`, and `sigma_fibers`) and invokes `construct_sigma` to rebuild `sigma` with the specified triviality options.

        Inputs:
            - trivial_factor (bool, optional): If `True`, permits the use of the factor 1 in constructing `sigma`. Defaults to `False`.
            - trivial_sigma (bool, optional): If `True`, generates a trivial `sigma`. Defaults to `False`.

        Outputs:
            - None: Updates `sigma` attributes in place.
        """
        # Reset `sigma` attributes to their initial state.
        self.sigma_done = False
        self.sigma_img = None
        self.sigma_fibers = None

        # Reconstruct `sigma` with the specified options.
        self.construct_sigma(trivial_factor=trivial_factor, trivial_sigma=trivial_sigma)


    def construct_mus(self) -> bool:
        """
        Constructs the list `mus` and the corresponding `x_images` to satisfy a Bézout identity condition.

        This method generates `mus` and `x_images` for each index `k` in `[0, n)` such that the Bézout identity is satisfied. A specific index `k0` is excluded from the initial summation and is later calculated to ensure the identity holds.

        Inputs:
            - None.

        Outputs:
            - bool: Returns `True` if the Bézout identity condition is satisfied 
                    (i.e., the greatest common divisor (gcd) equals 1); `False` otherwise.

        Process:
            1. Randomly selects an index `k0` to exclude from the initial computation.
            2. For all other indices:
                - Generates random values for `mu` and `x_omega` (in `[0, q)`).
                - Updates the Bézout sum using the product of `factors[sigma_img[k]]`, `x_omega`, and `mu`.
            3. Computes the excluded component (`k0`) to complete the Bézout identity:
                - Uses the extended Euclidean algorithm (`extended_gcd`) to find suitable values for `mu` and other components.
            4. Updates `mus` and `x_images` to ensure they satisfy the identity.

        Notes:
            - The method relies on the `factors` and `sigma_img` dictionaries.
            - The modulo operation ensures all values remain in `[0, q)`.
        """
        bezout_sum = 0
        # Initialize the list of `mus`.
        self.mus = []
        # Initialize the list of `x_images`. 
        self.x_images = []  

        # Randomly select an index to exclude from the initial summation.
        k0 = random.randrange(0, self.n)

        # Compute initial components for the Bézout sum, excluding `k0`.
        for k in range(self.n):
            if k == k0:
                # Skip `k0` in this initial loop, leaving placeholders.
                self.mus.append(None)
                self.x_images.append(None)
            else:
                # Generate random values for `mu` and `x_omega`.
                mu = random.randint(0, self.q)
                x_omega = random.randint(0, self.q)

                # Update the Bézout sum.
                bezout_sum += self.factors[self.sigma_img[k]] * x_omega * mu

                # Append the values to `mus` and `x_images`.
                self.mus.append(mu)
                self.x_images.append(x_omega)

        # Compute the Bézout identity for the excluded component (`k0`).
        x_omega = random.randint(0, self.q)
        gcd, modif, mu = extended_gcd(bezout_sum, self.factors[self.sigma_img[k0]] * x_omega)

        # Update `mus` and `x_images` to complete the identity.
        for k in range(len(self.mus)):
            if k == k0:
                # Set the missing `mu` and `x_omega` for `k0`.
                self.mus[k] = mu % self.q
                self.x_images[k] = x_omega
            else:
                # Modify existing `mus` to satisfy the identity.
                self.mus[k] = (modif * self.mus[k]) % self.q

        # Return True if the Bézout identity holds (gcd == 1).
        return gcd == 1


    def construct_lambdas(self, new_sigma: bool = True, new_mus: bool = True) -> None:
        """
        Constructs the 3-tensor `lambda` using the parameters `sigma_img`, `mus`, `x_images`, and `\ell`.

        This method generates a 3-dimensional list `lambdas` (so named because "lambda" is a reserved keyword in Python). Each entry of `lambdas` is computed based on precomputed factors, Bézout values, and a symmetric matrix `\ell`. The construction ensures that all coefficients of the 3-tensor are computed modulo `q`.

        Inputs:
            - new_sigma (bool, optional): Whether to reconstruct `sigma_img` before building `lambdas`. Defaults to `True`.
            - new_mus (bool, optional): Whether to reconstruct `mus` before building `lambdas`. Defaults to `True`.

        Outputs:
            - None: Updates `self.lambdas` in place.

        Process:
            1. Optionally reconstructs `sigma_img` if `new_sigma` is `True`.
            2. Constructs the symmetric matrix `\ell`.
            3. Reconstructs `mus` if necessary, ensuring Bézout identity holds.
            4. Builds the 3-tensor `lambdas` as a 3D list:
                - Outer dimension corresponds to `k` in `[0, n)`.
                - Inner dimensions correspond to `i` and `j` in `[0, n)`.
                - Each value `lambdas[k][i][j]` is computed as:
                    `(factors[sigma_img[k]] * mus[k] * (x_images[i] * x_images[j] - ell[i][j] * sigma_q(i,j))) % q`
        """
        # Optionally reconstruct `sigma_img` if requested.
        if new_sigma:
            self.reconstruct_sigma()

        # Construct the symmetric matrix `\ell`.
        self.construct_ell()

        # Optionally reconstruct `mus` to ensure the Bézout identity holds.
        if new_sigma or new_mus:
            success = self.construct_mus()
            while not success:  # Retry until the identity is satisfied.
                success = self.construct_mus()

        # Initialize the `lambdas` matrix as a 3D list.
        self.lambdas = []

        # Build the `lambdas` matrix.
        for k in range(self.n):
            lambda_k = []
            for i in range(self.n):
                lambda_k_i = []
                for j in range(self.n):
                    # Each lambda coefficient is the product of a term dependent on k and a term dependent on (i, j).
                    tmp_k = self.factors[self.sigma_img[k]] * self.mus[k]
                    tmp_i_j = self.x_images[i] * self.x_images[j] - self.ell[i][j] * self.sigma_q(i, j)
                    
                    # Append the modular result to the innermost list.
                    lambda_k_i.append((tmp_k * tmp_i_j) % self.q)
                # Append the row to the current layer.
                lambda_k.append(lambda_k_i)
            # Append the layer to `lambdas`.
            self.lambdas.append(lambda_k)


    def construct_sigma(self, trivial_factor: bool = False, trivial_sigma: bool = False) -> None:
        """
        Constructs the `n_0`-repartition `sigma` and its associated data.

        This method generates a function `sigma` and its image (`self.sigma_img`), as well as the corresponding fibers (`self.sigma_fibers`) based on the specified parameters. The mapping rules defining the function `sigma` depends on the flags `trivial_factor` and `trivial_sigma`.

        Inputs:
            - trivial_factor (bool): Determines whether `sigma` can map elements to 0. If `True`, `sigma(i)` can equal 0 such that `\sigma[q]_{i, j}` can equal `q`. Default is `False`.
            - trivial_sigma (bool): Forces `sigma` to map all elements to 0. If `True`, `sigma = 0` such that `\sigma[q]_{i, j} = q`. Default is `False`.

        Outputs:
            - None: Updates the following attributes in place:
                - `self.sigma_img` (List[int]): The image of the function `sigma`.
                - `self.sigma_fibers` (Dict[int, List[int]]): A dictionary where keys are values in the image of `sigma`, and values are lists of indices in the domain that map to those values.
                - `self.sigma_done` (bool): Set to `True` after constructing `sigma`.

        Notes:
            - `sigma_img` represents the output of the function `sigma`, where each index corresponds to an element of the domain, and the value at that index is the result of applying `sigma`.
            - `sigma_fibers` groups indices in the domain by their corresponding values in `sigma_img`.
            - The method shuffles the indices in the domain before constructing `sigma` to ensure randomness.

        Example:
            If `self.n = 5`, `self.n0 = 3`, and `trivial_factor = False`:
            - A possible `sigma_img` could be `[2, 3, 1, 2, 3]`.
            - The corresponding `sigma_fibers` would be `{0: [], 1: [2], 2: [0, 3], 3: [1, 4]}`.
        """
        # Proceed only if `sigma` has not been constructed yet.
        if not self.sigma_done:  
            # Generate a shuffled list of indices in the range [0, self.n).
            tmp_indices = list(range(self.n))
            random.shuffle(tmp_indices)

            # Case 1: All elements of `sigma_img` are 0.
            if trivial_sigma:
                self.sigma_img = [0 for _ in tmp_indices]

            # Case 2: `sigma(i)` can be 0, and `\sigma[q]_{i, j}` can equal `q`.
            elif trivial_factor:
                # Introduce a random shift within the range [0, self.n0 + 1).
                shift = random.randrange(0, self.n0 + 1)
                # Construct `sigma_img` as a shifted modulo sequence.
                self.sigma_img = [(shift + i) % (self.n0 + 1) for i in tmp_indices]

            # Case 3: `sigma(i)` > 0, and `\sigma[q]_{i, j}` cannot equal `q`.
            else:
                # Introduce a random shift within the range [0, self.n0).
                shift = random.randrange(0, self.n0)
                # Construct `sigma_img` as a shifted modulo sequence starting from 1.
                self.sigma_img = [1 + ((shift + i) % self.n0) for i in tmp_indices]

            # Define a helper function to find all indices in `img` where the value equals `k`.
            indices = lambda k, img: [i for i, v in enumerate(img) if v == k]

            # Construct `sigma_fibers`: Map each value in the range [0, self.n0 + 1) to the list of indices in `sigma_img` where the value appears.
            self.sigma_fibers = {k: indices(k, self.sigma_img) for k in range(self.n0 + 1)}

            # Mark `sigma` as completed.
            self.sigma_done = True

    def sigma_q_divisor(self, i: int, j: int) -> int:
        """
        Returns the divisor used to define the ratio `\sigma[q]_{i, j}` for given indices `i` and `j`.

        This method calculates the value of `sigma_q_divisor(i, j)` based on the constructed `sigma_img` and associated factors. It first calls the `construct_sigma` method to ensure the necessary mappings are initialized before performing the computation.

        Inputs:
            - i (int): The row index, representing the first component in the calculation.
            - j (int): The column index, representing the second component in the calculation.

        Outputs:
            - int: The value of `sigma_q_divisor(i, j)`: 
                - If `sigma_img[i] == sigma_img[j]`, return the factor corresponding to the shared value of `sigma_img[i]`. 
                - Otherwise, return the product of the factors corresponding to `sigma_img[i]` and `sigma_img[j]`.

        Notes:
            - The method relies on `construct_sigma()` to ensure that the dictionaries `sigma_img` and `factors` are properly initialized.
            - Modulo operations (`i % self.n` and `j % self.n`) are used to handle cases where indices exceed the valid range.

        Example:
            For `self.n = 4`, `self.sigma_img = [1, 2, 1, 3]`, and `self.factors = [q_0, q_1, q_2, q_3]`:
                - `sigma_q_divisor(0, 2)` returns `q_1` (since `sigma_img[0] == sigma_img[2] == 1`).
                - `sigma_q_divisor(1, 3)` returns `q_2 * q_3` (since `sigma_img[1] = 2` and `sigma_img[3] = 3`).
        """
        # Ensure `sigma_img` and related mappings are initialized.
        self.construct_sigma()

        # Reduce indices modulo `self.n` to handle cyclic indexing.
        i_ = i % self.n
        j_ = j % self.n

        # Check if the `sigma_img` values for the two indices are the same.
        if self.sigma_img[i_] == self.sigma_img[j_]:
            # Return the associated factor if `sigma_img[i] == sigma_img[j]`.
            return self.factors[self.sigma_img[i_]]
        else:
            # Otherwise, return the product of the factors for `sigma_img[i]` and `sigma_img[j]`.
            return self.factors[self.sigma_img[i_]] * self.factors[self.sigma_img[j_]]


    def sigma_q(self, i: int, j: int) -> int:
        """
        Computes the value of the ratio `\sigma[q]` for given indices `i` and `j`.

        This method calculates the value `\sigma[q]_{i, j}` as the quotient of `self.q` divided by the value of `sigma_q_divisor(i, j)`.

        Inputs:
            - i (int): The row index, representing the first component in the calculation.
            - j (int): The column index, representing the second component in the calculation.

        Outputs:
            - int: The value of `\sigma[q]_{i, j}`:
                - Computed as `self.q / sigma_q_divisor(i, j)`.

        Notes:
            - The method assumes that `self.q` is a predefined integer value.
            - The calculation of `sigma_q_divisor(i, j)` relies on the `construct_sigma` method to ensure the required mappings are initialized.

        Example:
            For `self.q = 120` and the result of `sigma_q_divisor(0, 1) = 10`:
                - `sigma_q(0, 1)` returns `120 / 10 = 12`.
        """
        # Compute and return the value of `\sigma[q]` evaluated at (i, j) using `sigma_q_divisor`.
        return int(self.q / self.sigma_q_divisor(i, j))


    def construct_ell(self) -> None:
        """
        Constructs the matrix `\ell` for use in the computation of the 3-tensor `lambda`.

        The `\ell` matrix is an `n x n` symmetric matrix with random entries in the range `[0, q)` for indices `(i, j)` where `i <= j`. For indices where `i > j`, the matrix ensures symmetry by setting `ell[i][j] = ell[j][i]`.

        Inputs:
            - None.

        Outputs:
            - None: Updates `self.ell` in place as a symmetric matrix.

        Notes:
            - The matrix is constructed row by row. For each `(i, j)` pair:
                - If `i <= j`, a random value is chosen in the range `[0, q)`.
                - If `i > j`, the value is copied from `ell[j][i]` to ensure symmetry.
            - The random values are generated using `random.randrange(0, self.q)`.

        Example:
            For `n = 3` and `q = 10`, a possible `\ell` matrix might be:
                [
                    [3, 7, 2],
                    [7, 9, 6],
                    [2, 6, 4]
                ]
        """
        # Initialize the `\ell` matrix as an empty list.
        self.ell = []

        # Construct the `\ell` matrix row by row.
        for i in range(self.n):
            # Initialize the row for the current index `i`.
            ell_row = []
            for j in range(self.n):
                if i <= j:
                    # For `i <= j`, generate a random value in `[0, q)`.
                    ell_i_j = random.randrange(0, self.q)
                    ell_row.append(ell_i_j)
                else:
                    # For `i > j`, ensure symmetry by copying the value from `ell[j][i]`.
                    ell_row.append(self.ell[j][i])
            # Add the constructed row to the `\ell` matrix.
            self.ell.append(ell_row)
