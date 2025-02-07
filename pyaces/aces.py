"""
This code defines a set of classes for performing operations related to homomorphic encryption schemes, focusing on polynomial generation, noise management, key establishment, ciphertext manipulation, and decryption. The primary functionalities are as follows:

Class:
1. class ArithChannel:
   - A class for handling arithmetic channels in the context of the homomorphic encryption scheme ACES. This class provides methods for generating and manipulating polynomials used in noise generation and key creation, with a focus on secure polynomial operations for constructing cryptographic parameters and noisy keys.

Methods:
- ArithChannel.__init__(self, p: int, N: int, deg_u: int, repartition: Repartition, anchor: Callable[[Any], list[int]] = lambda i: [0,1]):
   - Initializes the `ArithChannel` class by generating the necessary polynomials for encryption, including the secret key, initializer, and noisy key polynomials.

- ArithChannel.generate_u(self) -> Polynomial:
   - Generates a random polynomial `u` whose evaluation at `arg = 1` is zero modulo `self.q`.

- ArithChannel.generate_secret(self) -> list[Polynomial]:
   - Generates a list of secret polynomials based on `x_images`, ensuring each polynomial's evaluation at `arg = 1` equals the corresponding `x_image[i]`.

- ArithChannel.generate_vanishers(self) -> list[Polynomial]:
   - Generates a list of polynomials, where each polynomial's evaluation at `arg = 1` equals `p * k`, with `k` randomly chosen from the `anchor` function.

- ArithChannel.generate_initializer(self) -> list[list[Polynomial]]:
   - Generates the initializer matrix `f0`, which is used in key generation and consists of polynomials whose evaluation at `arg = 1` takes the form of a product `q_{\sigma(i)} * r`, where `\sigma` is the repartition function and `q_{\sigma(i)}` is a prime factor of `q`.

- ArithChannel.generate_noisy_key(self) -> list[Polynomial]:
   - Computes the noisy part of the public key as the sum `f0 * x + e`, where `x` is the secret key, `f0` is the initializer matrix, and `e` represents a vector of noisy polynomials.

- ArithChannel.publish(self, publish_levels: bool = True) -> dict:
   - Publishes the generated polynomials and other relevant data for external use, with an option to include noise levels in the published data.

2. class ACESPseudoCipher:
   - Represents a pseudo-ciphertext in the ACES cryptosystem. A pseudo-ciphertext is derived from an `ACESCipher` instance by evaluating its polynomial components at `arg=1`. This class stores the resulting decomposition and encrypted value as integers. It also generates the ciphertexts required for a refresh operation when used with a refresher.

Methods:
- ACESPseudoCipher.__init__(self, dec: list[int], enc: int):
   - Initializes an `ACESPseudoCipher` instance with a decomposition vector and an encrypted value.

- ACESPseudoCipher.corefresher(self, aces: Union[ACES, ACESReader]) -> Tuple[list[ACESCipher], ACESCipher]:
   - Encrypts the components of the pseudo-ciphertext and produces the ciphertexts needed for a refresh operation, to be used alongside the output of `ACESReader.generate_refresher`.

3. class ACESCipher:
   - Represents a ciphertext in the ACES cryptosystem. This class encapsulates a ciphertext `(c, c')`, where `c'` contains the encrypted message and `c` is primarily used for decryption when the secret key is available. It provides methods to convert a ciphertext into a pseudo-ciphertext and to generate the ciphertexts needed for a refresh operation.

Methods:
- ACESCipher.__init__(self, dec: list[Polynomial], enc: Polynomial, lvl: int):
   - Initializes an `ACESCipher` instance with a decomposition vector, an encrypted polynomial, and a noise level.

- ACESCipher.pseudo(self) -> ACESPseudoCipher:
   - Converts the ciphertext into a pseudo-ciphertext by evaluating its polynomial components at `arg=1`.

- ACESCipher.corefresher(self, aces: Union[ACES, ACESReader]) -> Tuple[list[ACESCipher], ACESCipher]:
   - Generates the ciphertexts required for a refresh operation by first converting the ciphertext into a pseudo-ciphertext and then applying `ACESPseudoCipher.corefresher`.

4. class ACES:
   - A class for encrypting messages using the ACES cryptosystem without knowledge of the secret key. This class provides encryption functionality using a public key consisting of polynomials (f0, f1). It enables message encryption while incorporating structured noise for security.

Methods:
- ACES.__init__(self, f0: list[list[Polynomial]], f1: list[Polynomial], 
                p: int, q: int, n: int, N: int, u: Polynomial, 
                levels: list[Optional[int]] = [], debug: bool = False, 
                **args):
   - Initializes the ACES encryption system using the public key.

- ACES.encrypt(self, m: int, anchor: Callable[[Any], int] = lambda v, w: random.randint(0, w)) -> ACESCipher:
   - Encrypts a message using the ACES encryption scheme.

- ACES.generate_b(self, anchor: Callable[[Any, Any], int] = lambda v, w: random.randint(0, w)) -> list[Polynomial]:
   - Generates the decomposition vector `b` for encryption.

- ACES.generate_r_m(self, m: int) -> Polynomial:
   - Generates a polynomial representation of the plaintext message.

5. class ACESReader:
   - A class for handling decryption and encryption in the ACES cryptosystem. This class enables the owner of the secret key to decrypt ciphertexts and also encrypt messages into the general form of ciphertexts. It provides methods for generating encryption parameters, handling noise, and constructing ciphertexts in accordance with the ACES cryptographic framework.

Methods:
- ACESReader.__init__(self, ac: ArithChannel, debug: bool = False):
   - Initializes the ACESReader with parameters from an ArithChannel instance.

- ACESReader.decrypt(self, c: ACESCipher) -> int:
   - Decrypts a ciphertext using the ACES decryption formula.

- ACESReader.encrypt(self, m: int, min_noise: int = 0, max_noise: int = 1, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> ACESCipher:
   - Encrypts a message using the ACES encryption scheme.

- ACESReader.generate_dec(self, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> list[Polynomial]:
   - Generates the decomposition vector `c` for encryption.

- ACESReader.generate_r_m(self, m: int) -> Polynomial:
   - Generates a polynomial representation of the plaintext message.

- ACESReader.generate_vanisher(self, min_noise: int = 0, max_noise: int = 1) -> Polynomial:
   - Generates a noise polynomial for encryption.

- ACESReader.generate_refresher(self, min_noise: int = 0, max_noise: int = 1, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> list[ACESCipher]:
   - Generates refreshed encryptions of the secret key components.
"""

