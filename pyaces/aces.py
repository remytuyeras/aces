import random

def degree(p):
  for i,c in enumerate(p.coefs[::-1]):
    if c != 0:
      return len(p.coefs)-i-1
  return 0

class Polynomial(object):
  
  def __init__(self,coefs,intmod=None):
    self.coefs = coefs
    self.intmod = intmod

  def __repr__(self):
    return "+".join([f"[{c}]^{k}" for k,c in enumerate(self.coefs) if k <= degree(self) and c != 0][::-1])+f" ({self.intmod})"

  def mod(self,intmod=None):
    if intmod == None:
      return Polynomial(self.coefs,None)
    else:
      return Polynomial([(x % intmod) for x in self.coefs],intmod)

  def __mul__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x * y) % mod if mod != None else x*y
    d_self = degree(self)
    d_other = degree(other)
    coefs = [sum([(mod_coef(c,other.coefs[n-k]) if 0 <= n-k < len(other.coefs) else 0) for k,c in enumerate(self.coefs)]) for n in range(d_self+d_other+1)]
    return Polynomial(coefs,mod)

  def __add__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x + y) % mod if mod != None else x + y
    d_self = degree(self)
    d_other = degree(other)
    coefs = [ mod_coef(self.coefs[k] if 0<=k<len(self.coefs) else 0, other.coefs[k] if 0 <=k<len(other.coefs) else 0) for k in range(max(d_self,d_other)+1)]
    return Polynomial(coefs,mod)
  
  def __lshift__(self,other):
    d_other = degree(other)
    if other.coefs[d_other] != 1:
      print("Warning for Polynomial.__lshift__: polynomial modulus is not monic (no action taken)")
      return self, False

    d_self = degree(self)
    if d_self < d_other:
      return self, False

    deg_diff = d_self-d_other
    a_d = self.coefs[d_self]
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x - a_d * y) % mod if mod != None else x - a_d * y
    coefs = [(mod_coef(c,other.coefs[k-deg_diff]) if  0 <= k-deg_diff < len(other.coefs) else c) for k,c in enumerate(self.coefs)]
    return Polynomial(coefs,mod), True

  def __mod__(self,other):
    p, t = self << other
    while t:
      p, t = p << other
    return p

  @staticmethod
  def random(intmod,dim,anchor = lambda v,w : random.randrange(w)):
    return Polynomial([anchor(i,intmod) for i in range(dim)],intmod)

  @staticmethod
  def randshift(coef,intmod,dim):
    degree_shift = [0]*(random.randrange(dim))
    return Polynomial(degree_shift + [coef % intmod],intmod)

  def __call__(self,arg=1):
    output = 0
    for i, c in enumerate(self.coefs):
      output = (output*arg+c) % self.intmod if self.intmod != None else output*arg+c
      if i == degree(self):
        return output
    return None

import math
from functools import reduce

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

def randinverse(intmod):
  a = random.randrange(1,intmod)
  while math.gcd(a,intmod) != 1:
    a = random.randrange(1,intmod)
  _, inva, k = extended_gcd(a,intmod)
  return (a,inva % intmod)


import numpy as np

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

  def generate(self,length,pswap=1,pmult=2,pline=3):
    u = np.eye(self.dim, dtype=int)
    invu = np.eye(self.dim, dtype=int)
    choices = ["swap"] * pswap + ["mult"] * pmult + ["line"] * pline
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
    return (u % self.intmod), (invu % self.intmod)

