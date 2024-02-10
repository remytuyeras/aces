# Best practices for ACES

- [Recap](#recap)
- [ACES security](#aces-security)
- [Homomorphism and why it works](#homomorphism-and-why-it-works)
- [Take away on parameters](#take-away-on-parameters)


## Recap

ACES depends on the generation of an arithmetic channel, defined as a quadruple $\mathsf{C} = (p, q, \omega, u)$, where $p$, $q$, and $\omega$ are positive integers, and $u$ is a polynomial in $\mathbb{Z}[X]$ satisfying the equation $u(\omega) = q$ in $\mathbb{Z}$. While the integer $\omega$ remains fixed at $1$ and the ACES library automatically generates the polynomial $u$, the user is still required to manually select the values for $p$ and $q$.

Importantly, the security of ACES relies on two consecutive modulus operations, specifically involving the positive integers $q$ and $p$. We will review the corresponding security principles pertaining to these two integers in the subsequent subsections.

### ACES encryption

The ACES framework encrypts a message $m \in \mathbb{Z}_p$ as a ciphertext $(c,c')$ according to the following procedure:

1. The first component $c$ is an $n$-vector over $\mathbb{Z}_q[X]_u$ given by $c = f_0^Tb$, where:
    - $f_0$ is an $n \times N$ matrix over $\mathbb{Z}_q[X]_u$ (chosen during key generation).
    - $b = (b_i)_i$ is an $N$-vector over $\mathbb{Z}_q[X]_u$ such that $b_i(\omega) \in \lbrace 0,1,\dots,p \rbrace$ (selected by the sender).

2. The second component $c'$ is an element of $\mathbb{Z}_q[X]$ defined as $c' = r_m + c^Tx + e$, where:
    - $r_m$ is an element over $\mathbb{Z}_q[X]_u$ chosen such that its evaluation in $\mathbb{Z}_q$ at the integer $\omega$ equals $m$ (chosen by the sender).
    - $x$ is an $n$-vector over $\mathbb{Z}_q[X]_u$ (considered the private key).
    - $e$ is a scalar product in the form of $b^Te'$, where $e'= (e_i')_i$ is an $N$-vector over $\mathbb{Z}_q[X]_u$ such that the evaluation of $e_i'$ in $\mathbb{Z}_q$ at the integer $\omega$ is equal to a product $p \ell$ where $\ell \in \lbrace 0,1\rbrace$.


## ACES Security

### Protecting the public key

Given that the public key takes the form $(f_0, f_1)$ with $f_1 = f_0^Tx + e'$, it is reasonable to assume that an attacker's objective might involve deducing the value of $x$ by analyzing the distribution of $f_1$.

First, let us establish that the polynomial $e' = (e_1',\dots,e_N')$ is determined by the sender $\mathsf{Bob}$ through the selection of a random $N \times n$-matrix $(a_{i,j})_{i,j}$ in $\mathbb{Z}_q$, a random $N$-vector $s=(s_1,s_2,\dots,s_N)$ of non-negative integers $s_i < n$ and a random $N$-vector 

$$\epsilon=(\epsilon_1,\epsilon_2,\dots,\epsilon_N)$$

of elements $\epsilon_{i} \in \lbrace 0,1\rbrace$ with the following conditions:
- The equation $\epsilon_{i} = 0$ holds with probability $\mathbb{P}_i$.
- The expression for $e'_i$ is given by the following formula

$$e_i' = \Big(\big(p \epsilon_{i} - \sum_{j=0}^{n-1} a_{i,j} \big)~(\mathsf{mod}~q)\Big)X^{s_i} + \sum_{i=0}^{n-1} a_{i,j}X^j$$


#### Attacks in $\mathbb{Z}_q[X]_u$

Given a $n$-vector $x'$ over $\mathbb{Z}_q[X]_u$, an attacker may want to analyze the distribution of the polynomials 

$$f_{1,i} - \mathsf{row}_i(f_0)^Tx'$$

for every $i \in \lbrace 1,2,\dots,N\rbrace$. Note that the sample associated with this distribution is given by the following set.

$$\lbrace \mathsf{row}_i(f_0)^T(x-x') + e_i' ~|~i \in \lbrace 1,2,\dots,N\rbrace \rbrace$$

If the attacker found an element $x'$ such that $f_0^Tx = f_0^Tx'$, the previous distribution would appear random since the distribution of the coefficients $a_{i,j}$
is uniform. More specifically, in this scenario, the polynomials are examined coefficient by coefficient, which means that the attacker would only perceive the randomness of each coefficient and not their overall relationships. We reach a similar conclusion for any other element $x'$, as the summand $\mathsf{row}_i(f_0)^T(x-x')$ would merely shift the random behavior by a constant value. As a result, ACES benefits from the hardness of the RLWE problem.


>[!NOTE]
>The paper ["Provably Weak Instances of Ring-LWE Revisited"](https://eprint.iacr.org/2016/239.pdf) provides examples where an attack on the presented version of RLWE (PLWE) is feasible due to the condition $u(1) = 0$ in $\mathbb{Z}_q$. It is crucial to note that this vulnerability is observed in cases where $q$ is small, and the error term $e'$ tends to exhibit a distribution closer to Gaussian than uniform. It is important to emphasize that this scenario is distinct from the context considered in ACES.
>


#### Attacks in $\mathbb{Z}$ with evaluations at $\omega$

An attacker may want to take advantage of the form of the image of $e'$ in $\mathbb{Z}_q$ when evaluated at $\omega=1$. Specifically, the attacker is likely to exploit the existence of a non-negative integer $k_i$ satisfying the equation:

$$e_{i}'(\omega) - qk_i = p \epsilon_{i}$$

It is worth noting that the probability of $k_i$ being non-zero is high, given that the coefficients $a_{i,j}$ are as likely to be small as they are to be large in the interval $\mathbb{Z}_q$. Because the attacker is not assumed to know the value of each $e_i'(\omega)$ they may likely to attack the public key using some search/decision algorithm. Specifically, given a $n$-vector $x'$ over $\mathbb{Z}_q[X]_u$, an attacker may want to analyze the distribution of the integers 

$$f_{1,i}(\omega) - \mathsf{row}_i(f_0(\omega))^Tx'(\omega)\quad(\mathsf{mod}\,q),$$

The previous integer can be calculated as a difference of the form $\chi_i = f_{1,i}(\omega)- \mathsf{row}_i(f_0(\omega))^Tx'(\omega)-qk_i'$ for some positive integer $k_i'$. This means that the attacker has access to a distribution of the following form:

$$\chi_{i} = \mathsf{row}_{i}(f_0(\omega))^{T}(x(\omega)-x'(\omega)) + p \epsilon_i+q(k_i-k_i')$$

The previous formula means that if $f_0^Tx = f_0^Tx'$, then the distribution of the data points is restricted to elements of the form $qk + p \epsilon$ with $\epsilon \in \lbrace 0,1 \rbrace$ and $k \in \mathbb{N}$. Without any assumption on $f_0$, this may give a way for an attacker to search for elements $x'$ capturing the values of $x$ when evaluated at the element $\omega$.

However, if we sample $f_0 = (f_{0,i,j})_{i,j}$ according to the formula

$$f_{0,i,j} = \Big(\big(p k_{i,j} - \sum_{k=0}^{n-1} v_{i,j,k}\big)~(\mathsf{mod}~q)\Big)X^{s_{i,j}} + \sum_{k=0}^{n-1} v_{i,j,k}X^k$$

where each $s_{i,j}$ is a random integer from the interval $[0,n-1]$, each $k_{i,j}^{\prime\prime}$ is a random element from  $\mathbb{Z}_q$ and each $v_{i,j,k}$ is a random element from $\mathbb{Z}_q$, then we have the property that $f_{0,i,j}(\omega)$ is a non-trivial multiple $p k_{i,k}$ of $p$ in $\mathbb{Z}_q$. In other words, the distribution of the data points $\chi_i$ looks more like a random sample of elements from $p\mathbb{N} + q\mathbb{Z}$. If we choose $p$ and $q$ to be coprime, then the set $p\mathbb{N} + q\mathbb{Z}$ is equal to $\mathbb{N}$, which means that that the distribution of our data points $\chi_i$ would just look uniform in $\mathbb{Z}_q$. Indeed, suppose that we can find $x'$ such that there are $\eta_i \in \lbrace 0,1\rbrace$ and $\kappa_i \in \mathbb{N}$ for which the following equation holds.

$$\chi_i = p \eta_i + q \kappa_i$$

In this context, we have the following relation, where $k_i^{\prime\prime}$ denotes the vector $(k_{i,1}^{\prime\prime},\dots,k_{i,N}^{\prime\prime})$.

$$q(\kappa_i + k_i'-k_i) = p\Big((k_i^{\prime\prime})^T(x(\omega)-x'(\omega)) + \epsilon_{i} - \eta_i \Big)$$

When $p$ and $q$ are coprime, the previous equation can be decomposed into two relations as follows:

$$k_i \equiv \kappa_i + k_i' \,(\mathsf{mod}\,p) \quad\quad\quad (k_i^{\prime\prime})^T(x(\omega)-x'(\omega)) \equiv \eta_i - \epsilon_{i}  \,(\mathsf{mod}\,q)$$

The equation displayed on the right says that the vector $(k_i^{\prime\prime})^Tx'(\omega)$ in $\mathbb{Z}_q$ is of the form 

$$(k_i^{\prime\prime})^Tx(\omega) + \eta_i'$$

for some $\eta_i' \in \lbrace -1,0,1 \rbrace$. In other words, the attacker is only given a vector very close to the lattice generated by the vector $k_i^{\prime\prime}$. Since finding vectors of a lattice that are close to some given vector is considered a difficult, it follows that the attacker will face the challenge of solving a [Closest Vector Problem](https://en.wikipedia.org/wiki/Lattice_problem#Closest_vector_problem_(CVP)).

### Protecting your ciphertext 

Recall that a general ciphertext $(c,c')$ consists of an $n$-vector $c$ over $\mathbb{Z}_q[X]_u$ and an element $c$ in $\mathbb{Z}_q[X]_u$ such that the equation 

$$c' = r_m + c^Tx + e$$

holds and where the folloiwng conditions are satisfied:
- $r_m$ is an element of $\mathbb{Z}_q[X]_u$ such that the value $r_m(\omega)$ is equal to the value of a message $m$ in $\mathbb{Z}_q$;
- $e$ is an element of $\mathbb{Z}_q[X]_u$ such that the value $e(\omega)$ is a multiple of $p$ in $\mathbb{Z}_q$.

Here, it is reasonable to assume that an attacker's objective might involve deducing the value of $r_m$ by analyzing the distribution of $c'$. To discuss this scenario, let us establish that the polynomial $r_m$ is determined by the sender $\mathsf{Bob}$ through the selection of $n$ random coefficients $m_0, m_1, \dots, m_{n-1}$ in $\mathbb{Z}_q$ and a random non-negative integer $s < n$. This encoding follows the formula:

$$r_m = \Big(\big(m - \sum_{i=0}^{n-1} m_i\big)~(\mathsf{mod}~q)\Big)X^s + \sum_{i=0}^{n-1} m_iX^i$$

#### Important considerations

While the previous structure can already suggest various attack models on the ciphertext, it is important to note that the encryption of a given message $m$ by ACES is even more specific as $e = b^Te'$ and $c = b^Tf_1$. 

In our implementation, the polynomial $b$ is determined by $\mathsf{Bob}$ through the selection of $n$ random coefficients $b_0, b_1, \dots, b_{n-1}$ in $\mathbb{Z}_q$, a random non-negative integer $s' < n$ and a random element $\delta_1 \in \lbrace 0,1,\dots,p\rbrace$ with the formula:

$$b = \Big(\big(\delta_1 - \sum_{i=0}^{n-1} b_i\big)~(\mathsf{mod}~q)\Big)X^{s'} + \sum_{i=1}^{n-1} b_iX^i$$

While $b$ is generated randomly, it still has the property that $b(\omega) \in \lbrace 0,1,\dots,p \rbrace$, which may give some advantage to an attacker as the evaluation $(be')(\omega)$ womightuld still be small in $\mathbb{Z}_q$.

To prevent an attacker to take advantage of the previous properties, the encrypter is recommanded to apply a random identity operation on the encrypted data to convert it into a ciphetext $(c,c')$ with a general as defined above.

For example, the ciphertext resulting from the following operations on the encrypted data $\mathsf{E}(m)$ can still be decoded as $m$, but it does not have the same form as if it had just been produced by ACES:

$$\mathsf{Enc}(1) \otimes \mathsf{Enc}(m) \oplus \mathsf{Enc}(0)\oplus\mathsf{Enc}(0) \otimes \mathsf{Enc}(1)$$

However, since every general ciphertext should be assumed to result from a homomorphic operation on ciphertexts generated by ACES, general ciphertexts still have some structure that can be exploited if the matrix 

$$f_0 = (f_{0,i,j})_{i,j}$$

satisfies certain properties. For example, if the evaluations $f_{0,i,j}(\omega)$ are all multiples of $p$ in $\mathbb{Z}$, then so do the coefficients of the vectors $c$ associated with any ciphertext $(c,c')$. These considerations are taken into account in the following two sections.

#### Attacks in $\mathbb{Z}_q[X]_u$

Given a $n$-vector $x'$ over $\mathbb{Z}_q[X]_u$, an attacker may want to analyze the distribution of the coefficients making the polynomial $c' - c^Tx'$. Specifically, the sample associated with this distribution is given by the following set, where $\rho_i$ returns the $i$-th coefficient of its input.

$$\lbrace \rho_i(r_m) + \sum_{j=0}^{i} \rho_j(c) \cdot \rho_{i-j}(x-x') + \rho_{i}(e) ~|~j \in \lbrace 0,2,\dots,n-1\rbrace \rbrace$$

If the attacker found an element $x'$ such that $c^Tx = c^Tx'$, the previous distribution would appear random because the polynomial $e$ can be expressed as products and sums of polynomials whose coefficients are randomly picked in $\mathbb{Z}_q$. 

Note that, in our scenario, the polynomials are examined coefficient by coefficient, which means that the attacker would only perceive the randomness of each coefficient and not their overall relationships. For example, the $s$-th coefficient of $r_m$, which is of the form 

$$(m - \sum_{i=0}^{n-1} m_i + m_s \big)~(\mathsf{mod}~q)$$

would still look random. Indeed, during the generation of $r_m$, $\mathsf{Bob}$ has the freedom to select $a_0, a_1, \dots, a_{n-1}$ such that the inequality 

$$m < \sum_{i=1}^{s-1}m_i + \sum_{i=s+1}^{n-1}m_i < q$$

holds in $\mathbb{Z}$. This means that the term 

$$m - \sum_{i=0}^{n-1}m_i + m_s$$

lands outside the interval $[0, q-1]$, which introduces an additional term $qk_0$ to the computation of the $s$-th coeffcient in $\mathbb{Z}_q$. 

$$(m - \sum_{i=0}^{n-1} m_i + m_s \big)~(\mathsf{mod}~q) = m - \sum_{i=1}^{s-1}m_i - \sum_{i=s+1}^{n-1}m_i + qk_0$$

Furthermore, because each coefficient $m_i$ is taken randomly in the interval $[0, q-1]$, the sum $m - \sum_{i=0}^{n-1}m_i + m_s$ varies within the interval $[-(n-1)q,p]$. Consequently, the element $k_0$ should reasonably be inferred within the interval $[0,n]$. This calculation also suggests that the value of $k_0$ is mainly determined by the coeffcients $m_i$ as the value $m$ is less than $p$, which can be considered much smaller than $q$ (since $p^2 < q$).

Selecting coprime $p$ and $q$ would then ensure that the "randomness" of the term $qk_0$ is entirely determined by the randomness of the elements $m_0, m_1, \dots, m_{n-1}$.

Finally, because the same principles as those listed above hold even when $c^Tx \neq c^Tx'$, it follows that ACES benefits from the hardness of the LWE/RLWE problem in all cases.

#### Attacks in $\mathbb{Z}$ with evaluations at $\omega$

An attacker may want to take advantage of the properties satisfied by the images of $e$ and $r_m$ in $\mathbb{Z}_q$ when evaluated at $\omega=1$. Specifically, the attacker is likely to exploit the existence of two non-negative integers $k_0$ and $k_1$ satisfying the following equations for some non-negative integer $\lambda$

$$e(\omega) - qk_0 = p \lambda \quad\quad\quad\quad\quad r_m(\omega) - qk_1 = m$$

It is worth noting that the probability of $k_0$ and $k_1$ being non-zero is high, given that the coefficients of $e$ and $r_m$ are as likely to be small as they are to be large in $\mathbb{Z}_q$. Because the attacker is not assumed to know the values of $e(\omega)$ and $r_m(\omega)$, they may likely to attack the public key using some search/decision algorithm.

Specifically, given a $n$-vector $x'$ over $\mathbb{Z}_q[X]_u$ and an integer $m' \in \mathbb{Z}_p$, an attacker may want to decompose the following quantity:

$$c'(\omega) - c(\omega)^Tx'(\omega) - m'\quad(\mathsf{mod}\,q),$$

The previous integer can be calculated as a difference of the form $\chi = c'(\omega) - c(\omega)^Tx'(\omega) - m'-qk_2$ for some positive integer $k_2$. This means that the attacker has access to a quantity of the following form:

$$\chi = m-m' + p \lambda + q(k_0+k_1-k_2) + c(\omega)^T(x(\omega)-x'(\omega))$$

As explained in previous sections, we have a certain interest in making the image $f_{0,i,j}(\omega)$ to be multiples of $p$. As a result, given that we can assume that the ciphertext $(c,c')$ is the result of a homomorphic calculation using encrypted data as produced by ACES, it is reasonable to assume that the attacker will deal with a ciphertext $(c,c')$ such that the coefficients of $c(\omega)^T$ are multiples of $p$ in $\mathbb{Z}_q$. As a result, we can supposed that there exists a $n$-vector 

$$k_3 = (k_{3,1},k_{3,2},\dots,k_{3,n})$$

of non-negative integers such that $c(\omega)^T(x(\omega)-x'(\omega)) = pk_3^T(x(\omega)-x'(\omega))$. This means that we now have the following equation:

$$\chi = m-m' + q(k_0+k_1-k_2) + p(k_3^T(x(\omega)-x'(\omega))+\lambda)$$

If we choose $p$ and $q$ to be coprime, then usual theorems on Diophantine equations imply that the number of solutions for the previous equation is significant. Indeed, suppose that we can find $x'$ and $m'$ such that there are $\eta \in \mathbb{Z}$ and $\kappa \in \mathbb{N}$ for which the following equation holds.

$$\chi = p \eta + q \kappa$$

In this context, we have the following relation:

$$ q(k_0+k_1-k_2-\kappa) + p(k_3^T(x(\omega)-x'(\omega))+\lambda-\eta) = m'-m$$

Assuming that the attacker can easily find a soluton $(h_0,h_1)$ to the Diophantine equation $qh_0 + ph_2 = 1$, the attacker will have to find an integer $v$ such that we have:

$$(m'-m)(k_0+k_1-k_2-\kappa) = h_0+pv \quad\quad\quad\quad (m'-m)\Big(k_3^T(x(\omega)-x'(\omega))+\lambda\eta\Big) = h_1-qv$$

While $(\kappa,\eta,k_{3,1},\dots,k_{3,n},h_0,h_1,m')$ are given, the integers

$$(k_0,k_1,k_2,x_1(\omega),\dots,x_n(\omega),\lambda,v,m)$$

still have to be inferred. These considerations show that attacking ciphertexts in the way described above will likely be equivalent to searching the space of solutions of a system of two quadratic equations with $n+6$ unknown variables. This means that there is a large number of solutions to try for the attacker. 

Alternatively, we can look at the previous problem as a Diophatine equation of $n+2$ variables as follows:

$$q(k_0+k_1-k_2-\kappa) + pk_{3,1}(x_1(\omega)-x_1'(\omega)) + \dots + pk_{3,n}(x_n(\omega)-x_n'(\omega))+p(\lambda-\eta) = m'-m $$

Ideally, we want the solution of this equation to be such that the quantities

$$k_0+k_1-k_2-\kappa \quad\quad\quad k_3^T(x(\omega)-x'(\omega))+\lambda-\eta \quad\quad\quad x(\omega)-x'(\omega)$$

are as close as possible to 0 (if not equal to 0) so that we can have a situation where $m' = m$, and $x' = x$. This can add to the difficulty of finding the right solution. To corborate this intuition further, we can mention that, in general, [solving Diophantine equations for vectors with small norms is hard](https://dl.acm.org/doi/10.1016/j.tcs.2006.12.023), and is closely related to solving a [Short Integer Solution probolem](https://en.wikipedia.org/wiki/Short_integer_solution_problem) or a Shortest Vector Problem.

## Homomorphism and why it works

While the decryption in ACES operates within the ring $\mathbb{Z}$, it is essential to recognize that the homomorphic structure is established within the polynomial ring $\mathbb{Z}_q[X]_u$. In drawing a parallel, consider this process akin to employing complex numbers for computations that might pose greater challenges when exclusively using real numbers, such as solving polynomials or analyzing signals.

Specifically, if we let $x = (x_1,\dots,x_n)$ denote the private key for ACES, then the homomorphism property relies on a 3-tensor $\lambda = (\lambda_{i,j}^k)_{i,j,k}$ satisfying the following relation for every triple $(i,j,k)$ of elements in $\lbrace 0,1,2,\dots,n\rbrace$.

$$x_i \cdot x_j = \sum_{i,j} \lambda_{i,j}^k x_k$$

If we tried to imagine what this equation would amount to in the context of complex numbers, we would be faced with the challenge of finding real numbers $\lambda_1$ and $\lambda_2$ for which equations of the following form holds.

$$(a_1+ib_1)(a_2+ib_2) = \lambda_1 \cdot (a_1+ib_1) + \lambda_2 \cdot (a_2+ib_2)$$

By uniqueness of the complex and real parts, we would then obtain:
- $\lambda_1 a_1 + \lambda_2 a_2 = a_1a_2-b_1b_2$
- $\lambda_1 b_1 + \lambda_2 b_2 = a_1b_2+a_2b_1$

Note that without the complex structure, deducing the values of $\lambda_1$ and $\lambda_2$ would be challenging. This underscores how $\mathbb{C}$ introduces a mathematical structure that cannot be recovered by $\mathbb{R}$. In a parallel manner, we leverage the polynomial ring $\mathbb{Z}[X]$ to encapsulate the homomorphic properties of ACES. After performing arithmetic operations on polynomials to compute homomorphic sums and products, we can seamlessly revert to $\mathbb{Z}$ for decrypting the encrypted data.

### Remark on security

The conditions that define the coefficients of the 3-tensor $\lambda = (\lambda_{i,j}^k)_{i,j,k}$ are essentially equivalent to solving a system of quadratic polynomial equations in a finite <s>field</s> ring. In theory, the task of recovering the private key $x$ from the 3-tensor $\lambda$ is safeguarded by the Polynomial System Solving Problem. Specifically, if we express

$$x_k = \sum_{i=1}^{n-1} a_{k,i} X^i \quad\quad\textrm{and}\quad\quad u = \sum_{i=1}^{n-1} \mu_i X^i,$$

there exists a tuple $(a_0',a_1',\dots,a_{n-1}')$ of integers in the range $[0, q-1]$ such that, for every $r \in \lbrace 0,1,2,\dots,n-1\rbrace$, the coefficients of $\lambda$ satisfy the following equations in $\mathbb{Z}_q$:

$$\sum_{s+t = r } a_{i,s} a_{j,t} - \sum_{s+t = r } \mu_{s} a_{t}' = \sum_{k=0}^{n-1}\lambda_{i,j}^{k} a_{k,r}.$$

Solving this set of equations involves finding a <u>specific</u> solution $(a_{1,0},\dots,a_{n,n-1},a_0',\dots,a_{n-1}')$ for a system of $n$ quadratic polynomial equations

$$f_1(w_1,\dots,w_{n(n+1)}) = 0,$$

$$\vdots$$

$$f_{n}(w_1,\dots,w_{n(n+1)}) = 0,$$

in the finite ring $\mathbb{Z}_q$. According to research ([source](https://inria.hal.science/hal-00776070/document) and [source](https://www-polsys.lip6.fr/~jcf/Papers/JMC2.pdf)), embarking on an exhaustive search for the solution would result in a computational complexity of $O(q^{n(n+1)})$. Opting for a sufficiently large value of $q$ would force an attacker to turn to a formal calculus algorithm, such as the [F5 algorithm](https://en.wikipedia.org/wiki/Faug%C3%A8re%27s_F4_and_F5_algorithms), designed for solving polynomial equations with Gröbner basis. However, note that in our specific scenario, employing Gröbner basis techniques on our set of polynomial equations would prove ineffective since the equations characterizing $\lambda$ are already _reduced_.

Indeed, observe that the monomial $a_{i,s}a_{j,t}$ can only appear in the equation $f_{s+t}(w_1,\dots,w_{n(n+1)}) = 0$, indicating that it cannot be further reduced by the other equations. Consequently, an attacker attempting to compromise the private key using the equations defining the 3-tensor $\lambda$ would likely have to resort to either an exhaustive search or a hybrid method, which could be disadvantageous, particularly if $q$ is chosen to be large.

### Cost of homomorphism


ACES is a fully homomorphic encryption scheme that initially relies on a leveled FHE framework. This framework is then equipped with a refresh operation $\mathsf{refr}$ designed to mitigate the level increase resulting from arithmetic operations. In this section, we explore the conditions that must be satisfied by the parameters $p$ and $q$ to leverage the homomorphism property.

For two ciphertexts $(c_1, c_1') \in S_{\mathsf{C},k_1}(m_1)$ and $(c_2, c_2') \in S_{\mathsf{C},k_2}(m_2)$ with respective levels $k_1$ and $k_2$, the homomorphic sum of these ciphertexts can be computed if the inequality shown below on the left holds:

$$k_1 + k_2 < \frac{q}{p} \quad\quad\quad\Rightarrow\quad\quad\quad (c_1, c_1') \oplus (c_2, c_2') \in S_{\mathsf{C}, k_1 + k_2}(m_1 + m_2)$$

Similarly, for a suited parameter $\lambda$ (refer to [the paper in section 5.2](https://arxiv.org/abs/2401.13255)), the homomorphic product of the ciphertexts $(c_1, c_1')$ and $(c_2, c_2')$ is achievable if the inequality shown below on the left holds:

$$k_1 k_2 p < \frac{q}{p} \quad\quad\quad\Rightarrow\quad\quad\quad (c_1, c_1') \otimes_{\lambda} (c_2, c_2') \in S_{\mathsf{C}, k_1 k_2 p}(m_1 m_2)$$

Furthermore, given that any encryption $(c, c')$ produced through ACES is constrained by an upper bound represented by the integer $Np$, we can derive an estimate for $q$ in terms of $p$ and $N$ to ensure the system's capability to be decrypted after homomorphic additions and multiplications. To elaborate further, starting with ciphertexts generated by ACES, a multiplication operation results in a level of $N^2p^3$, whereas an addition operation yields a level of $2Np$. Consequently, a combination of additions and multiplications in the form:

$$x_1 \cdot y_1 + x_2 \cdot y_2 + \dots + x_h \cdot y_h$$

will produce a ciphertext with a level in $O(N^2p^3)$. Thus, using approximately $K$ layers of such combinations leads to a ciphertext with a level in 

$$O(N^{2^{K+1}-1}p^{3\cdot 2^{K-1}}p^{2^{K-1}-1})$$

Considering our desire for this level to be significantly less than $q/p$, the following inequality should be satisfied for the use of around $K$ layers of additions and multiplications:

$$q \gg  (K_0Np)^{2^{K+1}}$$

### Protection against the Chinese Remainder Theorem

The existence of the 3-tensor $\lambda$ facilitating homomorphic multiplications in ciphertexts stems from the quotient of the ring $\mathbb{Z}_q[X]$ by the polynomial ideal generated by $u$. Consequently, the parameter $u$ plays a crucial role in our system. However, this parameter introduces a potential vulnerability, as an attacker might attempt to glean information about the private key through it.

First, recall that the polynomial $u$ is taken in $\mathbb{Z}[X] \subseteq \mathbb{R}[X]$ such that $u(\omega) = q$. Let the sequence

$$\omega_1, \omega_2, \dots, \omega_{\rho}$$ 

denote the distinct roots of $u$ in $\mathbb{C}$ when $u$ is treated as a polynomial in $\mathbb{R}[X]$. Given the equation $u(\omega_i) = 0$ for all $i \in \lbrace 1,2,\dots,\rho \rbrace$, we have the following expression in $\mathbb{C}$:

$$c'(\omega_k) = r(m)(\omega_k) + c(\omega_k)^Tx(\omega_k) + e(\omega_k) + qk_{0}$$

Decomposing the polynomials $r(m)$ and $e$ yields the following formula, where $a_i$ and $a_i'$ are coefficients to be determined:

$$c'(\omega_k) = m + \sum_{i=1}^{n-1} a_i\big(\omega_k^i - 1\big) + c(\omega_k)^Tx(\omega_k) + p \delta + \sum_{i=1}^{n-1} a_i'\big(\omega_k^i - 1\big) + qk_{0}$$

This equation implies that we are attempting to solve a system of $\rho$ linear equations with $3n$ unknown variables:

$$(m,k_{0},\delta,a_1, a_2, \dots, a_{n-1}, x_1(\omega_k), \dots, x_n(\omega_k), a_1', a_2', \dots, a_{n-1}')$$

Given that $\rho \leq \mathsf{degree}(u) = n < n + 2n + 1$, deducing the values of $a_i$ and $a_i'$ through this approach could become particularly challenging. This difficulty becomes more pronounced when the value of $n$ exceeds $4$, introducing the possibility of some roots $\omega_k$ being complex numbers and [non-expressible by radicals](https://en.wikipedia.org/wiki/Solution_in_radicals). This intricacy adds complexity to the task of [precisely determining](https://en.wikipedia.org/wiki/Wilkinson%27s_polynomial) the approximate values of the coefficients of $c^T(\omega_k)$.

## Take away on parameters

Throughout the preceding sections, we showed that users should adhere to the following requirements when selecting values for $p$, $q$, $n$ and $N$:

- we should have $p^2 < q$
- $p$ and $q$ should be coprime
- to process at least $K$ layers of operations, we should have $q \gg  (K_0Np)^{2^{K+1}}$ for some constant $K_0$.
- we should take $n = \mathsf{deg}(u) > 4$