# =======================================
from __future__ import annotations
from .poly import Polynomial
from .repartition import Repartition
import random
import math
from typing import Callable, Tuple, Optional, Union, Any

# =======================================

class ArithChannel(object):
    """
    A class for handling arithmetic channels in the context of the homomorphic encryption scheme ACES. This class provides methods for generating and manipulating polynomials used in noise generation and key establishment, with a focus on secure polynomial operations for the construction of cryptographic parameters and noisy keys in the ACES framework.

    Attributes:
        - N (int): The ciphertext dimension, representing the size of the ciphertext space.
        - p (int): The modulus defining the plaintext space.
        - q (int): The modulus applied to the coefficients of the polynomials in the encryption scheme.
        - x_images (list[int]): A list of integers representing the images of the polynomial components of the secret key `x` at `arg=1`.
        - sigma_img (list[int]): The images defining a partition structure `sigma`.
        - factors (list[int]): The prime factors of the modulus `q` used in the noise generation process.
        - tensor (list[list[list[int]]]): A 3-tensor used to leverage the homomorphic properties of ACES.
        - n (int): The dimension of the secret key `x`.
        - deg_u (int): The degree of the polynomial `u`, which defines the size of the polynomial space.
        - anchor (Callable[[Any], list[int]]): A function that maps the i-th dimension to a list of levels to sample from for noise generation.
        - u (Polynomial): A generated polynomial whose evaluation at `arg=1` is zero modulo `q`, used in cryptographic operations.
        - x (list[Polynomial]): A secret key for the ACES encryption scheme.
        - f0 (list[list[Polynomial]]): A matrix of polynomials, forming part of the public data for the asymmetric version of ACES.
        - f1 (list[Polynomial]): A vector of polynomials, forming part of the public data for the asymmetric version of ACES.

    Methods:
        - generate_u(...): Generates a random polynomial `u` whose evaluation at `arg=1` is zero modulo `q`.
        - generate_secret(...): Generates an ACES secret key based on `x_images`.
        - generate_vanishers(...): Generates a list of noisy components used to conceal the secret key `x` in the construction of the public key.
        - generate_initializer(...): Generates the initializer matrix `f0` used to construct the noisy part of the public key.
        - generate_noisy_key(...): Computes the noisy part of the public key as a combination of `f0` and noise.
        - publish(...): Publishes the generated polynomials and other relevant data for use in the encryption scheme.
    """

    def __init__(self, p: int, N: int, deg_u: int, repartition: Repartition, anchor: Callable[[Any], list[int]] = lambda i: [0, 1]):
        """
        Initializes the `ArithChannel` class, generating the necessary polynomials for encryption, including the secret, initializer, and noisy key polynomials.

        Inputs:
            - p (int): The modulus defining the plaintext space.
            - N (int): The ciphertext dimension, representing the size of the ciphertext space.
            - deg_u (int): The degree of the polynomial `u`, which defines the size of the polynomial space.
            - repartition (Repartition): An object containing parameters (`q`, `x_images`, `sigma_img`, `factors`, `tensor`, `n`) used in cryptographic operations.
            - anchor (Callable[[Any], list[int]], optional): A function that provides a list of levels to sample from for noise generation. Defaults to a function returning `[0, 1]`.

        This method initializes the following attributes:
            - self.N: The ciphertext dimension.
            - self.p: The modulus defining the plaintext space.
            - self.q: The encryption modulus, derived from the repartition.
            - self.x_images: The list of `x_i(omega)` values for secret key polynomial generation, evaluated at `arg=1`.
            - self.sigma_img: The list of sigma values used in the partition structure `sigma`.
            - self.factors: The prime factors of `q`, used in the noise and key generation processes.
            - self.tensor: A tensor used for polynomial transformations in encryption.
            - self.n: The dimension of the secret key `x`.
            - self.deg_u: The degree of the polynomial `u`, used in various polynomial generation methods.
            - self.anchor: The function that maps the i-th dimension to noise levels.
            - self.u: The generated polynomial `u`, whose evaluation at `arg=1` is zero modulo `q`.
            - self.x: The list of secret polynomials intended to be used as a secret key for ACES.
            - self.f0: The initializer matrix `f0`, used in the construction of the noisy key.
            - self.f1: The noisy part of the public key, generated from the matrix `f0` and noise.
        """
        # Unused in the current implementation
        self._omega = 1

        # The ciphertext dimension
        self.N = N 
        # The modulus defining the plaintext space 
        self.p = p  
        # The encryption modulus from the repartition
        self.q = repartition.q  
        # List of integers used to infer the secret key `x`
        self.x_images = repartition.x_images  
        # The images defining the repartition structure `sigma`
        self.sigma_img = repartition.sigma_img  
        # The prime factors of `q`, used in noise generation
        self.factors = repartition.factors 
        # A 3-tensor used in polynomial transformations for encryption 
        self.tensor = repartition.lambdas  
        # The dimension of the secret key `x`
        self.n = repartition.n  
        # The degree of the polynomial `u`, defining the polynomial space size
        self.deg_u = deg_u  
        # Function mapping dimensions to noise levels for noise generation
        self.anchor = anchor  

        # Generate the polynomial `u`, whose evaluation at `arg=1` is zero modulo `q`
        self.u = self.generate_u()  

        # Generate the secret key `x`
        self.x = self.generate_secret()  

        # Generate the initializer matrix `f0` for the noisy part of the public key
        self.f0 = self.generate_initializer()  

        # Generate the noisy part of the public key
        self.f1 = self.generate_noisy_key()  

    def generate_u(self) -> Polynomial:
        """
        Generates a random polynomial `u` whose evaluation at `arg=1` is zero modulo `self.q`.

        This method generates a random polynomial and adjusts it so that its evaluation at `arg = 1` is zero modulo `self.q`. The polynomial is shifted so that the evaluation at `arg = 1` equals zero modulo `q`.

        Outputs:
            - Polynomial: The generated polynomial `u` with the required properties.
        """
        # Generate a random polynomial
        randpoly = Polynomial.random(self.q, self.deg_u)  

        # Append the leading coefficient as 1
        randpoly.coefs.append(1)  

        # Adjust to ensure evaluation at 1 is zero modulo q
        shift = Polynomial.randshift(self.q - randpoly(arg=1), self.q, self.deg_u) 

        # Return the polynomial with the desired properties 
        return shift + randpoly  

    def generate_secret(self) -> list[Polynomial]:
        """
        Generates a list of secret polynomials, each based on a corresponding `x_image`.

        This method generates secret polynomials for each `x_image[i]`, ensuring that each polynomial's evaluation at `arg = 1` equals `x_image[i]`. Each polynomial is adjusted by adding a shift to a random polynomial.

        Outputs:
            - list[Polynomial]: A list of secret polynomials used for encryption.
        """
        x = []
        for i in range(self.n):

            # Generate a random polynomial
            randpoly = Polynomial.random(self.q, self.deg_u)  

            # Adjust to match x_image[i]
            shift = Polynomial.randshift(self.x_images[i] - randpoly(arg=1), self.q, self.deg_u)  

            # Append the adjusted polynomial
            x.append(shift + randpoly)  
            
        return x  

    def generate_vanishers(self) -> list[Polynomial]:
        """
        Generates a list of polynomials belonging to the vanishing ideal associated with ACES. Each vanishing polynomial's evaluation at `arg = 1` must take the form of a product `p * k` for some level `k`.

        This method generates polynomials used for noise generation in the encryption process, with each polynomial's evaluation at `arg = 1` set to `p * k`, where `k` is randomly chosen from the anchor function.

        Outputs:
            - list[Polynomial]: A list of vanishing polynomials used for noise generation.
        """
        e = []
        for i in range(self.N):

            # Choose a level from the anchor function
            k = random.choice(self.anchor(i)) 

            # Generate a random polynomial
            randpoly = Polynomial.random(self.q, self.deg_u)  

            # Adjust to match p * k
            shift = Polynomial.randshift(self.p * k - randpoly(arg=1), self.q, self.deg_u)  

            # Append the adjusted polynomial
            e.append(shift + randpoly)  

        return e

    def generate_initializer(self) -> list[list[Polynomial]]:
        """
        Generates the initializer matrix `f0`, which is a list of lists of polynomials.

        This method generates the initializer matrix `f0`, used for key generation. Each entry in the matrix is a polynomial whose evaluation at `arg = 1` takes the form of a product `q_{\sigma(i)} \cdot r`, where `\sigma(i)` refers to the i-th image of the repartition function `sigma` and `q_{\sigma(i)}` refers to one of the prime factors of `q`.

        Outputs:
            - list[list[Polynomial]]: The initializer matrix `f0`.
        """
        f0 = []
        for _ in range(self.N):
            # Initialize the row for the matrix
            row = []  
            for k in range(self.n):

                # Random coefficient
                r = random.randrange(self.q)  

                # Generate a random polynomial
                randpoly = Polynomial.random(self.q, self.deg_u)  

                # Adjust to match factor
                shift = Polynomial.randshift(self.factors[self.sigma_img[k]] * r - randpoly(arg=1), self.q, self.deg_u)  

                # Append the adjusted polynomial to the row
                row.append(shift + randpoly)  

            # Append the row to the matrix
            f0.append(row)  

        return f0

    def generate_noisy_key(self) -> list[Polynomial]:
        """
        Generates the noisy part of the public key, which is computed as the sum of the initializer matrix `f0` and a noise component.

        This method computes the noisy part of the public key by performing matrix multiplication between `f0` and the secret polynomials `x`, and adding the noise component generated by `generate_vanishers`.

        Outputs:
            - list[Polynomial]: A vector of polynomials constituting the value of the attribute `self.f1`.
        """
        # Initialize the noisy key with zero polynomials
        f1 = [Polynomial([0], self.q) for _ in range(self.N)]  

        # Generate the vanishing polynomials (noise)
        e = self.generate_vanishers()  

        for i in range(self.N):
            for j in range(self.n):

                # Multiply f0 by the secret polynomials x
                f1[i] = f1[i] + self.f0[i][j] * self.x[j]  

            # Add the noise component
            f1[i] = (f1[i] + e[i]) % self.u  

        return f1  

    def publish(self, publish_levels: bool = True) -> dict:
        """
        Publishes the generated polynomials and other relevant data for external use.

        This method collects the generated polynomials (`f0`, `f1`, etc.) and other parameters into a dictionary and returns it. Optionally, it can include the levels of the noisy components used to conceal the secret key in the construction of the attribute `f1`.

        Inputs:
            - publish_levels (bool, optional): A flag to indicate whether to include levels in the published data. Defaults to `True`.

        Outputs:
            - dict: A dictionary containing the generated polynomials and other relevant data, including the levels and max saturation if applicable.
        """
        # Calculate the maximum level based on q and p
        max_level = (self.q + 1) // self.p - 1

        # Compute levels for each dimension
        levels = [min(max_level, max(self.anchor(i))) if publish_levels else 0 for i in range(self.N)]  

        # Return the dictionary with all relevant data
        return {
            "f0": self.f0,
            "f1": self.f1,
            "p": self.p,
            "q": self.q,
            "n": self.n,
            "N": self.N,
            "u": self.u,
            "tensor": self.tensor,
            "levels": levels,
            "max_saturation": round(100 * max(levels) / max_level, 4)  # Percentage of max saturation
        }  

