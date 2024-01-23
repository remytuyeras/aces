from aces import *

# q = 27 and n = deg(u) = 10
print("\n\033[94mWe generate an arithmetic channel with $\omega=1$ (default) and $q=27$. The polynomial $u$ is of degree 10\033[0m")
ac = ArithChannel(27,10)

print("\n\033[94mBelow, we show the private key $x$. Its dimension $n$ is equal to the degree of the polynomial $u$:\033[0m")
for x_i in ac.x:
  print(x_i)

# The publication step for ACES is as follows:
(f0,f1,intmod,dim,u,tensor) = ac.publish(fhe = True)

print(f"\n\033[94mThe key publication algorithm returns q={intmod} and n={dim} and the following data:\033[0m")

print("\n\033[94m(\033[93m1\033[94m) the matrix $f_0$ from the paper:\033[0m")
for f0_i in f0:
  print(f0_i)

print("\n\033[94m(\033[93m2\033[94m) the vector $f'$, taking the form $f+e$ in the paper:\033[0m")
print(f1)

print("\n\033[94m(\033[93m3\033[94m) the polynomial $u$ generated for the airthmetic channel structure:\033[0m")
print(u)

print("\n\033[94mSince $\omega=1$, the value for $u(omega)$ is the sum of its coefficients:\033[0m")
print("\033[94mu(omega) =\033[0m", sum(u.coefs))

print("\n\033[94mAlice and Bob are initialized with ACES and ACESReader...\033[0m")
bob = ACES(f0,f1,intmod,dim,u)
alice = ACESReader(ac.x,intmod,dim,u)

print("\n\033[94m[\033[93mEncryption/Decryption\033[0m] Test for m1=3:\033[0m")
m_a = 3
c_a = bob.encrypt(m_a)
print("\033[94mEncryption:\033[0m",c_a[1])
print("\033[94mDecryption (sanity check):\033[0m",alice.decrypt(c_a))

print("\n\033[94m[\033[93mEncryption/Decryption\033[0m] Test for m2=5:\033[0m")
m_b = 10
c_b = bob.encrypt(m_b)
print("\033[94mEncryption:\033[0m",c_b[1])
print("\033[94mDecryption (sanity check):\033[0m",alice.decrypt(c_b))

print("\n\033[94m[\033[93mHomomorphism\033[0m] We perform + and * on cyphertexts using ACESAlgebra:\033[0m")
alg = ACESAlgebra(intmod,dim,u,tensor)
print(f"\033[94mAddition of Enc(m1) and Enc(m2) modulo {intmod}:\033[0m", alice.decrypt(alg.add(c_a,c_b)))
print(f"\033[94mMultiplication of Enc(m1) and Enc(m2) modulo {intmod}:\033[0m",alice.decrypt(alg.mult(c_a,c_b)))
