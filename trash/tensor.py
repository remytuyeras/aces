import numpy as np
import random
import math
from .arith import Primes
from .poly import Polynomial

# =======================================

def extended_gcd(a, b):
  r = [a,b]
  s = [1,0]
  t = [0,1]
  while not(0 in r):
    r1 = r[-1]
    r0 = r[-2]
    q, r2 = divmod(r0,r1)
    r.append(r2)
    s.append(s[-2]-q*s[-1])
    t.append(t[-2]-q*t[-1]) 
  return (r[-2],s[-2],t[-2])

# =======================================

def randinverse(intmod):
  a = random.randrange(1,intmod)
  while math.gcd(a,intmod) != 1:
    a = random.randrange(1,intmod)
  _, inva, k = extended_gcd(a,intmod)
  return (a,inva % intmod)

# =======================================

class RandIso(object):

  def __init__(self,intmod,dim):
    self.intmod = intmod
    self.dim = dim

  def generate_pair(self):
    i = random.randrange(self.dim)
    j = random.choice([k for k in range(self.dim) if k!=i])
    return i,j

  def generate_swap(self):
    i,j = self.generate_pair()
    m = []
    for r in range(self.dim):
      if r == i:
        m.append([(1 if s==j else 0) for s in range(self.dim)])
      elif r == j:
        m.append([(1 if s==i else 0) for s in range(self.dim)])
      else:
        m.append([(1 if s==r else 0) for s in range(self.dim)])
    return np.array(m)
        
  def generate_mult(self):
    m = []
    invm = []
    for r in range(self.dim):
      a,inva = randinverse(self.intmod)
      m.append([(a if s==r else 0) for s in range(self.dim)])
      invm.append([(inva if s==r else 0) for s in range(self.dim)])
    return np.array(m), np.array(invm)

  def generate_line(self):
    i,j = self.generate_pair()
    m = []
    invm = []
    a = random.randrange(1,self.intmod)
    for r in range(self.dim):
      m.append([(1 if s==r else ( a if r==i and s==j else 0)) for s in range(self.dim)])
      invm.append([(1 if s==r else ( self.intmod-a if r==i and s==j else 0)) for s in range(self.dim)])
    return np.array(m), np.array(invm)

  def generate(self,length,pswap=1,pmult=2,pline=3,method=None):
    u = np.eye(self.dim, dtype=int)
    invu = np.eye(self.dim, dtype=int)
    choices = ["swap"] * pswap + ["mult"] * pmult + ["line"] * pline

    if method is not None:
      ref = method(self.intmod)
      record = []
      threshold = length
      length = int(length * math.exp(1)) # the 37% rule

    for i in range(length):
      x = random.choice(choices)
      if x == "swap":
        m = invm = self.generate_swap()
      if x == "mult":
        m , invm = self.generate_mult()
      if x == "line":
        m , invm = self.generate_line()
      u = (m @ u) % self.intmod
      invu = (invu @ invm) % self.intmod

      if method is not None:
        row_sum = u.sum(axis=0) % self.intmod
        flag = []
        for j, x in enumerate(map(method,row_sum)):
          flag.append(x not in [None, {}] and (True in [k in ref.keys() for k in x.keys()]))
        if i <= threshold:
          record.append(sum(flag))
        else:
          if sum(flag) >= max(record):
            # add success flag?
            print("method succeeded ->",sum(flag))
            break

    return (u % self.intmod), (invu % self.intmod) 