# =======================================

class ACESPseudoCipher(object):
    """
    A class representing a pseudo-ciphertext in the ACES cryptosystem.

    This class provides a representation for pseudo-ciphertexts, which are typically derived from `ACESCipher` instances. In this case, the pseudo-ciphertext is obtained by evaluating the polynomial components of an `ACESCipher` instance at `arg=1`. The class also generates the set of ciphertexts required for a refresh operation. These ciphertexts, obtained via the `corefresher` method, are meant to be used alongside the output of `ACESReader.generate_refresher`.

    Attributes:
        - dec (list[int]): The first component of a pseudo-ciphertext.
        - enc (int): The second component of a pseudo-ciphertext.
    
    Methods:
        - corefresher(...) -> Tuple[list[ACESCipher], ACESCipher]: Generates ciphertexts required for the refresh operation.
    """

    def __init__(self, dec: list[int], enc: int):
        """
        Initializes an ACESPseudoCipher instance.

        Inputs:
            - dec (list[int]): The first component of a pseudo-ciphertext as a list of integers.
            - enc (int): The second component of a pseudo-ciphertext as an integer.
        """
        self.dec = dec
        self.enc = enc

    def corefresher(self, aces: Union[ACES, ACESReader]) -> Tuple[list[ACESCipher], ACESCipher]:
        """
        Generates the ciphertexts needed for a refresh operation.

        This method encrypts each component of the pseudo-ciphertext so that it can be passed as input to `ACESAlgebra.refresh`, along with the output of `ACESReader.generate_refresher`.

        Inputs:
            - aces (Union[ACES, ACESReader]): An instance of the ACES cryptosystem, either in asymmetric (ACES) or symmetric (ACESReader) mode.

        Outputs:
            - Tuple[list[ACESCipher], ACESCipher]: A collection of ciphertexts encrypting the components of the pseudo-ciphertext.
        """
        return [aces.encrypt(dec_i % aces.p) for dec_i in self.dec], aces.encrypt(self.enc % aces.p)