class ArithChannel(object):

  #dim is both n = dim(x) and degre(u)
  def __init__(self,
                vanmod,
                intmod,
                dim,
                N,
                anchor = lambda v : 0 if random.uniform(0,1) < 0.5 else 1):
    # Implicit values for omega:
    self.omega = 1
    # Generate values for N, p, q, n, u, x, f0
    self.N = N
    if vanmod**2 < intmod and math.gcd(intmod,vanmod) == 1:
      self.vanmod = vanmod
      self.intmod = intmod
    else:
       self.vanmod = vanmod
       self.intmod = vanmod**2+1
    self.dim = dim
    self.u = self.generate_u()
    self.x, self.tensor = self.generate_secret(self.u)
    self.f0 = self.generate_initializer()
    self.f1, self.lvl_e = self.generate_noisy_key(anchor=anchor)

  def generate_vanisher(self,anchor = lambda v : 0 if random.uniform(0,1) < 0.5 else 1):
    e = []
    lvl_e = []
    for i in range(self.N):
      k = anchor(i)
      lvl_e.append(k)
      randpoly = Polynomial.random(self.intmod,self.dim)
      shift = Polynomial.randshift(self.vanmod * k - randpoly(arg=1),self.intmod,self.dim)
      e.append(shift + randpoly)
    return e, lvl_e

  def generate_initializer(self):
    f0 = []
    # divisor of self.intmod
    for _ in range(self.N):
      row = []
      for _ in range(self.dim):
        k = random.randrange(self.intmod)
        randpoly = Polynomial.random(self.intmod,self.dim)
        shift = Polynomial.randshift(self.vanmod * k - randpoly(arg=1),self.intmod,self.dim)
        row.append(shift + randpoly)
      f0.append(row)
    return f0

  def generate_noisy_key(self,anchor = lambda v : 0 if random.uniform(0,1) < 0.5 else 1):
    f1 = [Polynomial([0],self.intmod) for _ in range(self.N)]
    e, lvl_e = self.generate_vanisher(anchor = anchor)
    for i in range(self.N):
      for j in range(self.dim):
        f1[i] = (f1[i] + self.f0[i][j] * self.x[j]) % self.u
      f1[i] = f1[i] + e[i]
    return f1, lvl_e
    
  def publish(self,fhe = False):
    if fhe:
      return (self.f0,self.f1,self.vanmod,self.intmod,self.dim,self.N,self.u,self.tensor)
    else:
      return (self.f0,f1,self.vanmod,self.intmod,self.dim,self.N,self.u)

  def generate_u(self):
    #number of non zero coefficients for u where deg(u) = self.dim
    nonzeros = max(self.dim/2,min(self.dim-1,int(random.gauss(3*self.dim/4,self.dim/4))))
    
    #The dominant coefficient for u is equal to 1
    u_coefs = [1]

    while nonzeros-len(u_coefs) > 1:
      # a, _ = randinverse(self.intmod)
      a = random.randrange(self.intmod)
      u_coefs.append(a)

    u_coefs.append(self.intmod - sum(u_coefs))
    #number of zero coefficients for u
    zeros = self.dim - len(u_coefs)

    decomp = []
    remaining = zeros-sum(decomp)
    while remaining > 0:
      samp = max(0,min(remaining,int(random.gauss(remaining/2,remaining/2))))
      decomp.append(random.randint(0,samp))
      remaining = zeros-sum(decomp)
    
    u = []
    for i in range(len(u_coefs)):
      u.append(u_coefs[i])
      if i < len(decomp):
        u.extend([0] * decomp[i])
    u.extend([0] * (self.dim - len(u)+1))
    
    return Polynomial(u[::-1],self.intmod)

  def generate_secret(self,poly_u):
    ri = RandIso(self.intmod,self.dim)
    m, invm = ri.generate(60)

    x = []
    m_t = np.transpose(m)
    for k in range(len(m)):
      x.append(Polynomial(list(m_t[k]),self.intmod))

    tensor = []
    # we will have a list/array: tensor[i][j][k]
    for i in range(len(x)):
      row = []
      for j in range(len(x)):
        xi_xj_mod_u = (x[i] * x[j]) % poly_u
        a_ij_poly = xi_xj_mod_u.mod(self.intmod)

        if sum(a_ij_poly.coefs[self.dim:]) != 0:
          print("Error in ArithChannel.generate_secret: tensor cannot be computed due to dimension discrepancies")
          print(a_ij_poly)
          exit()

        a_ij = np.array(a_ij_poly.coefs[:self.dim] + [0] * (self.dim - len(a_ij_poly.coefs)) )
        row.append((invm @ a_ij) % self.intmod)
      tensor.append(np.array(row))
    
    return x, np.array(tensor)


class ACESCipher(object):

  def __init__(self,dec,enc,lvl):
    self.dec = dec
    self.enc = enc
    self.uplvl = lvl


