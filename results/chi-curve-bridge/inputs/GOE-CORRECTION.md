# Correction of the appendix density formula

## 1. Setup

Let $m\geq 1$, and let $X$ and $Y$ be independent with

```math
X\sim\chi_1,
\qquad
Y\sim\chi_{2m}.
```

Define

```math
R_m=(X^4+2X^2Y^2)^{1/4}.
```

The densities of the two chi variables are

```math
f_X(s)=\sqrt{\frac{2}{\pi}}e^{-s^2/2},
\qquad s>0,
```

and

```math
f_Y(y)=
\frac{2^{1-m}}{\Gamma(m)}
y^{2m-1}e^{-y^2/2},
\qquad y>0.
```

## 2. Conditional distribution

Fix $t>0$. Conditional on $X=s$, the event $R_m\leq t$ is

```math
s^4+2s^2Y^2\leq t^4.
```

It is empty for $s\gt t$. For $0\lt s\lt t$, it is equivalent to

```math
Y\leq
g_t(s):=
\sqrt{\frac12\left(\frac{t^4}{s^2}-s^2\right)}.
```

Consequently,

```math
\Pr(R_m\leq t)
=
\int_0^t f_X(s)F_Y(g_t(s))\,\mathrm{d}s.
```

At the moving endpoint $s=t$, we have $g_t(t)=0$ and hence
$F_Y(g_t(t))=0$. There is therefore no boundary contribution when
the expression is differentiated with respect to $t$.

## 3. Density by change of variables

Direct calculation gives

```math
\frac{\partial g_t(s)}{\partial t}
=
\frac{t^3}{s^2g_t(s)}.
```

To avoid any unspoken interchange of a derivative and an integral, apply the
two-dimensional change-of-variables theorem directly. On the positive
quadrant, use

```math
(s,y)
\longmapsto
\left(s,t=(s^4+2s^2y^2)^{1/4}\right).
```

This is a smooth bijection from $s\gt0$, $y\gt0$ onto $0\lt s\lt t$.
Its inverse is $(s,t)\mapsto(s,g_t(s))$, and the absolute Jacobian of
the inverse is

```math
\left|\frac{\partial g_t(s)}{\partial t}\right|
=
\frac{t^3}{s^2g_t(s)}.
```

The joint density of $(X,R_m)$ is therefore

```math
f_{X,R_m}(s,t)
=
f_X(s)f_Y(g_t(s))
\frac{t^3}{s^2g_t(s)}
\qquad (0\lt s\lt t).
```

Integrating out $s$ and substituting the two chi densities gives

```math
f_{R_m}(t)
\;=\;
\frac{2^{\,2-m}t^3}{\Gamma(m)\sqrt{2\pi}}
\int_0^t
g_t(s)^{\,2m-2}
\frac{\exp\!\left(-\frac{s^2+g_t(s)^2}{2}\right)}{s^2}
\,\mathrm{d}s.
```

This proves the corrected formula.

For completeness, differentiating the conditional CDF in Section 2 gives the
same calculation and is also legitimate. Locally uniformly for $t$ in a
compact subinterval of $(0,\infty)$, its derivative integrand is

```math
O\!\left((t-s)^{m-1}\right)
\quad\text{as }s\uparrow t
```

and

```math
O\!\left(s^{-2m}e^{-c/s^2}\right)
\quad\text{as }s\downarrow0
```

for some $c\gt0$. Both bounds are integrable. The moving-endpoint term is
zero because $F_Y(g_t(t))=F_Y(0)=0$. Thus dominated differentiation gives
the same density, but it is not needed for the proof above.

## 4. What changes from the 2016 typesetting

Equation (2) in the report displays

- the prefactor $2^{1-m}/\sqrt{2\pi}$,
- the power $g_t(s)^{m-2}$, and
- the exponential $e^{-g_t(s)/2}$.

The calculation above gives, respectively,

- $2^{2-m}/\sqrt{2\pi}$, because the $\chi_1$ density contributes
  $2/\sqrt{2\pi}$,
- $g_t(s)^{2m-2}$, because the $\chi_{2m}$ density contributes
  $g_t(s)^{2m-1}$ and the derivative contributes $g_t(s)^{-1}$, and
- $e^{-g_t(s)^2/2}$, because substituting $y=g_t(s)$ in the
  $\chi_{2m}$ density's Gaussian factor $e^{-y^2/2}$ retains the square.

These are corrections to the final typeset expression. The report's central
conditioning idea remains the proof. The density formula and verification
code in this repository already use the squared exponential; this addition
completes the list of changes from the printed report.

## 5. Independent radial-angular check

There is a second way to organize the same distribution. Put

```math
U=X^2,\qquad V=Y^2.
```

Then $U$ and $V$ are independent gamma variables with the same scale:

```math
U\sim\mathrm{Gamma}\left(\frac{1}{2},2\right),
\qquad
V\sim\mathrm{Gamma}(m,2).
```

The beta-gamma decomposition gives independent variables

```math
S=U+V\sim\chi^2_{2m+1},
\qquad
B=\frac{U}{U+V}
\sim\mathrm{Beta}\left(\frac{1}{2},m\right).
```

Since

```math
R_m^4=U^2+2UV=S^2B(2-B),
```

we obtain the exact factorization

```math
\boxed{
R_m=\chi_{2m+1}[B(2-B)]^{1/4},
}
```

where the two factors on the right are independent. This supplies an
independent normalization check and isolates the directional dependence of
the exceptional determinant factor.

## 6. Priority and scope

Bornemann and La Croix identify the exceptional determinant factor and give
its hypergeometric Mellin transform. They state that the corresponding inverse
Mellin transform cannot readily be written down. The 2016 report instead
derives a one-dimensional density integral by conditioning on $\chi_1$.

Accordingly, the defensible claim is narrow:

> The direct conditional-density derivation appears original to the 2016
> report relative to its principal GOE source.

This repository does not claim an exhaustive global priority search, a new
GOE factorization, or a new random-matrix universality theorem.