# =======================================

class ACESCipher(object):
    """
    A class representing a ciphertext in the ACES cryptosystem.

    This class defines an ACES ciphertext `(c, c')`, where:
    - `c'` contains the encrypted message.
    - `c` is primarily used for decryption when the secret key is available.

    The class provides methods to convert a ciphertext into a pseudo-ciphertext and to generate the necessary ciphertexts for a refresh operation.

    Attributes:
        - dec (list[Polynomial]): The component of the ciphertext used for decryption.
        - enc (Polynomial): The component of the ciphertext containing the message.
        - lvl (int): The noise level associated with the ciphertext.
    
    Methods:
        - pseudo(...): Converts the ciphertext into a pseudo-ciphertext.
        - corefresher(...): Generates ciphertexts required for the refresh operation.
    """

    def __init__(self, dec: list[Polynomial], enc: Polynomial, lvl: int):
        """
        Initializes an ACESCipher instance.

        Inputs:
            - dec (list[Polynomial]): A vector of polynomials primarily used for decryption. It interacts with the secret key via a scalar product.
            - enc (Polynomial): A polynomial concealing a message as a sum of random and deterministic polynomial expressions.
            - lvl (int): The noise level of the ciphertext.
        """
        self.dec = dec
        self.enc = enc
        self.lvl = lvl

    def pseudo(self) -> ACESPseudoCipher:
        """
        Converts the ciphertext into a pseudo-ciphertext.

        This method evaluates the polynomials composing the ciphertext at `arg=1`, yielding the associated pseudo-ciphertext.

        Outputs:
            - ACESPseudoCipher: The pseudo-ciphertext associated with the ciphertext.
        """
        enc = self.enc(arg=1)
        dec = [(dec_i.intmod - dec_i(arg=1)) % dec_i.intmod for dec_i in self.dec]
        return ACESPseudoCipher(dec, enc)
    
    def corefresher(self, aces: Union[ACES, ACESReader]) -> Tuple[list[ACESCipher], ACESCipher]:
        """
        Generates the ciphertexts needed for a refresh operation.

        This method first converts the ciphertext into a pseudo-ciphertext, then applies `ACESPseudoCipher.corefresher` to generate the ciphertexts required for refreshing the ciphertext.

        In practice, these ciphertexts are used as input to `ACESAlgebra.refresh`, along with the output of `ACESReader.generate_refresher`.

        Inputs:
            - aces (Union[ACES, ACESReader]): An instance of the ACES cryptosystem, either in asymmetric (ACES) or symmetric (ACESReader) mode.

        Outputs:
            - Tuple[list[ACESCipher], ACESCipher]: A collection of ciphertexts to be passed to the method `ACESAlgebra.refresh` as its second input.
        """
        pseudo_cipher = self.pseudo()
        return pseudo_cipher.corefresher(aces)

