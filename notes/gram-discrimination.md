# Testing competing Gram models

We interpret each response Gram as a covariance, explicitly regularized by `eta I`, with `eta=0.05 lambda_max(Q_zero)`. This changes the model and makes both covariances positive definite. A common invertible whitening and rotation turns the two centered Gaussian laws into products with marginal variances `1` and the generalized covariance eigenvalues. Independence belongs to these transformed Gaussian coordinates and repeated draws, not to entries of a random Gram matrix.

[Avital–Kontorovich–Vershynin–Zou, Theorem 1.2](https://arxiv.org/abs/2609.21049v1) gives a scalar proxy for product total variation. With midpoint score `u=(p-q)/(p+q)` and midpoint law `M=(P+Q)/2`, solve

```text
sum_i log E_Mi sqrt(1+u_i^2/t^2) = 1/2.
```

Then `min(1,t)` is comparable to TV up to universal constants. It is not TV itself or a calibrated error probability.

The code applies this to `Q_zero+eta I` versus `Q_T+eta I`, checks Gaussian-quadrature refinement, and separately estimates TV by Monte Carlo in the likelihood-ratio decision region. All six comparisons are recorded. At response temperature `0.005`, the proxy is about `0.146` for one vector; estimated TV is `0.149 +/- 0.005` (approximate 95% interval). For eight independent vectors, the proxy is `0.551` and estimated TV is `0.459 +/- 0.005`. The discrepancy illustrates why the proxy must not be read as an exact probability.

```sh
python experiments/gram_discrimination.py
# or add --cpu
```

The likelihood calculation uses independent Gaussian draws from each stated model. It does not establish that an experimental field actually follows either Gaussian model. The statistical comparison assesses distinguishability, while the rational algebra check assesses the polynomial identity. [Recorded results](../results/gram-discrimination/report.json).
