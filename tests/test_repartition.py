import sys

sys.path.insert(1, "./")
import pyaces as pyc


def test_repartition():
    """
    Test for the Repartition class in the pyaces module.

    This test demonstrates the functionality of the Repartition class, including:

    1. Initializing the Repartition class with parameters `n`, `p`, and `upperbound`, and verifying the properties of the generated candidate prime `q`.

    2. Reconstructing the `sigma` structure using the `reconstruct_sigma()` method, with multiple configurations (default, trivial_sigma, trivial_factor).

    3. Constructing the `mus` coefficients using the `construct_mus()` method, and ensuring that the boolean value returned (`gcd_is_one`) correctly reflects whether the Bezout identity, associated with the mus coefficients, has a gcd of 1. This is verified by checking if the sum `\sum_k x_k(\omega) \cdot q_{\sigma(k)} \cdot \mu_k` modulo `q` equals 1.

    4. Validating the `construct()` method by checking the properties of `lambda` matrices, `ell` matrix, and relations between `x` images and the lambda values.

    Inputs:
    - n: Number of elements in the partition.
    - p: Some parameter (context specific).
    - upperbound: Upper bound for prime generation and selection of candidate prime `q`.

    Outputs:
    - Printed verification of each step, showing intermediate results and values.
    - Images of the secret key `x = (x_1, ..., x_n)`, represented by `x_images`.
    - Assertions to ensure correctness of computations, gcd conditions, and matrix relations.
    """

    # Step 1: Initialize the Repartition class with parameters `n`, `p`, and `upperbound`
    print("==== Repartition.__init__() ====")
    repartition = pyc.Repartition(
        n=5, p=2, upperbound=47601551
    )  # Initialize with parameters
    print("n =", repartition.n)
    print("data for q =", repartition.candidate)
    print("q =", repartition.q)
    print("factors =", repartition.factors)
    print("n0 =", repartition.n0)

    # Step 2: Reconstruct the `sigma` structure
    print("\n==== Repartition.reconstruct_sigma() ====")

    # Default reconstruction (no trivial factors or sigma)
    repartition.reconstruct_sigma()
    print("sigma_done =", repartition.sigma_done)
    print("sigma_img =", repartition.sigma_img)
    print("sigma_fibers =", repartition.sigma_fibers)
    assert 0 not in repartition.sigma_img  # Ensure 0 is not in sigma_img

    # Reconstruct with trivial sigma
    repartition.reconstruct_sigma(trivial_sigma=True)
    print("sigma_done =", repartition.sigma_done)
    print("sigma_img =", repartition.sigma_img)
    print("sigma_fibers =", repartition.sigma_fibers)
    assert len(repartition.sigma_fibers[0]) == len(
        repartition.sigma_img
    )  # Check lengths match

    # Reconstruct with trivial factor
    repartition.reconstruct_sigma(trivial_factor=True)
    print("sigma_done =", repartition.sigma_done)
    print("sigma_img =", repartition.sigma_img)
    print("sigma_fibers =", repartition.sigma_fibers)

    # Step 3: Construct the `mus` coefficients
    print("\n==== Repartition.construct_mus() ====")
    gcd_is_one = repartition.construct_mus()
    print("mus =", repartition.mus)
    print("x_images =", repartition.x_images)

    # Verify the sum condition
    print(
        "\nIs the sum (\\sum_k x_k(omega) * q_{\\sigma(k)} * mu_k) equal to 1?",
        gcd_is_one,
    )
    bezout_sum = 0
    for k in range(repartition.n):
        bezout_sum += (
            repartition.factors[repartition.sigma_img[k]]
            * repartition.mus[k]
            * repartition.x_images[k]
        )

    print(
        "We can verify that \\sum_k x_k(omega) * q_{\\sigma(k)} * mu_k =",
        bezout_sum % repartition.q,
        ", which is " + ("indeed" if gcd_is_one else "not") + " 1",
    )

    assert (bezout_sum % repartition.q == 1) or not (gcd_is_one), (
        "Error in construct_mus()"
    )

    # Step 4: Use the `construct()` method and check matrix relations
    print("\n===== Repartition.construct() =====\n")
    repartition.construct()
    bezout_sum = 0
    for k in range(repartition.n):
        bezout_sum += (
            repartition.factors[repartition.sigma_img[k]]
            * repartition.mus[k]
            * repartition.x_images[k]
        )

    print("gcd =", bezout_sum % repartition.q)
    print("x_images =", repartition.x_images)

    # Step 5: Display lambda matrices and ell matrix
    print("\n~~~ display lambda matrices ~~~")
    for k in range(len(repartition.lambdas)):
        for i in range(len(repartition.lambdas[k])):
            print(repartition.lambdas[k][i])
        print()

    print("\n~~~ display ell matrix ~~~")
    for row in repartition.ell:
        print(row)
    print()

    # Step 6: Check lambda relations with x images
    print("\n~~~ check lambda relations with x ~~~")
    for i in range(repartition.n):
        for j in range(repartition.n):
            result = repartition.x_images[i] * repartition.x_images[
                j
            ] - repartition.ell[i][j] * repartition.sigma_q(i, j)
            linear_i_j = 0
            for k in range(repartition.n):
                linear_i_j += repartition.lambdas[k][i][j] * repartition.x_images[k]

            print(
                f"x_{{{i}}}(omega) x_{{{j}}}(omega)-\\ell_{{{i, j}}}\\sigma[q]_{{{i, j}}} \t=",
                result % repartition.q,
                "|",
                linear_i_j % repartition.q,
                f"= \t\\sum_k x_k(omega) \\lambda_{{{i, j}}}^k",
            )

            assert result % repartition.q == linear_i_j % repartition.q, (
                "Error in construct()"
            )


if __name__ == "__main__":
    test_repartition()
