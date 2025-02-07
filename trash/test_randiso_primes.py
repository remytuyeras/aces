import sys 
sys.path.insert(1,"./")
import pyaces as pyc
import numpy as np

intmod = 37*3*17
ri = pyc.RandIso(intmod,5)
primes = pyc.Primes(intmod)
# If method is not None then 37% rule applies in the way primes.factorize is applied
u, invu = ri.generate(60,method = primes.factorize)

print(u)
print(invu)

print(u @ invu % intmod) 
assert (u @ invu % intmod == np.identity(5)).all()

print(invu @ u % intmod) 
assert (invu @ u % intmod == np.identity(5)).all()

import math
row_sum = u.sum(axis=0) % ri.intmod
# check for units 
check = [True if x == 1 else False for x in map(lambda a:math.gcd(a,intmod),row_sum)]
print(check)
assert False in check

