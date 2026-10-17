# Higher unfolding terms and denominator guesses

**Result:** the previously invisible $Y_0$ direction becomes nontrivial at higher order. On the selected $Y_0$ target surface, the actual evaluation map has two local critical-value branches whose difference begins in degree three. This supplies explicit cubic and sextic denominator guesses. The $X_0$ direction remains a negative result at the tested precision: its centered height is zero through degree twelve and its centered linear coefficient is zero through degree eleven. These finite-order vanishings do not prove exact vanishing.

This continues the [order-four unfolding](cyclic-fano-unfolding.md) for the fixed `cyclic-triple-fano` target. The original $(F,q,A)$, with $q=1$, is unchanged. The quotient coordinates are $(X_0,X_1,Z,Y_0,Y_1,Y_2)$, where $Z=X_2^3$. The calculations take place near the swapped curve through $[0:1:0:i:1:i]$.

## The actual local evaluation graph

For the $Y_0$ calculation the target is

$$
[0:1:z:i+V:1+h:i(1+h)],
$$

with $z$ determined by the fixed hypersurface equation. Put $u=t/s-(1+h)$ and substitute the actual curve

$$
\begin{aligned}
X_0&=bu,& X_1&=1,& Z&=z+ku+lu^2+mu^3,\\
Y_0&=i+V+(i+C)u,& Y_1&=1+h+u,&Y_2&=i(1+h)+Eu.
\end{aligned}
$$

We solve all seven coefficients of $u^0,\ldots,u^6$ simultaneously for $(z,k,l,m,C,E,h)$ as formal functions of $(b,V)$. The constant Jacobian determinant is $-135000/2401$, so the formal and analytic implicit-function theorems apply. Substitution checks every physical coefficient through degree eight. The resulting $h=H(b,V)$ is therefore a jet of the actual evaluation map, rather than a chosen replacement polynomial.

There are no terms of total degree less than three, and the leading cubic is particularly small:

$$
H_3(b,V)=\alpha b^3+d b^2V+e bV^2,
\qquad
\alpha=\frac56+\frac{8i}{35},\quad
d=\frac5{21}+\frac i2,\quad
e=\frac{5i}{42}.
$$

The inflection center $b=s(V)$ is defined by $H_{bb}(s(V),V)=0$. Its linear term is $-dV/(3\alpha)$. Translating to $x=b-s(V)$ gives the leading centered cubic

$$
\alpha x^3+\lambda_2 V^2x+\mu_3V^3,
$$

where

$$
\lambda_2=e-\frac{d^2}{3\alpha}
=\frac{28225}{592722}+\frac{4955i}{461006}\ne0,
$$

$$
\mu_3=-\frac{de}{3\alpha}+\frac{2d^3}{27\alpha^2}
=\frac{3866303375}{1229617792494}
-\frac{341757500i}{29276614107}.
$$

This resolves part of the negative first-order result. The $Y_0$ direction has zero first-order class in $T^1$, but it introduces a nonzero $V^2x$ term at the next relevant order. The family still fails the first-order versality test; no miniversal unfolding is claimed.

## A local branch statement, with its limits

Substitute $b=Vt$ into $H_b$ and divide by $V^2$. At $V=0$ the resulting quadratic has two distinct roots because $\lambda_2\ne0$. The analytic implicit-function theorem gives two exact local critical branches with distinct tangent directions. Their images have the form

$$
h=c_+V^3+O(V^4),\qquad h=c_-V^3+O(V^4),
$$

where

$$
(c_\pm-\mu_3)^2+\gamma=0,
\qquad \gamma=\frac{4\lambda_2^3}{27\alpha}\ne0.
$$

Thus the two critical-value branches have **contact order three**. Their leading weighted equation is

$$
(h-\mu_3V^3)^2+\gamma V^6=0,
\qquad \mathrm{wt}(V)=1,\quad\mathrm{wt}(h)=3.
$$

The producer verifies this polynomial directly against the discriminant of $H_3(b,V)-h$. It is not the discriminant of the complete evaluation map. Higher terms remain, and the result concerns the specified local target surface. It does not identify a global branch divisor or a supporting divisor for the Hodge certificate.

## Three homogeneous candidates

