from pyaces import *

ac = ArithChannel(32,10*32**5+1,10,5)
(f0,f1,vanmod,intmod,dim,N,u,tensor) = ac.publish(fhe = True)

bob = ACES(f0,f1,vanmod,intmod,dim,N,u)
alice = ACESReader(ac)

alg = ACESAlgebra(vanmod,intmod,dim,u,tensor)
q_p = intmod/vanmod

import random as rd
array = [rd.randint(0,5) for _ in range(8)]
enc_array = [bob.encrypt(a) for a in array]
send_array, keep_array = map(list,zip(*enc_array))
print(array)
print(send_array)
print(keep_array)

rfr = ACESRefresher(ac)

true_fun = Algebra().compile("(0*1+2*3+4*5)*6+7")
send_fun = alg.compile("(0*1+2*3+4*5)*6+7")
keep_fun = rfr.compile("(0*1+2*3+4*5)*6+7")

truth = true_fun(array)
print(truth % 32)

secret = keep_fun(rfr.process(keep_array))
e1 = send_fun(send_array)
alice.decrypt(e1)

online = send_fun(send_array)
print(online.uplvl)
print(q_p - online.uplvl)
print(alice.decrypt(online))

true_fun1 = Algebra().compile("0*1+2*3+4*5")
send_fun1 = alg.compile("0*1+2*3+4*5")
keep_fun1 = rfr.compile("0*1+2*3+4*5")

truth1 = true_fun1(array)
print(truth1 % 32)
online1 = send_fun1(send_array)
print(online1.uplvl)
print(q_p - online1.uplvl)
print(alice.decrypt(online1))


k1 = keep_fun1(rfr.process(keep_array))
c1 = alg.refresh(online1,k1)
print(c1.uplvl)
print(alice.decrypt(c1))

true_fun2 = Algebra().compile("8*6+7")
send_fun2 = alg.compile("8*6+7")
keep_fun2 = rfr.compile("8*6+7")

truth2 = true_fun2(array+[truth1])
print(truth2 % 32)
online2 = send_fun2(send_array + [c1])
print(online2.uplvl)
print(q_p - online2.uplvl)
print(alice.decrypt(online2))