# =======================================

class ACES(object):
    """
    A class for encrypting messages using the ACES cryptosystem without knowledge of the secret key.
    
    This class provides encryption functionality using a public key consisting of polynomials (`f0`, `f1`). It enables message encryption while incorporating structured noise components for enhanced security, providing a fully homomorphic encryption system without requiring access to the secret key. Typically, this class is initialized with the output of the method `ArithChannel.publish`.

    Attributes:
        - f0 (list[list[Polynomial]]): A matrix of polynomials forming part of the public key. These polynomials are used to construct the value of the attribute `f1`.
        - f1 (list[Polynomial]): A list of polynomials forming part of the public key. These polynomials are used in the encryption process to help hide the plaintext.
        - p (int): The plaintext modulus, used to define the space for the message being encrypted.
        - q (int): The ciphertext modulus, used for encoding the encrypted message.
        - n (int): The dimension of the secret key, which determines the number of polynomials in the rows of the matrix `f0`.
        - N (int): The number of noise components used in the encryption process. This influences the security of the encryption by adding noise to the ciphertext.
        - u (Polynomial): The auxiliary modulus used for encryption computations, influencing how the encryption operations are performed.
        - levels (list[Optional[int]]): Noise scaling factors for different encryption levels. This helps adjust the noise distribution during the encryption process.
        - debug (bool): A flag indicating whether debug messages should be printed during encryption.

    Methods:
        - encrypt(...): Encrypts a message using the ACES encryption scheme, applying the public key and noise components.
        - generate_b(...): Generates the noise components used in encryption, which are added to the ciphertext to maintain security.
        - generate_r_m(...): Generates a polynomial representation of the plaintext message, mapping the message to a form that can be encrypted.
    """
    
    def __init__(self, 
                 f0: list[list[Polynomial]], f1: list[Polynomial], 
                 p: int, q: int, n: int, N: int, u: Polynomial, 
                 levels: list[Optional[int]] = [], debug: bool = False, 
                 **args):
        """
        Initializes the ACES encryption system using the public key `f0` and `f1`, as well as other encryption parameters.

        Inputs:
            - f0 (list[list[Polynomial]]): A matrix of polynomials forming part of the public key, used in the encryption process.
            - f1 (list[Polynomial]): A list of polynomials forming part of the public key, used in conjunction with `f0` for encryption and decryption.
            - p (int): The plaintext modulus, defining the space for the message.
            - q (int): The ciphertext modulus, used for encoding the encrypted message.
            - n (int): The dimension of the secret key, which determines the number of polynomials in the rows of the matrix `f0`.
            - N (int): The number of noise components used in the encryption process.
            - u (Polynomial): The auxiliary modulus used for encryption computations.
            - levels (list[Optional[int]], optional): Noise scaling factors for encryption levels. Defaults to an empty list.
            - debug (bool, optional): A flag to enable debug messages during encryption. Defaults to `False`.
            - **args: Additional parameters passed via the double-star operator. These parameters can be used to pass public key data generated by an `ArithChannel` instance as a single double-starred argument.
        """
        self.f0 = f0
        self.f1 = f1
        self.p = p
        self.q = q
        self.n = n
        self.N = N
        self.u = u
        self.levels = levels
        self.debug = debug

    def encrypt(self, m: int, anchor: Callable[[Any], int] = lambda v, w: random.randint(0, w)) -> ACESCipher:
        """
        Encrypts a message using the ACES encryption scheme.

        This method encrypts a plaintext message using structured randomness and the public key `(f0, f1)` to produce ciphertext. The encryption process incorporates multiplicative noise components to ensure security.

        Inputs:
            - m (int): The plaintext message to encrypt.
            - anchor (Callable, optional): A function for introducing randomness in the encryption process. Defaults to a uniform random function.

        Outputs:
            - ACESCipher: The ciphertext resulting from the encryption of the message `m`.
        """
        if self.debug and m >= self.p:
            print(f"\033[93mWarning in ACES.encrypt: The input message is encrypted as {m % self.p} and adds {m // self.p} points to the noise level.\033[0m")
        
        # Generate the multiplicative noise components, stored in the list `b`, used for encryption
        b = self.generate_b(anchor=anchor)

        # Generate the message encoding polynomial `r_m`, which represents the message
        enc = self.generate_r_m(m)
        
        # Compute the part of the ciphertext that hides the message, using `f1`
        for i in range(self.N):
            enc = enc + b[i] * self.f1[i]
        enc = enc % self.u
        
        # Compute the part of the ciphertext usually used for decryption, using `f0`
        dec = []
        for j in range(self.n):
            dec_j = Polynomial([0], self.q)
            for i in range(self.N):
                dec_j = dec_j + b[i] * self.f0[i][j]
            dec.append(dec_j % self.u)
        
        # Compute the noise contribution associated with `f1`
        f1_noise = sum([max(1, math.ceil(b[i](arg=1) / self.p)) * level * self.p if isinstance(level, int) else 0 for i, level in enumerate(self.levels)])
        noise = f1_noise + m // self.p

        if self.debug:
            total_noise = (self.q + 1) // self.p - 1
            print(f"\033[93mWarning in ACES.encrypt: encryption starting at {round(100 * noise / total_noise, 4)}% of max. noise level.\033[0m")
        
        return ACESCipher(dec, enc, noise)


    def generate_b(self, anchor: Callable[[Any, Any], int] = lambda v, w: random.randint(0, w)) -> list[Polynomial]:
        """
        Generates the multiplicative noise components used in the encryption process.

        This method creates a list of polynomials whose evaluations at `arg=1` correspond to random values generated by the `anchor` function. These polynomials contribute noise to the ciphertext, ensuring security by obscuring the plaintext during encryption.

        Inputs:
            - anchor (Callable, optional): A function for introducing randomness in the noise generation process. The default is a uniform random selection.

        Outputs:
            - list[Polynomial]: A list of polynomials used as multiplicative noise components in the encryption process.
        """
        b = []
        deg_u = self.u.degree()
        for i in range(self.N):

            # Generate a random value using the anchor function
            b_i = anchor(i, self.p)

            # Generate a random polynomial
            randpoly = Polynomial.random(self.q, deg_u)

            # Adjust the polynomial to match the random value at arg=1  
            shift = Polynomial.randshift(b_i - randpoly(arg=1), self.q, deg_u)

            # Append the final polynomial to the list  
            b.append(shift + randpoly)  

        return b

    def generate_r_m(self, m: int) -> Polynomial:
        """
        Generates a polynomial representation of the plaintext message `m`.

        This method constructs a polynomial whose evaluation at `arg=1` equals the message `m`. The polynomial is generated by adding a random polynomial and adjusting it to ensure that the value at `arg=1` matches `m`.

        Inputs:
            - m (int): The plaintext message to be represented as a polynomial.

        Outputs:
            - Polynomial: A polynomial whose evaluation at `arg=1` equals `m`.
        """
        # Degree of the polynomial
        deg_u = self.u.degree()  

        # Generate a random polynomial
        randpoly = Polynomial.random(self.q, deg_u)  

        # Adjust to match the message at arg=1
        shift = Polynomial.randshift(m - randpoly(arg=1), self.q, deg_u)  

        # Return the adjusted polynomial representing `m`
        return shift + randpoly  