The preceding full first-order calculation supplies the target covector $h-iW$, where the general target has $Y_2/X_1=i(1+h)+W$. Hence its homogeneous representative is

$$
T=-iY_2-X_1,
\qquad V_h=Y_0-iX_1.
$$

Using $T/X_1=h$ on the tested surface, the exported guesses are

$$
D_1=T,\qquad
D_3=TX_1^2-\mu_3V_h^3,\qquad
D_6=D_3^2+\gamma V_h^6.
$$

They have weighted degrees one, three and six, respectively, over $\mathbb Q(i)$. All coefficients and their homogeneous monomials are in [candidates.json](../results/cyclic-fano-higher-unfolding/candidates.json). Restriction to the actual target surface is checked exactly. Extending these expressions away from that surface is a choice; local contact does not make any candidate a valid denominator. The separate complete fixed-denominator equations must decide that question. No rational norm is silently substituted, and no higher-degree family is claimed covered.

The subsequent [complete fixed-denominator tests](cyclic-fano-guided-denominators.md)
reject all three guesses, three rational tangent-norm powers, and three
Jacobian-multiplied repairs. The local branch statement survives these
failures; it has not supplied a certificate denominator.

![Actual higher-order map data, leading local branches and denominator tests](../results/cyclic-fano-higher-unfolding-figures/cyclic-fano-higher-unfolding.png)

The branch curves in the figure show their checked leading jets. They are not numerical solutions of the complete global branch equations. Exact denominator-test outcomes are a separate panel.

## The retained negative direction and precision

The $X_0$ comparison instead moves the target to $[U:1:z:i:1+h:i(1+h)]$. It was first tested through degree eight and then through degree twelve. Its centered height vanishes through degree twelve and its centered linear coefficient through degree eleven. The test found no nonzero correction at those orders, so it contributes a failed direction rather than another invented candidate.

For a graph known through degree $n$, the inflection center is known through $n-2$, the centered height through $n$, the centered linear coefficient through $n-1$, and the centered cubic coefficient through $n-3$. The stronger height and linear bounds use the fact that $H$ begins in degree three and $H_{bb}$ vanishes at the exact center. Packets export these precisions explicitly; terms beyond them are discarded.

## Reproduction and failures

```sh
python experiments/cyclic_fano_higher_unfolding.py run --axis X0 --order 12
python experiments/cyclic_fano_higher_unfolding.py run --axis Y0 --order 8
python experiments/cyclic_fano_higher_unfolding.py verify --axis X0 --order 12
python experiments/cyclic_fano_higher_unfolding.py verify --axis Y0 --order 8
python experiments/cyclic_fano_higher_unfolding.py candidates
python experiments/cyclic_fano_higher_unfolding.py verify-candidates
python -S experiments/check_cyclic_fano_higher_unfolding.py
python experiments/plot_cyclic_fano_higher_unfolding.py
```

The producer reuses the frozen sparse Gaussian-rational arithmetic from the prior unfolding script and records that dependency's hash. Each search worker has a 120-second wall-clock bound. Final arithmetic took about 3.7 seconds for $X_0$ degree twelve and 0.7 seconds for $Y_0$ degree eight. Both primary verification runs and the candidate reconstruction passed. The independent standard-library checker verifies the physical jets from the frozen source, the leading discriminant, all three homogeneous restrictions, and nine mutation controls. A preliminary symbolic comparison failed because a complex expansion introduced real/imaginary-part wrappers around polynomial variables; the corrected comparison uses polynomial arithmetic over $\mathbb Q(i)$. Its failure log is retained. No incidence identity failed and no search timed out. The unqualified `unfolding-order8.json` and `attempt-order8.json` preserve the first exploratory $X_0$ run; the final verification chain uses the axis-qualified packets and their declared precision limits.

Credit: the upstream rational-curve support framework, the preceding exact cyclic Fano fiber and unfolding calculations, and standard implicit-function, discriminant and local branch arguments. OpenAI Codex assisted construction and independent review. The work supplies local geometry and testable guesses, not a global support theorem, a certificate, a Lean proof, or an accepted solution. The local evaluation branches have not been identified with the separate order-three deck symmetry of the original sextic.
