<p align="center">
  <img width="300px" src="img/twofish.png" style="border: 3 solid grey;"/>
  <h1 align="center">PyACES</a></h1>
  <p align="center">A python library for the fully homomorphic encryption scheme ACES</p>
</p>

# Presentation

This package proposes an implementation for the ACES cryptosystem where we take parameters $\omega = 1$. Details are available in the preprint  [<em>"Constructing a Fully Homomorphic Encryption Scheme with the Yoneda Lemma"</em>](https://arxiv.org/abs/2401.13255).

The name "PyACES" is pronounced "pisces," echoing a symbol synonymous with [_malleability_](https://en.wikipedia.org/wiki/Malleability_(cryptography)). In the Pisces symbol, the two fishes represent a harmonious interplay between opposite directions, reflecting the dual nature of encryption and decryption.

# Installation

Install the package using ```pip```:

```shell
pip install pyaces
```
Then use the following import in your Python code.

```python
import pyaces
```

To upgrade to the [latest version](https://pypi.org/project/pyaces/):
```shell
pip install --upgrade pyaces==version_number
```

# Facts about PyACES

- PyACES is the only known FHE cryptosystem whose additiona dn multiplication are commutative and weakly-associative

# Progress and upcoming features
- [ ] Uploading version 0.1.0 to PyPI:
  - ![50%](https://progress-bar.xyz/50)

- [ ] Resolve Issues:
  - https://github.com/remytuyeras/aces/issues/1 ![80%](https://progress-bar.xyz/80)

- [ ] Add guide to [https://eprint.iacr.org](https://eprint.iacr.org). Current progress:
  - ![80%](https://progress-bar.xyz/80?title=Tutorial)
  - ![5%](https://progress-bar.xyz/5?title=Performance)
  - ![10%](https://progress-bar.xyz/10?title=Security)
  
- [ ] Finish documentation:
  - [ ] `algebras.py`
  - [ ] `test_algebras.py`
  - [ ] `test_refresh.py`
  - [ ] `test_classifier.py`


# Quickstart

Run the following script:

```python
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
plain_add = alice.decrypt()
print(f"{m1} * {m2} (mod {ac.p}) =", plain_add)
```

You should see the following display in your terminal

```text
getting primes...
primes obtained

bob encrypts 3 (mod 4):
Warning in ACES.encrypt: encryption starting at 0.0003% of max. noise level.

bob encrypts 2 (mod 4):
Warning in ACES.encrypt: encryption starting at 0.0003% of max. noise level.

bob computes 3 + 2 (mod 4):
Warning in ACESAlgebra.add: saturation increasing from (0.0003%, 0.0003%) to 0.0007% of max. noise level.
3 + 2 (mod 4) = 1

bob computes 3 * 2 (mod 4):
Warning in ACESAlgebra.mult: saturation increasing from (0.0003%, 0.0003%) to 0.0565% of max. noise level.
3 * 2 (mod 4) = 2
```