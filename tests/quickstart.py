import sys

sys.path.insert(1, "./")
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

print(f"\nbob encrypts {m2} (mod {ac.p}):")
cip2 = bob.encrypt(m2)

alg = pyc.ACESAlgebra(**public, debug=debug)

print(f"\nbob computes {m1} + {m2} (mod {ac.p}):")
cip_add = alg.add(cip1, cip2)
plain_add = alice.decrypt(cip_add)
print(f"{m1} + {m2} (mod {ac.p}) =", plain_add)

print(f"\nbob computes {m1} * {m2} (mod {ac.p}):")
cip_mult = alg.mult(cip1, cip2)
plain_add = alice.decrypt(cip_mult)
print(f"{m1} * {m2} (mod {ac.p}) =", plain_add)
