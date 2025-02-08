import sys

sys.path.insert(1, "./")
import pyaces as pyc
import random

s = """\033[94m>>>\033[0m \033[92m# === SETTING UP PyACES === \033[0m
\033[94m>>>\033[0m import pyaces as pyc
\033[94m>>>\033[0m repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)
"""
print(s, end="")
repartition = pyc.Repartition(n=5, p=2, upperbound=47601551)

s = """\033[94m>>>\033[0m repartition.construct()
"""
print(s, end="")
repartition.construct()

s = f"""\033[94m>>>\033[0m repartition.q
{repr(repartition.q)}
\033[94m>>>\033[0m repartition.n0
{repr(repartition.n0)}
\033[94m>>>\033[0m repartition.factors
{repr(repartition.factors)}
\033[94m>>>\033[0m repartition.sigma_img
{repr(repartition.sigma_img)}
\033[94m>>>\033[0m [repartition.factors[sigma_i] for sigma_i in repartition.sigma_img]
{repr([repartition.factors[sigma_i] for sigma_i in repartition.sigma_img])}
\033[94m>>>\033[0m  repartition.x_images
{repr(repartition.x_images)}
"""
print(s, end="")


s = """\033[94m>>>\033[0m ac = pyc.ArithChannel(p=32, N=10, deg_u=3, repartition=repartition)
\033[94m>>>\033[0m import numpy as np
"""
print(s, end="")
ac = pyc.ArithChannel(p=32, N=10, deg_u=3, repartition=repartition)
import numpy as np

x = np.array(ac.x)
f0 = np.array(ac.f0)
f0_x = f0 @ x
lambdas = np.array(repartition.lambdas)
ell = np.array(repartition.ell)
s = f"""\033[94m>>>\033[0m x = np.array(ac.x); x \033[92m# tuple of polynomials\033[0m
{repr(x)}
\033[94m>>>\033[0m f0 = np.array(ac.f0); f0 \033[92m# matrix of polynomials\033[0m
{repr(f0)}
\033[94m>>>\033[0m f0 @ x
{repr(f0_x)}
\033[94m>>>\033[0m np.array(repartition.lambdas)
{repr(lambdas)}
\033[94m>>>\033[0m np.array(repartition.ell)
{repr(ell)}
"""
print(s, end="")

public = ac.publish()
s = f"""\033[94m>>>\033[0m public = ac.publish()
\033[94m>>>\033[0m public.keys()
{repr(public.keys())}
\033[94m>>>\033[0m public["levels"] \033[92m# max levels for each noisy component\033[0m
{public["levels"]}
\033[94m>>>\033[0m public["max_saturation"] \033[92m# max. percentage of bandwidth occupied by noisy components\033[0m
{public["max_saturation"]}
\033[94m>>>\033[0m public["max_saturation"] == round(100 * max(public["levels"]) / ((ac.q-(ac.p-1)) // ac.p), 4)
{public["max_saturation"] == round(100 * max(public["levels"]) / ((ac.q - (ac.p - 1)) // ac.p), 4)}
\033[94m>>>\033[0m ac = pyc.ArithChannel(p=32, N=10, deg_u=3, repartition=repartition,
\033[94m...\033[0m anchor=lambda _: list(range(6)),
\033[94m...\033[0m )
\033[94m>>>\033[0m public = ac.publish()
"""
print(s, end="")
ac = pyc.ArithChannel(
    p=32, N=10, deg_u=3, repartition=repartition, anchor=lambda _: list(range(6))
)
public = ac.publish()

s = f"""\033[94m>>>\033[0m public["levels"]
{public["levels"]}
\033[94m>>>\033[0m public["max_saturation"]
{public["max_saturation"]}
"""
print(s, end="")

s = """\033[94m>>>\033[0m \033[92m# === ENCRYPTION & DECRYPTION === \033[0m
\033[94m>>>\033[0m alice = pyc.ACESReader(ac, debug=True)
\033[94m>>>\033[0m bob = pyc.ACES(**public, debug=True)
"""
print(s, end="")
alice = pyc.ACESReader(ac, debug=True)
bob = pyc.ACES(**public, debug=True)

