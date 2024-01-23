from aces import *
import matplotlib.pyplot as plt

'''
We can attempt to attack the ACES cryptosystem by studying the distribution
of a collection of encryptions for a unique data point. To create these distributions, we
can evaluate every encryption at the integer $omega = 1$ (see the research paper). The code 
presented below can be used to find ACES setups that give a random distributions for these encryptions.
'''
# Setup the cryptosystem parameters
ac = ArithChannel(27,10)
(f0,f1,intmod,dim,u,tensor) = ac.publish(fhe = True)
# Simulate two communicating parties
bob = ACES(f0,f1,intmod,dim,u)
alice = ACESReader(ac.x,intmod,dim,u)

# Compute the polynomial evaluations Enc(m)(omega) where omega=1
dist = []
m = 3
for i in range(2000):
  c = bob.encrypt(m)
  attack = sum(c[1].coefs) % intmod
  d = alice.decrypt(c)
  print(f"Enc({m})(omega) =",c[1],"attack:",attack,"[Sanity check] decrypted as",d)
  dist.append(attack)

plt.hist(dist, density=False, bins=range(intmod+1))
plt.ylabel('Probability')
plt.xlabel('Value obtained from simple attack')
plt.show()
