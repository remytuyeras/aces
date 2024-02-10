from pyaces import *

ac = ArithChannel(32,32**5+1,10,2)
(f0,f1,vanmod,intmod,dim,N,u,tensor) = ac.publish(fhe = True)

print(u)
print(sum(u.coefs)-intmod)

q_p = intmod/vanmod
print(q_p)

bob = ACES(f0,f1,vanmod,intmod,dim,N,u)
enc3, k3 = bob.encrypt(3)
print(k3)

for d in enc3.dec:
  print(d)

print(enc3.uplvl)
alice = ACESReader(ac)
print(alice.decrypt(enc3))

alg = ACESAlgebra(vanmod,intmod,dim,u,tensor)
enc5, k5 = bob.encrypt(5)

print(alice.decrypt(alg.add(enc3,enc5)))
print(alice.decrypt(alg.mult(enc3,enc5)))