s = """\033[94m>>>\033[0m cip3 = bob.encrypt(3)
"""
print(s, end="")
cip3 = bob.encrypt(3)

s = f"""\033[94m>>>\033[0m cip3.enc
{repr(cip3.enc)}
\033[94m>>>\033[0m np.array(cip3.dec)
{repr(np.array(cip3.dec))}
\033[94m>>>\033[0m cip3.lvl
{repr(cip3.lvl)}
\033[94m>>>\033[0m alice.decrypt(cip3)
{repr(alice.decrypt(cip3))}
"""
print(s, end="")


s = """\033[94m>>>\033[0m import random
\033[94m>>>\033[0m cip3 = bob.encrypt(3, anchor = lambda _, w: random.randint(0, 2*w))
"""
print(s, end="")
cip3 = bob.encrypt(3, anchor=lambda _, w: random.randint(0, 2 * w))

s = f"""\033[94m>>>\033[0m cip3.lvl
{repr(cip3.lvl)}
\033[94m>>>\033[0m alice.decrypt(cip3)
{repr(alice.decrypt(cip3))}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip5 = bob.encrypt(37)
"""
print(s, end="")
cip5 = bob.encrypt(37)

s = f"""\033[94m>>>\033[0m cip5.enc
{repr(cip5.enc)}
\033[94m>>>\033[0m np.array(cip5.dec)
{repr(np.array(cip5.dec))}
\033[94m>>>\033[0m cip5.lvl
{repr(cip5.lvl)}
\033[94m>>>\033[0m alice.decrypt(cip5)
{repr(alice.decrypt(cip5))}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip3 = alice.encrypt(3, max_noise=10)
"""
print(s, end="")
cip3 = alice.encrypt(3, max_noise=10)

s = f"""\033[94m>>>\033[0m cip3.enc
{repr(cip3.enc)}
\033[94m>>>\033[0m np.array(cip3.dec)
{repr(np.array(cip3.dec))}
\033[94m>>>\033[0m cip3.lvl
{repr(cip3.lvl)}
\033[94m>>>\033[0m alice.decrypt(cip3)
{repr(alice.decrypt(cip3))}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip5 = alice.encrypt(37, max_noise=10)
"""
print(s, end="")
cip5 = alice.encrypt(37, max_noise=10)

s = f"""\033[94m>>>\033[0m cip5.enc
{repr(cip5.enc)}
\033[94m>>>\033[0m np.array(cip5.dec)
{repr(np.array(cip5.dec))}
\033[94m>>>\033[0m cip5.lvl
{repr(cip5.lvl)}
\033[94m>>>\033[0m alice.decrypt(cip5)
{repr(alice.decrypt(cip5))}
"""
print(s, end="")

m1 = random.randrange(ac.p)
m2 = random.randrange(ac.p)
s = f"""\033[94m>>>\033[0m m1 = random.randrange(ac.p); m1
{repr(m1)}
\033[94m>>>\033[0m m2 = random.randrange(ac.p); m2
{repr(m2)}
"""
print(s, end="")


s = """\033[94m>>>\033[0m cip1 = bob.encrypt(m1); cip1.enc
"""
print(s, end="")
cip1 = bob.encrypt(m1)

s = f"""\033[94m>>>\033[0m 
{repr(cip1.enc)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip2 = bob.encrypt(m2); cip2.enc
"""
print(s, end="")
cip2 = bob.encrypt(m2)

s = f"""\033[94m>>>\033[0m 
{repr(cip2.enc)}
"""
print(s, end="")


alg = pyc.ACESAlgebra(**public, debug=True)
s = """\033[94m>>>\033[0m alg = pyc.ACESAlgebra(**public, debug=True)
\033[94m>>>\033[0m add = alice.decrypt(alg.add(cip1, cip2))
"""
print(s, end="")

