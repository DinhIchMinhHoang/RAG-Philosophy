<table border="1"><tr><td colspan="2">Calculus</td></tr><tr><td>$\frac{dy}{dx}$</td><td>Derivative of $y$ with respect to $x$</td></tr><tr><td>$\frac{\partial y}{\partial x}$</td><td>Partial derivative of $y$ with respect to $x$</td></tr><tr><td>$\nabla_{x}y$</td><td>Gradient of $y$ with respect to $x$</td></tr><tr><td>$\nabla_{x}y$</td><td>Tensor containing derivatives of $y$ with respect to $X$</td></tr><tr><td>$\frac{\partial f}{\partial x}$</td><td>Jacobian matrix $J \in \mathbb{R}^{m \times n}$ of $f: \mathbb{R}^{n} \rightarrow \mathbb{R}^{m}$</td></tr><tr><td>$\nabla_{x}^{2}f(x)$ or $H(f)(x)$</td><td>The Hessian matrix of $f$ at input point $x$</td></tr><tr><td>$\int f(x)dx$</td><td>Definite integral over the entire domain of $x$</td></tr><tr><td>$\int \mathbb{S}f(x)dx$</td><td>Definite integral with respect to $x$ over the set $\mathbb{S}$</td></tr><tr><td colspan="2">Probability and Information Theory</td></tr><tr><td>a $\bot$ b</td><td>The random variables $a$ and $b$ are independent</td></tr><tr><td>a $\bot$ b | c</td><td>They are conditionally independent given $c$</td></tr><tr><td>$P(a)$</td><td>A probability distribution over a discrete variable</td></tr><tr><td>$p(a)$</td><td>A probability distribution over a continuous variable, or over a variable whose type has not been specified</td></tr><tr><td>a $\sim P$</td><td>Random variable $a$ has distribution $P$</td></tr><tr><td>$\mathbb{E}_{x \sim P}[f(x)]$ or $\mathbb{E}f(x)$</td><td>Expectation of $f(x)$ with respect to $P(x)$</td></tr><tr><td>$\operatorname{Var}(f(x))$</td><td>Variance of $f(x)$ under $P(x)$</td></tr><tr><td>$\operatorname{Cov}(f(x), g(x))$</td><td>Covariance of $f(x)$ and $g(x)$ under $P(x)$</td></tr><tr><td>$H(x)$</td><td>Shannon entropy of the random variable $x$</td></tr><tr><td>$D_{\mathrm{KL}}(P \| Q)$</td><td>Kullback-Leibler divergence of $P$ and $Q$</td></tr><tr><td>$\mathcal{N}(x; \mu, \Sigma)$</td><td>Gaussian distribution over $x$ with mean $\mu$ and covariance $\Sigma$</td></tr></table>

Functions

$f : \mathbb{A} \rightarrow \mathbb{B}$ The function $f$ with domain $\mathbb{A}$ and range $\mathbb{B}$

$f \circ g$ Composition of the functions $f$ and $g$

$f(\mathbf{x}; \theta)$ A function of $\mathbf{x}$ parametrized by $\theta$. (Sometimes we write $f(\mathbf{x})$ and omit the argument $\theta$ to lighten notation)

$\log x$ Natural logarithm of $x$

$\sigma(x)$ Logistic sigmoid, $\frac{1}{1 + \exp(-x)}$

$\zeta(x)$ Softplus, $\log(1 + \exp(x))$

$||\mathbf{x}||_p$ $L^p$ norm of $\mathbf{x}$

$||\mathbf{x}||$ $L^2$ norm of $\mathbf{x}$

$x^+$ Positive part of $x$, i.e., $\max(0, x)$

$1_{\text{condition}}$ is 1 if the condition is true, 0 otherwise

Sometimes we use a function $f$ whose argument is a scalar but apply it to a vector, matrix, or tensor: $f(\mathbf{x}), f(\mathbf{X}),$ or $f(\mathbf{X})$. This denotes the application of $f$ to the array element-wise. For example, if $\mathbf{C} = \sigma(\mathbf{X})$, then $C_{i,j,k} = \sigma(X_{i,j,k})$ for all valid values of $i, j$ and $k$.

Datasets and Distributions

$p_{\text{data}}$ The data generating distribution

$\hat{p}_{\text{data}}$ The empirical distribution defined by the training set

$\mathbb{X}$ A set of training examples

$\mathbf{x}^{(i)}$ The $i$-th example (input) from a dataset

$y^{(i)}$ or $\mathbf{y}^{(i)}$ The target associated with $\mathbf{x}^{(i)}$ for supervised learning

$\mathbf{X}$ The $m \times n$ matrix with input example $\mathbf{x}^{(i)}$ in row $X_{i,:}$