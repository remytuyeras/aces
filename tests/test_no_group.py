import sys
import random

sys.path.insert(1, "./")
import pyaces as pyc

def test_no_group():
    """
    Test to ensure that the space of ciphertexts does not define a group structure.

    This test verifies that the ciphertext space in the ACES scheme does not form a group, preventing vulnerabilities associated with "Group Homomorphic Encryption" attacks as described in https://eprint.iacr.org/2014/029.pdf.

    The test proceeds as follows:
    1. Initialize the ACES scheme with a given partition and arithmetic channel.
    2. Encrypt two random messages `m1` and `m2`.
    3. Define an operation on ciphertexts to simulate a group structure check.
    4. Decrypt the resulting ciphertext and compare with expected plaintext subtraction.
    5. If the decrypted result always matches the expected difference, the space may be forming a group.

    Inputs:
    - Random messages `m1` and `m2` chosen from the plaintext space.

    Outputs:
    - Printed comparison of expected and decrypted values.
    - Assertion failure if ciphertexts behave as a group for too many iterations.
    """

    debug = True

    # Initialize the ACES encryption scheme
    repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)
    repartition.construct()
    ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
    public = ac.publish(publish_levels=True)

    # Instantiate Alice and Bob's encryption objects
    alice = pyc.ACESReader(ac, debug=debug)
    bob = pyc.ACES(**public, debug=debug)

    is_group = True
    limit = 100
    count = 0

    while is_group:
        # Generate two random messages
        m1 = random.randrange(ac.p)
        m2 = random.randrange(ac.p)
        
        # Encrypt messages
        cip1 = bob.encrypt(m1)
        cip2 = bob.encrypt(m2)

        # Define subtraction operation on ciphertexts
        c0 = [(cip2.dec[k] - cip1.dec[k]) % ac.u for k in range(ac.n)]
        c1 = (cip2.enc - cip1.enc) % ac.u
        cip3 = pyc.ACESCipher(c0, c1, max(cip2.lvl, (ac.q - cip1.lvl * ac.p) // ac.p))

        # Decrypt the modified ciphertext
        plain = alice.decrypt(cip3)

        print(f"{m2} - {m1} (mod {ac.p}) = {(m2 - m1) % ac.p} but decrypted as {plain}")
        is_group = ((m2 - m1) % ac.p) == plain
        
        count += 1
        if count == limit:
            break

    # Ensure that the ciphertext space does not behave as a group
    assert count < limit and not is_group, "Warning: Ciphertexts seem to have a group structure"

if __name__ == "__main__":
    test_no_group()