add = alice.decrypt(alg.add(cip1, cip2))
s = f"""\033[94m>>>\033[0m add
{repr(add)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m mult = alice.decrypt(alg.mult(cip1, cip2))
"""
print(s, end="")

error = None
try:
    mult = alice.decrypt(alg.mult(cip1, cip2))
except Exception as e:
    error = e
s = f"""\033[90mTraceback (most recent call last):
  File "(path)/aces/tests/guide.py", line 232, in <module>
    mult = alice.decrypt(alg.mult(cip1, cip2))
  File "(path)/aces/./pyaces/algebras.py", line 244, in mult
    raise Exception("{error}")\033[0m
Exception: {error}
"""
print(s, end="")


s = """\033[94m>>>\033[0m \033[94m>>>\033[0m repartition = pyc.Repartition(n=5, p=2, upperbound=476015501)
"""
print(s, end="")
repartition = pyc.Repartition(n=5, p=2, upperbound=476015501)

s = """\033[94m>>>\033[0m repartition.construct()
"""
print(s, end="")
repartition.construct()

s = """\033[94m>>>\033[0m ac = pyc.ArithChannel(p=32, N=10, deg_u=3, repartition=repartition)
\033[94m>>>\033[0m public = ac.publish()
"""
print(s, end="")
ac = pyc.ArithChannel(p=32, N=10, deg_u=3, repartition=repartition)
public = ac.publish()

s = """\033[94m>>>\033[0m alice = pyc.ACESReader(ac, debug=False)
\033[94m>>>\033[0m bob = pyc.ACES(**public, debug=False)
"""
print(s, end="")
alice = pyc.ACESReader(ac, debug=False)
bob = pyc.ACES(**public, debug=False)

m1 = random.randrange(ac.p)
m2 = random.randrange(ac.p)
s = f"""\033[94m>>>\033[0m m1 = random.randrange(ac.p); m1
{repr(m1)}
\033[94m>>>\033[0m m2 = random.randrange(ac.p); m2
{repr(m2)}
"""
print(s, end="")
s = """\033[94m>>>\033[0m cip1 = bob.encrypt(m1); cip1.enc
"""
print(s, end="")

cip1 = bob.encrypt(m1)
s = f"""{repr(cip1.enc)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip2 = bob.encrypt(m2); cip2.enc
"""
print(s, end="")

cip2 = bob.encrypt(m2)
s = f"""{repr(cip2.enc)}
"""
print(s, end="")


alg = pyc.ACESAlgebra(**public, debug=False)
s = """\033[94m>>>\033[0m alg = pyc.ACESAlgebra(**public, debug=False)
\033[94m>>>\033[0m add = alice.decrypt(alg.add(cip1, cip2))
"""
print(s, end="")

add = alice.decrypt(alg.add(cip1, cip2))
s = f"""\033[94m>>>\033[0m add
{repr(add)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m mult = alice.decrypt(alg.mult(cip1, cip2))
"""
print(s, end="")

mult = alice.decrypt(alg.mult(cip1, cip2))
s = f"""\033[94m>>>\033[0m mult
{repr(mult)}
"""
print(s, end="")


plain_input = [random.randrange(ac.p) for _ in range(8)]
s = f"""\033[94m>>>\033[0m plain_input = [random.randrange(ac.p) for _ in range(8)]
\033[94m>>>\033[0m plain_input
{repr(plain_input)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cipher_input = [bob.encrypt(m) for m in plain_input]
"""
print(s, end="")
cipher_input = [bob.encrypt(m) for m in plain_input]


equation_schema = "0*1+2*5+3*4+6*7+1*5"
plain_comp = pyc.Algebra().compile(equation_schema)
plain_output = plain_comp(plain_input)
s = f"""\033[94m>>>\033[0m equation_schema = "0*1+2*5+3*4+6*7+1*5"
\033[94m>>>\033[0m plain_comp = pyc.Algebra().compile(equation_schema)
\033[94m>>>\033[0m plain_output = plain_comp(plain_input)
\033[94m>>>\033[0m plain_output % ac.p
{repr(plain_output % ac.p)}
"""
print(s, end="")

