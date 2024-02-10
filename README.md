<p align="center">
  <img width="300px" src="img/twofish.png" style="border: 3 solid grey;"/>
  <h1 align="center">PyACES</a></h1>
  <p align="center">A python library for the fully homomorphic encryption scheme ACES</p>
</p>

# Presentation

This package proposes an implementation for the ACES cryptosystem where we take parameters $\omega = 1$ and $\mathsf{deg}(u) = n$. Details are available in the preprint  [<em>"Constructing a Fully Homomorphic Encryption Scheme with the Yoneda Lemma"</em>](https://arxiv.org/abs/2401.13255).

The name "PyACES" is pronounced "pisces," echoing a symbol synonymous with [_malleability_](https://en.wikipedia.org/wiki/Malleability_(cryptography)). In the Pisces symbol, the two fishes represent a harmonious interplay between opposite directions, reflecting the dual nature of encryption and decryption.

> [!WARNING]
> Despite the announcement made in the research paper, this implementation has been generalized to any value $N\geq 1$. See the guide attached with this repo for more details on different parameter choices while keeping ACES secure.
>

# Installation

At this time, the only way to install the package is to download its code and use it in your own code as follows.

```python
from pyaces import *
```

# Parameterization

ACES depends on the generation of an <em>arithmetic channel</em>, which is a quadruple $\mathsf{C} = (p,q,\omega,u)$ where $p$, $q$ and $\omega$ are three positive integers and $u$ is a polynomial in $\mathbb{Z}[X]$ for which the equation $u(\omega) = q$ holds in $\mathbb{Z}$. While the integer $\omega$ remains fixed at $1$, and the ACES library automatically generates the polynomial $u$, the user is still required to manually select the values for $p$ $q$, $n = \mathsf{deg}(u)$ and $N$.

A brief review of [section 5.1 of the research paper](https://arxiv.org/abs/2401.13255) already informs us that the condition $p^2 < q$ must hold for ACES to be valid. In conjunction with this prerequisite, the accompanying guide, accessible [here](GUIDE.md) in this repository, provides further insights into considerations for adjusting the values of $p$, $q$ $n$ and $N$. Specficially, users should take

- $p^2 < q$
- $p$ and $q$ coprime
- $q \gg  (K_0Np)^{2^{K+1}}$ for some constant $K_0$ to process at least $K$ layers of operations
- $n = \mathsf{deg}(u) > 4$

For simplicity, we recommend that users use the formula below, where $s \geq 2$, $t \geq 2$, $K_0 \geq 1$, $K_1 \geq 1$ and $K \geq 1$:

$$q = (K_0Np)^{t^{K+1} + K_1 } + 1$$

> [!NOTE]
> Iddition to exploring the parameterization space of ACES, the [guide](GUIDE.md) also elucidates specific technical aspects pertaining to the security of ACES. In particular, it gives useful recommendations on how to use ciphertexts in a secure way (for example see [guide](GUIDE.md#important-considerations)).
>

# Quickstart

To create an arithmetic channel $\mathsf{C} = (p,q,\omega,u)$, use the class ```ArithChannel```. The following snippet shows how to generate an arithmetic channel with
- $p=2^5 = 32$, 
- $q=\cdot p^{2^2+1}+1 = 33554433$, 
- $\mathsf{deg}(u) = 10 = n$ 
- and $N=2$
```python
>>> from pyaces import *
>>> ac = ArithChannel(32,32**5+1,10,2)
```
To generate the public key of a scheme with fully homomorphic properties, use the following instance:
```python
>>> (f0,f1,vanmod,intmod,dim,N,u,tensor) = ac.publish(fhe = True)
```
We can quickly verify that the condition $u(1)=q$ holds as follows.
```python
>>> u
[1]^10+[15561488]^9+[10729359]^8+[5895107]^7+[10512515]^6+[13114310]^5+[31946593]^4+[17963261]^3+[-72168201]^2 (33554433)
>>> sum(u.coefs)-intmod
0
```
Below, we will access the private key $x$ via the property ```ac.x```. It is important to note that the integers $p$ and $q$ used for initializing the arithmetic channel ```ac``` must satisfy the relationships $p^2 < q$ and $\mathsf{gcd}(p, q) = 1$. In cases where these conditions are not met, the class ```ArithChannel``` will generate a new value for $q$ as $p^2+1$.

As elaborated in the research paper and the preceding section, the homomorphism property imposes an upper limit on the maximum achievable level. This limit is determined by the ratio $q/p$, and it can be calculated as shown below:
```python
>>> q_p = intmod/vanmod
>>> q_p
1048576.03125
```
To encrypt messages $m \in \mathbb{Z}_p$, use the class ```ACES``` as shown below.
```python
>>> bob = ACES(f0,f1,vanmod,intmod,dim,N,u)
```
The following example illustrates an encryption of the message $m=3$. The encryption algorithm outputs a ciphertext $(c,c')$ and a vector of integers that can be used to calculate the level of the ciphertext. For the sake of exposition, we also display the polynomials making the vector $c \in \mathbb{Z}_q[X]_u^{(n)}$.
```python
>>> enc3, k3 = bob.encrypt(3)
>>> k3
[2, 14]
>>> for d in enc3.dec:
...   d
...
[21379560]^9+[25028370]^8+[8694508]^7+[28102446]^6+[5172890]^5+[24589603]^4+[5543292]^3+[11274872]^2+[13629468]^1+[19271064]^0 (33554433)
[9108842]^9+[5039426]^8+[21244355]^7+[3175448]^6+[22655005]^5+[15962061]^4+[20588907]^3+[26006670]^2+[27534017]^1+[16266756]^0 (33554433)
[1458536]^9+[24643021]^8+[15203777]^7+[23778795]^6+[24103882]^5+[23940451]^4+[3773861]^3+[9206299]^2+[10862051]^1+[7246808]^0 (33554433)
[22153519]^9+[7780220]^8+[16360279]^7+[28545698]^6+[22573294]^5+[163643]^4+[27158635]^3+[8665100]^2+[5091255]^1+[4834865]^0 (33554433)
[12109157]^9+[4473554]^8+[24217584]^7+[17701710]^6+[1472804]^5+[8994119]^4+[30242395]^3+[3669714]^2+[11512159]^1+[4809361]^0 (33554433)
[16571218]^9+[31797286]^8+[21517446]^7+[9449064]^6+[31547175]^5+[19754057]^4+[22483530]^3+[22371627]^2+[6812861]^1+[20406855]^0 (33554433)
[6535938]^9+[20943309]^8+[10663544]^7+[9754641]^6+[6342352]^5+[25438883]^4+[29421614]^3+[30503775]^2+[14529486]^1+[456676]^0 (33554433)
[17806160]^9+[19626456]^8+[29126106]^7+[24033050]^6+[23506780]^5+[28391799]^4+[4000439]^3+[10046721]^2+[19523779]^1+[17246181]^0 (33554433)
[15096919]^9+[15509580]^8+[14202625]^7+[28337590]^6+[9646278]^5+[31062288]^4+[26781822]^3+[8778106]^2+[20152751]^1+[5062739]^0 (33554433)
[2363338]^9+[16535237]^8+[30285612]^7+[4934198]^6+[21283726]^5+[5267871]^4+[26811682]^3+[5040335]^2+[7297640]^1+[24881255]^0 (33554433)
>>> enc3.uplvl
64
```
In the preceding example, the vector ```k3``` can be used to determine the level of the ciphertext $(c,c')$ by computing its scalar product with the vector ```ac.lvl_e```. The integer ```enc3.uplvl``` is known to all parties and represents an upper bound on the level of $(c,c')$. It is crucial to emphasize that, in practical scenarios, the vector ```k3``` should remain confidential, and only its theoretical upper bound ```enc3.uplvl``` is deemed safe to share. In fact, it is strongly recommended to retain only integers $0 \leq k'_i \leq$```k3[i]``` and securely erase ```k3``` from the computer memory.


To decrypt an encrypted message, use the ```ACESReader``` class. The following example demonstrates how to decrypt the ciphertext ```enc3```. As expected, we retrieve the message $m=3$.
```python
>>> alice = ACESReader(ac)
>>> alice.decrypt(enc3)
3
```
To do arithmetic on encrypted information, use the class ```ACESAlgebra```. The following example shows how to recover the homomorphism properties:

$$\mathsf{Dec}(\mathsf{Enc}(3) + \mathsf{Enc}(5)) = 3+5\quad\quad\mathsf{Dec}(\mathsf{Enc}(3) \cdot \mathsf{Enc}(5)) = 3 \cdot 5$$

```python
>>> alg = ACESAlgebra(vanmod,intmod,dim,u,tensor)
>>> enc5, k5 = bob.encrypt(5)
>>> alice.decrypt(alg.add(enc3,enc5))
8
>>> alice.decrypt(alg.mult(enc3,enc5))
15
```

# Proper FHE

Now that we have explored the features of the leveled FHE underlying ACES, let us illustrate the FHE protocol described in [section 5.3 of the research paper](https://arxiv.org/abs/2401.13255). To make this tutorial relevant to illustrating the refreshing step for the FHE protocol, we will now take the parameters 
- $p=2^5 = 32$, 
- $q=10\cdot p^{2^2+1}+1 = 335544321$, 
- $\mathsf{deg}(u) = 10 = n$ 
- and $N=5$
```python
>>> from pyaces import *
>>> ac = ArithChannel(32,10*32**5+1,10,5)
>>> (f0,f1,vanmod,intmod,dim,N,u,tensor) = ac.publish(fhe = True)
>>> bob = ACES(f0,f1,vanmod,intmod,dim,N,u)
>>> alice = ACESReader(ac)
>>> alg = ACESAlgebra(vanmod,intmod,dim,u,tensor)
>>> q_p = intmod/vanmod

```
Now, we want to consider a list ```array``` of data and its encryption through ACES. We can illustrate this with the following lines of code.
```python
>>> import random as rd
>>> array = [rd.randint(0,5) for _ in range(8)]
>>> enc_array = [bob.encrypt(a) for a in array]
```
As seen earlier, the algorithm ```bob.encrypt()``` returns the ciphertext and its associated level. Since we cannot share levels, we want to separate them as follows.
```python
>>> send_array, keep_array = map(list,zip(*enc_array))
```
We now have the following data:
```python
>>> array
[5, 4, 5, 0, 3, 3, 1, 1]
>>> send_array
[<pyaces.aces.ACESCipher object at 0x7f7c63e9ff10>, <pyaces.aces.ACESCipher object at 0x7f7c8cecb610>, <pyaces.aces.ACESCipher object at 0x7f7c63ebd700>, <pyaces.aces.ACESCipher object at 0x7f7c63ebd070>, <pyaces.aces.ACESCipher object at 0x7f7c63ebdee0>, <pyaces.aces.ACESCipher object at 0x7f7c63ebdcd0>, <pyaces.aces.ACESCipher object at 0x7f7c63ebdc40>, <pyaces.aces.ACESCipher object at 0x7f7c63ec5f10>]
>>> keep_array
[[21, 8, 17, 14, 7], [13, 27, 18, 3, 31], [0, 3, 23, 4, 23], [16, 30, 6, 9, 13], [29, 28, 18, 18, 26], [14, 19, 3, 13, 22], [18, 1, 6, 23, 18], [20, 10, 6, 30, 0]]
```
Since operations on levels need to be dissociated form the algebraic operations done on ciphertext, we want to initiate the refresher algebra as follows.
```python
>>> rfr = ACESRefresher(ac)
```
To simulate an FHE protocol, let us suppose that $\mathsf{Alice}$ has sent the encrypted data ```send_array``` on a remote server and consider a scenario where an algoritm of additions and multiplications as shown below runs on the encrypted data.

$$F:(x_0,x_1,x_2,\dots,x_7) \mapsto (x_0 \cdot x_1 + x_2 \cdot x_3 + x_4 \cdot x_5) \cdot x_6 + x_7$$

We define this algorithm on the non-encrypted data ```array``` (as a sanity check), on the list of encrypted data ```send_array``` and on the list of levels ```keep_array``` as instructed in [section 5.3 of the research paper](https://arxiv.org/abs/2401.13255).
```python
>>> true_fun = Algebra().compile("(0*1+2*3+4*5)*6+7")
>>> send_fun = alg.compile("(0*1+2*3+4*5)*6+7")
>>> keep_fun = rfr.compile("(0*1+2*3+4*5)*6+7")
...
```
First, let us see what the algorithm is meant to output for the values in ```array```:
```python
>>> truth = true_fun(array)
>>> truth % 32
30
```
Now, let us shift our focus to the server side. To recap, we previously set $q = 10\cdot p^{2^2+1}+1$, implying that ```ACESAlgebra``` can likely accommodate only a single layer of a sum of multiplications. However, the ```send_fun``` function incorporates two such layers. As a result, this configuration is sufficient to surpass the levels beyond $q/p$, resulting in a failure of the leveled FHE procedure, as demonstrated below.
```python
>>> online = send_fun(send_array)
>>> online.uplvl
12582912160
>>> q_p - online.uplvl
-12572426399.96875
>>> alice.decrypt(online)
25
```
As explained in [Section 5.3 of the research paper](https://arxiv.org/abs/2401.13255), it is necessary to decompose the algorithm $F$ into smaller layers, namely $F_1$ and $F_2$. For instance, the definition of $F_1$ is presented below.
```python
>>> true_fun1 = Algebra().compile("0*1+2*3+4*5")
>>> send_fun1 = alg.compile("0*1+2*3+4*5")
>>> keep_fun1 = rfr.compile("0*1+2*3+4*5")
```
When we apply $F_1$ to the corresponding ciphertexts, the leveled homomorphism proves to be successful, as evidenced below.
```python
>>> truth1 = true_fun1(array)
>>> truth1 % 32
29
>>> online1 = send_fun1(send_array)
>>> online1.uplvl
2457600
>>> q_p - online1.uplvl
8028160.03125
>>> alice.decrypt(online1)
29
```
Subsequently, we can calculate the equivalent of $F_1$ on the corresponding levels using ```keep_fun1```. In practice, the resulting output level ```k1``` (or in fact any positive integer less than ```k1```) is transmitted to the server, while maintaining the secrecy of the levels in ```keep_array```. Then, the server uses the integer ```k1``` to refresh the ciphertext ```online1```.
```python
>>> k1 = keep_fun1(rfr.process(keep_array))
>>> c1 = alg.refresh(online1,k1)
>>> c1.uplvl
2380640
>>> alice.decrypt(c1)
29
```
As can be seen above, the refresh operation does not impact the message associated with the ciphertext; rather, it diminishes the upper bound level ```c1.uplvl```. While this reduction may appear trivial when compared to the earlier value of ```online1.uplvl```, the refresh operation nevertheless remains efficient in revitalizing the ciphertext.

To confirm the success of this refresh operation, we can now proceed to compute the second layer of the algorithm $F$. First, let us define the function $F_2$ associated with this the second layer.
```python
>>> true_fun2 = Algebra().compile("8*6+7")
>>> send_fun2 = alg.compile("8*6+7")
>>> keep_fun2 = rfr.compile("8*6+7")
```
If we now combine this second layer with the output of the refresh operation, we can validate that the computed ciphertext accurately recovers the true value of the computation.
```python
>>> truth2 = true_fun2(array+[truth1])
>>> truth2 % 32
30
>>> online2 = send_fun2(send_array + [c1])
>>> online2.uplvl
12188876960
>>> q_p - online2.uplvl
-12178391199.96875
>>> alice.decrypt(online2)
30
```
A limitation in our presentation was that our algorithm struggled to handle numerous layers of additions and multiplications. Although this might restrict the volume of information processed simultaneously, we could enhance the level range by setting $p=2$ and $q = 2^{2^5+5}+1 = 137438953473$.