# Arithmetic Channel Ecnryption Scheme 
class ACES(object):

  def __init__(self,f0,f1,vanmod,intmod,dim,N,u):
    self.f0 = f0
    self.f1 = f1
    self.vanmod = vanmod
    self.intmod = intmod
    self.dim = dim
    self.N = N
    self.u = u

  def encrypt(self,m,anchor = lambda v,w: random.randint(0,w)):
    if m >= self.vanmod:
      print(f"Warning in ACES.encrypt: the input is equivalent to {m % self.vanmod}")
    b = self.generate_linear(anchor=anchor)
    enc = self.generate_error(m)
    for i in range(self.N):
      enc = enc + (b[i] * self.f1[i]) % self.u
    dec = []
    for j in range(self.dim):
      dec_j = Polynomial([0],self.intmod)
      for i in range(self.N):
        dec_j = dec_j + (b[i] * self.f0[i][j]) % self.u
      dec.append(dec_j)
    return ACESCipher(dec,enc,self.N * self.vanmod) , [b[i](arg=1) for i in range(self.N)]

  def generate_linear(self,anchor = lambda v,w: random.randint(0,w)):
    b = []
    for i in range(self.N):
      k = anchor(i,self.vanmod)
      randpoly = Polynomial.random(self.intmod,self.dim)
      shift = Polynomial.randshift(k - randpoly(arg=1),self.intmod,self.dim)
      b.append(shift + randpoly)
    return b

  def generate_error(self,m):
    randpoly = Polynomial.random(self.intmod,self.dim)
    shift = Polynomial.randshift(m - randpoly(arg=1),self.intmod,self.dim)
    return shift + randpoly


class ACESReader(object):

  def __init__(self,ac):
    self.x = ac.x
    self.vanmod = ac.vanmod
    self.intmod = ac.intmod
    self.dim = ac.dim
    self.N = ac.N
    self.u = ac.u

  def decrypt(self,c):
    cTx = Polynomial([0],self.intmod)
    for i in range(self.dim):
      cTx = cTx + c.dec[i] * self.x[i]
    
    m_pre = c.enc + Polynomial([-1],self.intmod) * cTx
    return ( m_pre(arg=1) % self.intmod ) % self.vanmod



from pyaces.compaces import read_operations

class ACESAlgebra(object):

  def __init__(self,vanmod,intmod,dim,u,tensor):
    self.vanmod = vanmod
    self.intmod = intmod
    self.dim = dim
    self.u = u
    self.tensor = tensor

  def add(self,a,b):
    c0 = [ (a.dec[k]+b.dec[k]) % self.u for k in range(self.dim) ]
    c1 = (a.enc+b.enc) % self.u
    return ACESCipher(c0, c1, a.uplvl + b.uplvl)
  
  def mult(self,a,b):
    t = []
    for k in range(self.dim):
      tmp = Polynomial([0],self.intmod)
      for i in range(self.dim):
        for j in range(self.dim):
          tmp = tmp + Polynomial([self.tensor[i][j][k]],self.intmod) * a.dec[i] * b.dec[j]
      t.append(tmp)

    c0 = [ ( b.enc * a.dec[k] +a.enc * b.dec[k] + Polynomial([-1],self.intmod) * t[k]) % self.u for k in range(self.dim) ]
    c1 = ( a.enc * b.enc ) % self.u
    return ACESCipher(c0, c1, a.uplvl*b.uplvl*self.vanmod)

  def refresh(self,c,k):
    return ACESCipher(c.dec, c.enc + Polynomial([- k * self.vanmod],self.intmod) , c.uplvl-k)

  def compile(self,instruction):
    return lambda a: read_operations(self,instruction,a)


class ACESRefresher(object):

  def __init__(self,ac):
    self.vanmod = ac.vanmod
    self.N = ac.N
    self.lvl_e = ac.lvl_e

  def process(self,refresher_list):
    return  [sum([a[i]* self.lvl_e[i] for i in range(self.N)]) for a in refresher_list]

  def add(self,a,b):
    return a+b

  def mult(self,a,b):
    return a*b*self.vanmod

  def compile(self,instruction):
    return lambda a: read_operations(self,instruction,a)