cipher_comp = alg.compile(equation_schema)
s = """\033[94m>>>\033[0m cipher_comp = alg.compile(equation_schema)
\033[94m>>>\033[0m cipher_output = cipher_comp(cipher_input)
"""
print(s, end="")
error = None
try:
    cipher_output = cipher_comp(cipher_input)
except Exception as e:
    error = e

s = f"""\033[90mTraceback (most recent call last):
  File "(path)/aces/tests/guide.py", line 343, in <module>
    cipher_output = cipher_comp(cipher_input)
  File "(path)/aces/./pyaces/algebras.py", line 270, in <lambda>
    return lambda a: read_operations(self, instruction, a)
  File "(path)/aces/./pyaces/compaces.py", line 154, in read_operations
    return alg.add(
  File "(path)/aces/./pyaces/algebras.py", line 131, in add
    raise Exception("{error}")\033[0m
Exception: {error}
"""
print(s, end="")


s = """\033[94m>>>\033[0m refresher = alice.generate_refresher(max_noise=10)
"""
print(s, end="")
refresher = alice.generate_refresher(max_noise=10)


classifier = pyc.ACESRefreshClassifier(ac, debug=False)
alg = pyc.ACESAlgebra(
    **public,
    debug=False,
    refresh_classifier=classifier.refresh_classifier,
    encrypter=bob,
    refresher=refresher,
)
s = """\033[94m>>>\033[0m classifier = pyc.ACESRefreshClassifier(ac, debug=False)
\033[94m>>>\033[0m alg = pyc.ACESAlgebra(**public, debug=False,
\033[94m...\033[0m refresh_classifier=classifier.refresh_classifier,
\033[94m...\033[0m encrypter=bob, 
\033[94m...\033[0m refresher=refresher)
"""
print(s, end="")


cipher_comp = alg.compile(equation_schema)
s = """\033[94m>>>\033[0m cipher_comp = alg.compile(equation_schema)
\033[94m>>>\033[0m cipher_output = cipher_comp(cipher_input)
"""
print(s, end="")
cipher_output = cipher_comp(cipher_input)


s = f"""\033[94m>>>\033[0m alice.decrypt(cipher_output)
{repr(alice.decrypt(cipher_output))}
"""
print(s, end="")


s = """\033[94m>>>\033[0m \033[92m# === PROPERTIES === \033[0m
\033[94m>>>\033[0m repartition = pyc.Repartition(n=5, p=2, upperbound=476015501)
"""
print(s, end="")
repartition = pyc.Repartition(n=5, p=2, upperbound=476015501)

s = """\033[94m>>>\033[0m repartition.construct()
"""
print(s, end="")
repartition.construct()

s = """\033[94m>>>\033[0m ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
\033[94m>>>\033[0m public = ac.publish()
"""
print(s, end="")
ac = pyc.ArithChannel(p=4, N=10, deg_u=3, repartition=repartition)
public = ac.publish()

s = """\033[94m>>>\033[0m alice = pyc.ACESReader(ac, debug=False)
\033[94m>>>\033[0m bob = pyc.ACES(**public, debug=False)
"""
print(s, end="")
alice = pyc.ACESReader(ac, debug=False)
bob = pyc.ACES(**public, debug=False)

m1 = random.randrange(ac.p)
m2 = random.randrange(ac.p)
m3 = random.randrange(ac.p)
s = f"""\033[94m>>>\033[0m m1 = random.randrange(ac.p); m1
{repr(m1)}
\033[94m>>>\033[0m m2 = random.randrange(ac.p); m2
{repr(m2)}
\033[94m>>>\033[0m m3 = random.randrange(ac.p); m3
{repr(m3)}
"""
print(s, end="")
s = """\033[94m>>>\033[0m cip1 = bob.encrypt(m1); cip1.enc
"""
print(s, end="")

