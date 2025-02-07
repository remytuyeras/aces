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

print("\nInitialize ACESAlgebra() with refresher...")
# max_noise influences how fast max noise level is reached
refresher = alice.generate_refresher(max_noise=80)
classifier = pyc.ACESRefreshClassifier(ac, debug=debug)
alg = pyc.ACESAlgebra(**public, debug=debug, refresh_classifier=classifier.refresh_classifier, encrypter=bob, refresher=refresher)

plain_input = [random.randrange(1,ac.p) for _ in range(8)]
print("\nplain_input =", plain_input)

equation_schema = "(((0*1+2*3+4*5)*6+7)*3)*2"
print(f"\nCompile {equation_schema} with Algebra() ...")
plain_comp = pyc.Algebra().compile(equation_schema)
print(f"Compute {equation_schema} on plaintexts ...")
plain_output = plain_comp(plain_input)
print("\nplain_output =", plain_output % ac.p)

print(f"\nCompile {equation_schema} with ACESAlgebra() ...")
cipher_comp = alg.compile(equation_schema)

print("Encrypt inputs ...")
cipher_input = [bob.encrypt(m) for m in plain_input]

print(f"Compute {equation_schema} on ciphertexts ...")
cipher_output = cipher_comp(cipher_input)
print("\ncipher_output.enc \t=", cipher_output.enc)

decrypted_output = alice.decrypt(cipher_output)
print("cipher_output.lvl \t=", cipher_output.lvl)
print("decrypt(cipher_output) \t=", decrypted_output, f"   (Compare to plaintext output: {plain_output % ac.p})")

assert decrypted_output == plain_output % ac.p
