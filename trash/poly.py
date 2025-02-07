import random


def reduction(a,b,mod = None):
  if a == 0 or b == 0:
    return False, 0
  reducer = lambda a,b : (a % b) == 0
  if mod is not None :
    a_ = a % mod
    truth.extend([reducer(a_ + k * mod,b) for k in range(mod)])
  else:
    truth = [reducer(a,b)]
  reducible = True in truth
  k = truth.index(True) if reducible else 0
  return reducible, (a_ + k * mod) // b if mod is not None else a // b


class Polynomial(object):
  
  def __init__(self,coefs,intmod=None):
    self.intmod = intmod
    self.coefs = [(c % self.intmod if self.intmod is not None else c) for c in coefs]

  def degree(self):
    for i,c in enumerate(self.coefs[::-1]):
      if c != 0:
        return len(self.coefs)-i-1
    return 0

  def lead_coef(self):
    for i,c in enumerate(self.coefs[::-1]):
      if c != 0:
        return c
    return 0

  def is_null(self):
    return self.lead_coef() == 0

  def __eq__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: ((x-y) % mod) == 0 if mod is not None else x == y
    d_self = self.degree()
    d_other = other.degree()
    truth = [mod_coef(self.coefs[k] if 0<=k<len(self.coefs) else 0, other.coefs[k] if 0 <=k<len(other.coefs) else 0) for k in range(max(d_self,d_other)+1)]
    return all(truth)

  def __neq__(self,other):
    return not( self == other)

  def __repr__(self):
    s = "+".join([f"[{c}]^{k}" for k,c in enumerate(self.coefs) if k <= self.degree() and c != 0][::-1])
    return (s if s != "" else "Null")+f" ({self.intmod})"

  def mod(self,intmod=None):
    if intmod is None:
      return Polynomial(self.coefs,None)
    else:
      return Polynomial([(x % intmod) for x in self.coefs],intmod)

  def __mul__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x * y) % mod if mod is not None else x*y
    d_self = self.degree()
    d_other = other.degree()
    coefs = [sum([(mod_coef(c,other.coefs[n-k]) if 0 <= n-k < len(other.coefs) else 0) for k,c in enumerate(self.coefs)]) for n in range(d_self+d_other+1)]
    return Polynomial(coefs,mod)

  def __add__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x + y) % mod if mod is not None else x + y
    d_self = self.degree()
    d_other = other.degree()
    coefs = [mod_coef(self.coefs[k] if 0<=k<len(self.coefs) else 0, other.coefs[k] if 0 <=k<len(other.coefs) else 0) for k in range(max(d_self,d_other)+1)]
    return Polynomial(coefs,mod)

  def __sub__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x - y) % mod if mod is not None else x - y
    d_self = self.degree()
    d_other = other.degree()
    coefs = [mod_coef(self.coefs[k] if 0<=k<len(self.coefs) else 0, other.coefs[k] if 0 <=k<len(other.coefs) else 0) for k in range(max(d_self,d_other)+1)]
    return Polynomial(coefs,mod)

  def __lshift__(self,other):
    mod = None if self.intmod != other.intmod else self.intmod

    self_lead = self.lead_coef()
    other_lead = other.lead_coef()

    reducible, q = reduction(self.lead_coef(),other.lead_coef(),mod)

    if not reducible:
      return self, Polynomial([0],mod), False

    d_self = self.degree()
    d_other = other.degree()

    if d_self < d_other:
      return self, Polynomial([0],mod), False

    deg_diff = d_self-d_other
    mod = None if self.intmod != other.intmod else self.intmod
    mod_coef = lambda x,y: (x - q * y) % mod if mod is not None else x - q * y
    coefs = [(mod_coef(c,other.coefs[k-deg_diff]) if  0 <= k-deg_diff < len(other.coefs) else c) for k,c in enumerate(self.coefs)]
    return Polynomial(coefs,mod), Polynomial([0] * deg_diff + [q],mod), True

  def __mod__(self,other):
    r, _, t = self << other
    while t:
      r, _, t = r << other
    return r

  def divmod(self,other):
    remainder, q, t = self << other
    quotient = q
    while t:
      remainder, q, t = remainder << other
      quotient = quotient + q
    return quotient, remainder

  def extended_gcd(self, other):
    mod = None if self.intmod != other.intmod else self.intmod
    poly_0 = Polynomial([0],mod)
    poly_1 = Polynomial([1],mod)
    r = [self,other]
    s = [poly_1,poly_0]
    t = [poly_0,poly_1]
    reducible = True
    while reducible:
      r1 = r[-1]
      r0 = r[-2]
      q, r2 = r0.divmod(r1)
      if r2 != r0:
        r.append(r2)
        reducible = not(r2.is_null())
        s.append(s[-2] - q*s[-1])
        t.append(t[-2] - q*t[-1])
      else:
        lead_r1 = Polynomial([r1.lead_coef()],mod)
        r0 =  lead_r1 * r[-2]
        q, r2 = r0.divmod(r1)
        reducible = r2 != r0 and not(r2.is_null())
        r.append(r2)
        s.append(lead_r1 * s[-2] - q*s[-1])
        t.append(lead_r1 * t[-2] - q*t[-1])

    return (r[-2],s[-2],t[-2])

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
      output = (output*arg+c) % self.intmod if self.intmod is not None else output*arg+c
      if i == self.degree():
        return output
    return None