cip1 = bob.encrypt(m1)
s = f"""{repr(cip1.enc)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip2 = bob.encrypt(m2); cip2.enc
"""
print(s, end="")

cip2 = bob.encrypt(m2)
s = f"""{repr(cip2.enc)}
"""
print(s, end="")

s = """\033[94m>>>\033[0m cip3 = bob.encrypt(m3); cip3.enc
"""
print(s, end="")

cip3 = bob.encrypt(m3)
s = f"""{repr(cip3.enc)}
"""
print(s, end="")

alg = pyc.ACESAlgebra(**public, debug=False)
s = """\033[94m>>>\033[0m alg = pyc.ACESAlgebra(**public, debug=False)
\033[94m>>>\033[0m add = alice.decrypt(alg.add(cip1, cip2))
"""
print(s, end="")


a = alg.add(cip1, cip2)
b = alg.add(cip2, cip1)
diff_enc = a.enc - b.enc
diff_dec = [a.dec[i] - b.dec[i] for i in range(ac.n)]
s = f"""\033[94m>>>\033[0m a = alg.add(cip1, cip2)
\033[94m>>>\033[0m b = alg.add(cip2, cip1)
\033[94m>>>\033[0m a.enc - b.enc
{repr(diff_enc)}
\033[94m>>>\033[0m [a.dec[i]-b.dec[i] for i in range(ac.n)]
{repr(diff_dec)}
"""
print(s, end="")

a = alg.mult(cip1, cip2)
b = alg.mult(cip2, cip1)
diff_enc = a.enc - b.enc
diff_dec = [a.dec[i] - b.dec[i] for i in range(ac.n)]
s = f"""\033[94m>>>\033[0m a = alg.mult(cip1, cip2)
\033[94m>>>\033[0m b = alg.mult(cip2, cip1)
\033[94m>>>\033[0m a.enc - b.enc
{repr(diff_enc)}
\033[94m>>>\033[0m [a.dec[i]-b.dec[i] for i in range(ac.n)]
{repr(diff_dec)}
"""
print(s, end="")

a = alg.add(alg.add(cip1, cip2), cip3)
b = alg.add(cip1, alg.add(cip2, cip3))
diff_enc = a.enc - b.enc
diff_dec = [a.dec[i] - b.dec[i] for i in range(ac.n)]
s = f"""\033[94m>>>\033[0m a = alg.add(alg.add(cip1, cip2), cip3)
\033[94m>>>\033[0m b = alg.add(cip1, alg.add(cip2, cip3))
\033[94m>>>\033[0m a.enc - b.enc
{repr(diff_enc)}
\033[94m>>>\033[0m [a.dec[i]-b.dec[i] for i in range(ac.n)]
{repr(diff_dec)}
"""
print(s, end="")

a = alg.mult(alg.mult(cip1, cip2), cip3)
b = alg.mult(cip1, alg.mult(cip2, cip3))
diff_enc = a.enc - b.enc
diff_dec = [(a.dec[i] - b.dec[i]).is_null() for i in range(ac.n)]
diff_dec_at_1 = [(a.dec[i] - b.dec[i])(arg=1) for i in range(ac.n)]
s = f"""\033[94m>>>\033[0m a = alg.mult(alg.mult(cip1, cip2), cip3)
\033[94m>>>\033[0m b = alg.mult(cip1, alg.mult(cip2, cip3))
\033[94m>>>\033[0m a.enc - b.enc
{repr(diff_enc)}
\033[94m>>>\033[0m [(a.dec[i]-b.dec[i]).is_null() for i in range(ac.n)]
{repr(diff_dec)}
\033[94m>>>\033[0m [(a.dec[i]-b.dec[i])(arg=1) for i in range(ac.n)]
{repr(diff_dec_at_1)}
"""
print(s, end="")
