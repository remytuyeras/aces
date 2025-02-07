import sys 
sys.path.insert(1,"./")
import pyaces as pyc
import random

debug = True

repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)
repartition.construct()
ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
public = ac.publish(publish_levels=True)

alice = pyc.ACESReader(ac, debug=debug)
bob = pyc.ACES(**public, debug=debug)

m1 = random.randrange(ac.p) 
m2 = random.randrange(ac.p) 

print(f"\nbob encrypts {m1} (mod {ac.p}):")
cip1 = bob.encrypt(m1)
assert isinstance(cip1, pyc.ACESCipher) and alice.decrypt(cip1) == m1, "Error in ACES.encrypt()"

print(f"\nbob encrypts {m2} (mod {ac.p}):")
cip2 = bob.encrypt(m2)
assert isinstance(cip2, pyc.ACESCipher) and alice.decrypt(cip2) == m2, "Error in ACES.encrypt()"

alg = pyc.ACESAlgebra(**public, debug=debug)

print("\n==== Test ACESAlgebra.add and ACESAlgebra.mult ====")
print(f"\nbob computes {m1} + {m2} (mod {ac.p}):")
add = alice.decrypt(alg.add(cip1, cip2))
print(f"{m1} + {m2} (mod {ac.p}) =", add)
assert add == (m1 + m2) % ac.p

print(f"\nbob computes {m1} * {m2} (mod {ac.p}):")
mult = alice.decrypt(alg.mult(cip1, cip2))
print(f"{m1} * {m2} (mod {ac.p}) =", mult)
assert mult == (m1 * m2) % ac.p

print("\n==== Test equation schema with Algebra() and ACESAlgebra() ====")
plain_input = [random.randrange(ac.p) for _ in range(8)]
print("plain_input =", plain_input)

equation_schema = "(0*1+2*3+4*5)*6+7"
print(f"\nCompile {equation_schema} with Algebra()...")
plain_comp = pyc.Algebra().compile(equation_schema)
print(f"Compute {equation_schema} on plaintexts ...")
plain_output = plain_comp(plain_input)
print("plain_output =", plain_output % ac.p)

print(f"\nCompile {equation_schema} with ACESAlgebra()...")
cipher_comp = alg.compile(equation_schema)
print("Encrypt inputs ...")
cipher_input = [bob.encrypt(m) for m in plain_input]
print(f"Compute {equation_schema} on ciphertexts ...")
cipher_output = cipher_comp(cipher_input)
print("\ncipher_output.enc \t=", cipher_output.enc)

decrypted_output = alice.decrypt(cipher_output)
print("decrypt(cipher_output) \t=", decrypted_output)
assert decrypted_output == plain_output % ac.p

print("cipher_output.lvl \t=", cipher_output.lvl)

print("\n==== Test manual refresh operation ====")

classifier = pyc.ACESRefreshClassifier(ac, debug=debug)
is_refreshable = classifier.is_refreshable(ciphertext=cipher_output)
is_locator, margin = classifier.is_locator(dec=cipher_output.dec)
print("Is cipher_output refreshable and is it associated with a locator?")
print(f"- is cipher_output refreshable ? ..... {is_refreshable}")
print(f"- has cipher_output a locator ? ...... {is_locator}")

max_co_margin = ((cipher_output.lvl + 1)* ac.p - 1) / ac.q
margin_satisfied = max_co_margin % ac.p < 1 - margin
print(f"- is margin condition satisfied ? .... {margin_satisfied}")
test_implication = not(margin_satisfied and is_locator) or is_refreshable
assert test_implication

print("\nCreate refresher ...")
refresher = alice.generate_refresher(max_noise=150)

print("Create corefresher ...")
corefresher = cipher_output.corefresher(bob)

print("Refresh ciphertext ...")
refreshed_cipher_output = alg.refresh(refresher=refresher, corefresher=corefresher)

print("\nrefreshed_cipher_output.lvl =", refreshed_cipher_output.lvl)
decrypted_refreshed_cipher_output = alice.decrypt(refreshed_cipher_output)
print("decrypt(refreshed_cipher_output) =", decrypted_refreshed_cipher_output, f"   (Compare to plaintext output: {plain_output % ac.p})")
assert not(is_refreshable) or decrypted_refreshed_cipher_output == plain_output % ac.p


