<p align="center">
  <img width="300px" src="img/twofish_rounded_border.png"/> <!--"border: 3px solid grey; border-radius: 135px;"-->
  <p align="center"><img src="img/logo_roboto_black.png" width="250px" /></p>   <!-- <h1 align="center">PyACES</h1> -->
  <p align="center">A Python library for the fully homomorphic encryption scheme ACES</p>
</p>

[![PyPI - Version](https://img.shields.io/pypi/v/pyaces)](https://pypi.org/project/pyaces/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaces)](https://pypi.org/project/pyaces/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/remytuyeras/aces)](https://github.com/remytuyeras/aces/tree/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/remytuyeras/aces)](https://github.com/remytuyeras/aces/tree/main)

<!-- [![CodeFactor](https://www.codefactor.io/repository/github/remytuyeras/aces/badge/main)](https://www.codefactor.io/repository/github/remytuyeras/aces/overview/main) -->
<!-- [![CodeFactor](https://www.codefactor.io/repository/github/remytuyeras/aces/badge/dev)](https://www.codefactor.io/repository/github/remytuyeras/aces/overview/dev) -->
[![CodeFactor Grade (with branch)](https://img.shields.io/codefactor/grade/github/remytuyeras/aces/main?label=code%20quality%20(main))](https://github.com/remytuyeras/aces/tree/main)
[![CodeFactor Grade (with branch)](https://img.shields.io/codefactor/grade/github/remytuyeras/aces/dev?label=code%20quality%20(dev))](https://github.com/remytuyeras/aces/tree/dev)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyaces)](https://pypi.org/project/pyaces/)
[![GitHub Repo stars](https://img.shields.io/github/stars/remytuyeras/aces)](https://github.com/remytuyeras/aces/tree/main)

[![GitHub Sponsors](https://img.shields.io/github/sponsors/remytuyeras)](https://github.com/remytuyeras)
[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/RTuyeras)](https://x.com/Rtuyeras)


# Overview

This package proposes an implementation for the ACES cryptosystem where we take parameters $\omega = 1$. Details are available in the preprint  [<em>"Constructing a Fully Homomorphic Encryption Scheme with the Yoneda Lemma"</em>](https://arxiv.org/abs/2401.13255).

The name "PyACES" is pronounced "pisces," echoing a symbol synonymous with [_malleability_](https://en.wikipedia.org/wiki/Malleability_(cryptography)). In the Pisces symbol, the two fishes represent a harmonious interplay between opposite directions, reflecting the dual nature of encryption and decryption.

# PyACES at a Glance

**PyACES** is:
  - most closely related to the **BGV** scheme.
  - currently being designed for use with **binary circuits**, similar to **TFHE**.
  - the only known FHE scheme ([ref: p. 4](https://ems.press/content/book-chapter-files/33149)) in which both `add` and `mult` are **commutative** and **associative**.
  - a **leveled FHE scheme** with a **refresh operation**, positioning it at the intersection of BGV and TFHE.

**PyACES** does not:
  - need to systematically refresh ciphertexts after each homomorphic operation.
  - require lookup tables for refreshing; instead, it tests whether ciphertexts can be decomposed into an affine-like structure.


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

# Progress and upcoming features

### :construction: To do before next release
- [ ] Uploading `version 0.1.0` to PyPI: ![50%](https://progress-bar.xyz/50)

- [x] Resolve Issue #1:
  - PyPI Publication: [![100%](https://progress-bar.xyz/100)](https://github.com/remytuyeras/aces/issues/1)
  - GitHub Actions for Automation: [![0%](https://progress-bar.xyz/0)](https://github.com/remytuyeras/aces/issues/1)
  - Project Structure and Dependency Management: [![100%](https://progress-bar.xyz/100)](https://github.com/remytuyeras/aces/issues/1)
  - Testing with Pytest: [![100%](https://progress-bar.xyz/100)](https://github.com/remytuyeras/aces/issues/1)
  - Code Quality with Ruff: [![100%](https://progress-bar.xyz/100)](https://github.com/remytuyeras/aces/issues/1)
  - Documentation Updates: [![100%](https://progress-bar.xyz/100)](https://github.com/remytuyeras/aces/issues/1)

- [ ] Add guide to [ePrint](https://eprint.iacr.org):
  - Tutorial: ![80%](https://progress-bar.xyz/80)
  - Performance analysis: ![10%](https://progress-bar.xyz/5)
  - Security analysis: ![30%](https://progress-bar.xyz/10)
  
- [ ] Complete documentation:
  - [ ] `algebras.py`
  - [ ] `test_algebras.py`
  - [ ] `test_refresh.py`
  - [ ] `test_classifier.py`

### :rocket: Major system enhancements _(subject to funding or sponsorship)_ 

- [ ] :file_folder: Create a function to generate cryptographic data with an efficient locator-director database (RAM).  

- [ ] :floppy_disk: Enable local storage of cryptographic data (ROM) and implement secure key management.  

- [ ] :lock: Implement file encryption (ROM).  

- [ ] :abacus: Support complex data types (`Int8`, `Int16`, `Int32`, `String`, `Bool`) and their arithmetic operations.  

- [ ] :zap: Optimize for CPU & GPU performance:  

  - [ ] :gear: Use `C`, `C++`, or `ctypes` for elementary operations on polynomials and ciphertexts.  
  
  - [ ] :video_game: Implement GPU acceleration with `CUDA`.


# Quickstart

The following script will encrypt two messages in $\mathbb{Z}_4$ and compute their sum and product modulo $4$.

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

After running the script, you should see the following display in your terminal.

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