# =======================================

class ACESReader(object):
    """
    A class for handling decryption and encryption in the ACES cryptosystem.
    
    This class enables the owner of the secret key to decrypt ciphertexts and encrypt messages into ciphertexts that conform to the ACES structure. It provides methods for generating encryption parameters, handling noise, and constructing ciphertexts in accordance with the ACES cryptographic framework.

    Attributes:
        - x (list[Polynomial]): The secret key of the cryptosystem, represented as a list of polynomials.
        - p (int): The plaintext modulus.
        - q (int): The ciphertext modulus.
        - n (int): The dimension of the secret key.
        - u (int): An auxiliary modulus used in encryption computations.
        - deg_u (int): The degree of the polynomial `u`.
        - sigma_img (list[int]): The images defining a partition structure `sigma`.
        - factors (list[int]): The prime factors of the modulus `q` used in the noise generation process.
        - debug (bool): A flag indicating whether debug messages should be printed during encryption.
    
    Methods:
        - decrypt(...): Decrypts a ciphertext using the ACES decryption formula.
        - encrypt(...): Encrypts a message using the ACES encryption scheme.
        - generate_dec(...): Generates the part of the ciphertext that interacts with the secret key for both decryption and encryption.
        - generate_r_m(...): Generates a polynomial representation of the plaintext message.
        - generate_vanisher(...): Generates a noise polynomial for encryption.
        - generate_refresher(...): Generates a refresher structure consisting of ciphertexts that encrypt information derived from secret key components.
    """

    def __init__(self, ac: ArithChannel, debug: bool = False):
        """
        Initializes the ACESReader with parameters from an ArithChannel instance.

        Inputs:
            - ac (ArithChannel): An instance containing all necessary cryptographic parameters for ACES.
            - debug (bool, optional): A flag enabling debug messages during encryption. Default is False.
        """
        self.x = ac.x
        self.p = ac.p
        self.q = ac.q
        self.n = ac.n
        self.u = ac.u
        self.deg_u = ac.deg_u
        self.sigma_img = ac.sigma_img
        self.factors = ac.factors
        self.debug = debug

    def decrypt(self, c: ACESCipher) -> int:
        """
        Decrypts a ciphertext using the ACES decryption formula.

        This method decrypts a given ciphertext by computing the scalar product between the secret key and the list of polynomials stored in `c.dec`. The result is then subtracted from the second component of the ciphertext (`c.enc`), and modular reduction is applied to retrieve the plaintext.

        Inputs:
            - c (ACESCipher): The ciphertext to decrypt.

        Outputs:
            - int: The recovered plaintext message.
        """
        cTx = Polynomial([0], self.q)
        
        # Compute the scalar product between c.dec and the secret key `x`
        for i in range(self.n):
            cTx = cTx + c.dec[i] * self.x[i]
        
        # Compute the intermediate decrypted value before modular reduction
        m_pre = c.enc - cTx
        
        # Apply modular reduction to recover the plaintext message
        return (m_pre(arg=1) % self.q) % self.p

    def encrypt(self, m: int, min_noise: int = 0, max_noise: int = 1, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> ACESCipher:
        """
        Encrypts a message using the ACES encryption scheme.

        This method generates a ciphertext corresponding to the plaintext input, adding structured noise to ensure security.

        Inputs:
            - m (int): The plaintext message to encrypt.
            - min_noise (int, optional): The minimum noise level applied to the encryption process. Default is 0.
            - max_noise (int, optional): The upper bound for the noise level added to encryption. Default is 1.
            - anchor (Callable, optional): A function that introduces randomness in the ciphertext generation process. Defaults to a uniform random function.

        Outputs:
            - ACESCipher: A ciphertext consisting of a decomposition vector and an encrypted polynomial.
        """
        if self.debug and m >= self.p:
            print(f"\033[93mWarning in ACESReader.encrypt: the input is encrypted as {m % self.p} and adds {m // self.p} point to noise level.\033[0m")
        
        # Generate the vector component of the ciphertext that interacts with the secret key `x` via a scalar product
        dec = self.generate_dec(anchor=anchor)

        # Generate the message encoding polynomial r_m
        r_m = self.generate_r_m(m)
        
        # Generate the noise polynomial e
        e = self.generate_vanisher(min_noise=min_noise, max_noise=max_noise)
        
        # Compute the ciphertext component containing the polynomial r_m and contributions from the secret key interaction
        enc = r_m + e
        for i in range(self.n):
            enc = enc + dec[i] * self.x[i]
        enc = enc % self.u

        # Add the message's noise contribution to that of the noise component when `m` is greater than `self.p`
        noise = max_noise + m // self.p

        if self.debug:
            total_noise = (self.q + 1) // self.p - 1
            print(f"\033[93mWarning in ACESReader.encrypt: encryption starting at {round(100 * noise / total_noise, 4)}% of max. noise level.\033[0m")

        return ACESCipher(dec, enc, noise)
    
    def generate_dec(self, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> list[Polynomial]:
        """
        Generates the vector component of the ciphertext that interacts with the secret key `x` via a scalar product.

        This method creates a list of polynomials whose evaluations at `arg=1` satisfy a scaling relation determined by `sigma_img` and `factors`.

        Inputs:
            - anchor (Callable, optional): A function for generating random scaling factors used in ciphertext construction. Defaults to uniform random selection.

        Outputs:
            - list[Polynomial]: A list of polynomials forming the decomposition vector.
        """
        dec = []
        for k in range(self.n):
            # Generate a random scaling factor r_k using the anchor function
            r_k = anchor(k, self.q)
            
            # Generate a random polynomial
            randpoly = Polynomial.random(self.q, self.deg_u)
            
            # Adjust the polynomial to satisfy the required scaling relation at arg=1
            shift = Polynomial.randshift(self.factors[self.sigma_img[k]] * r_k - randpoly(arg=1), self.q, self.deg_u)
            
            # Append the adjusted polynomial to the ciphertext component
            dec.append(shift + randpoly)
        
        return dec

    def generate_r_m(self, m: int) -> Polynomial:
        """
        Generates a polynomial representation of the plaintext message.

        This method ensures that the polynomial evaluates to `m` at `arg=1` by adjusting the polynomial.

        Inputs:
            - m (int): The plaintext message to be represented as a polynomial.

        Outputs:
            - Polynomial: A polynomial whose evaluation at `arg=1` equals `m`.
        """
        # Generate a random polynomial
        randpoly = Polynomial.random(self.q, self.deg_u)  

        # Adjust the polynomial to match `m` at `arg=1`
        shift = Polynomial.randshift(m - randpoly(arg=1), self.q, self.deg_u)  

        # Return the adjusted polynomial
        return shift + randpoly  
    
    def generate_vanisher(self, min_noise: int = 0, max_noise: int = 1) -> Polynomial:
        """
        Generates a noise polynomial for encryption.

        This polynomial ensures that its evaluation at `arg=1` is a multiple of `p`, contributing to structured noise in ciphertexts and enhancing encryption security.

        Inputs:
            - min_noise (int, optional): The minimum noise level to apply. Default is 0.
            - max_noise (int, optional): The maximum noise level to apply. Default is 1.

        Outputs:
            - Polynomial: A polynomial contributing to encryption noise.
        """
        # Generate a noise value within bounds
        noise = random.randint(max(0, min_noise), min(self.q // self.p, max_noise))  

        # Generate a random polynomial
        randpoly = Polynomial.random(self.q, self.deg_u)  

        # Adjust to ensure evaluation at `arg=1` is a multiple of `p`
        shift = Polynomial.randshift(self.p * noise - randpoly(arg=1), self.q, self.deg_u)  

        # Return the adjusted polynomial
        return shift + randpoly  

    
    def generate_refresher(self, min_noise: int = 0, max_noise: int = 1, anchor: Callable[[Any, Any], int] = lambda v, w: random.randrange(w)) -> list[ACESCipher]:
        """
        Generates a refresher structure, consisting of ciphertexts that encrypt information derived from the secret key components.

        Inputs:
            - min_noise (int, optional): Minimum noise level. Default is 0.
            - max_noise (int, optional): Maximum noise level. Default is 1.
            - anchor (Callable, optional): A function for generating randomness in the noise generation process. Default is uniform random selection.

        Outputs:
            - list[ACESCipher]: A list of ciphertexts that encrypt information derived from the secret key components.

        """
        return [self.encrypt(m=(x_i(arg=1) % self.p), min_noise=min_noise, max_noise=max_noise, anchor=anchor) for x_i in self.x]
