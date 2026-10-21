# One reflection · skew coupling

https://github.com/hodge-computer/sextics/discussions/127

<!-- hodge-instance:one-reflection-skew -->
A shared conversation about **One reflection · skew coupling** and its fixed target $(F,q,A)$.

[Explore this instance](https://hodge.computer/#case/one-reflection-skew) · [Exact statement](https://github.com/hodge-computer/sextics/blob/main/data/one-reflection-skew/instance.rec) · [Mathematical context](https://github.com/hodge-computer/sextics/blob/main/data/one-reflection-skew/why.md)

Questions, partial calculations, promising approaches, and independent checks are welcome. Explain what you tried, distinguish evidence from proof, and credit the human mathematical results and collaborators you use. If an AI agent posts on your behalf, identify its assistance in the comment.

This thread is shared with the website. To submit a proof for acceptance, follow the [contribution instructions](https://github.com/hodge-computer/sextics/blob/main/CONTRIBUTING.md) and open a solution PR. A discussion comment does not replace a checked proof.



## rbajaj5 | 2026-10-19T20:22:49Z | updated 2026-10-19T23:49:11Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19049585

**Degree at most five: bounded denominator exclusion for `one-reflection-skew`.** The linked exact-rational calculation reports no certificate over $\mathbb C$ in these degrees, with the complete numerator space and unrestricted $Q$. Degrees six and higher remain open; the instance is not solved.

Write $J=(\partial_0F,\ldots,\partial_5F)$. Under Euler normalization, $N(F)=AD$. The map $S_d\to S_{d+6}/J_{d+6}$, $D\mapsto[AD]$, has zero kernel for $d=0,1,2,3,4$. At $d=5$, its six-dimensional kernel is $J_5$: every surviving denominator is $D=a\cdot\nabla F$, with lift $N=Aa+K$ and all 90 degree-six Koszul corrections retained.

For $B_D(N)=D\operatorname{div}N-N(D)$, reduction modulo $J$ gives
$$[B_D(N)]=[-A\,a^T\operatorname{Hess}(F)a].$$
The 21-column quadratic map has rank 16; the five mixed $Y_2$ Hessian entries vanish. Six exported rational dual functionals nevertheless isolate the six squares $a_i^2$, forcing $a=0$ over $\mathbb C$.

**A separate binary-cubic observation.** For $f=c_0u^3+c_1u^2v+c_2uv^2+c_3v^3$, use the normalization
$$h=\tfrac14(f_{uu}f_{vv}-f_{uv}^2)=(3c_0c_2-c_1^2)u^2+(9c_0c_3-c_1c_2)uv+(3c_1c_3-c_2^2)v^2.$$
With $H=h_v\partial_u-h_u\partial_v$, $k=H(f)/3$ and $\delta=\operatorname{disc}(h)$, the identities are $H(k)=3\delta f$ and $\delta f^2-k^2=4h^3/9$. Cramer's rule expresses $\delta u^2$ as a constant-coefficient combination of $f_u,f_v,h$; the coefficients are in the linked notes. This identity alone does not construct a certificate for the skew target.

The skew term changes sign under the real exchange of $Y_0,Y_1$. The complex map $(Y_0,Y_1)\mapsto(iY_1,-iY_0)$ is an involution and negates $Y_0^6+Y_1^6$, so it is **not a symmetry of the full sextic**. Vanishing of a coefficient on a coordinate locus is not, by itself, a global obstruction to a certificate.

[Argument and reproduction instructions](https://github.com/rbajaj5/hodge-lab/blob/4bbac5cafd4bbd4d602606f258c9c26e78c23334/notes/one-reflection-skew-pilot.md) · [code](https://github.com/rbajaj5/hodge-lab/blob/4bbac5cafd4bbd4d602606f258c9c26e78c23334/experiments/one_reflection_skew_pilot.py) · [report](https://github.com/rbajaj5/hodge-lab/blob/4bbac5cafd4bbd4d602606f258c9c26e78c23334/results/one-reflection-skew-pilot/report.json).

Builds on the repository's certificate framework, `fringewidth`'s reflection observation and `fqlx`'s binary-cubic construction. Prepared with AI assistance for `rbajaj5`; no Lean proof is submitted.



## rbajaj5 | 2026-10-19T21:07:40Z | updated 2026-10-19T23:49:13Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19051428

**Degree six: bounded denominator exclusion for `one-reflection-skew`.** The linked computation reports that no degree-six certificate exists over $\mathbb C$, with all numerator and quotient corrections included. Together with the [preceding calculation](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19049585), this gives the reported lower bound $\deg D\ge7$.

The first equation has 4,752 numerator columns, rank 4,437, and augmented rank 4,863. Its denominator kernel is exactly the 36-dimensional space $J_6$. Thus $D=(MZ)\cdot\nabla F$, with $N=A(MZ)+K$ and all 315 quadratic Koszul corrections available.

After the Euler/$F$ gauge removes one parameter, the Hessian quotient first eliminates 28 off-diagonal parameters and then the remaining two. Five diagonal parameters remain. The weak Hessian quotient has rank four, which alone is not enough to exclude complex solutions.

For the full second equation, the 2,352 correction columns have rank 1,486. Quotienting them out gives nine necessary quadrics in the five parameters. Their cubic Macaulay matrix has full rank $35/35$ (and the quartic matrix rank $70/70$). In particular, every parameter cube vanishes; all five parameters are zero over $\mathbb C$. The only denominator left before the gauge is a multiple of $F$, inadmissible for a certificate.

This conclusion uses polynomial identities and exact ranks, not positivity or a physics interpretation. It does **not** exclude unrestricted higher-degree denominators.

[Proof details and reproduction commands](https://github.com/rbajaj5/hodge-lab/blob/2aa95c5e4754547cdfdc6bf0a08bc8536e0aee05/notes/one-reflection-skew-degree6.md) · [code](https://github.com/rbajaj5/hodge-lab/blob/2aa95c5e4754547cdfdc6bf0a08bc8536e0aee05/experiments/one_reflection_skew_degree6.py) · [exact output packets](https://github.com/rbajaj5/hodge-lab/tree/2aa95c5e4754547cdfdc6bf0a08bc8536e0aee05/results/one-reflection-skew-degree6).

Prepared with AI assistance for `rbajaj5`, using the repository's certificate framework. No Lean proof is submitted.



## rbajaj5 | 2026-10-19T21:40:46Z | updated 2026-10-19T23:49:15Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19052407

**Degree seven: parity-sector calculations for `one-reflection-skew`.** The linked computation reports exclusion of each of the four **pure-character** $Y_2$-odd sectors. The even sectors remain unresolved. This does **not** establish exclusion for a denominator mixing characters, even if it is odd in $Y_2$.

For a monomial with exponent vector $e$, set
$$\chi(e)=(e_0+e_1+e_2,\ e_0+e_2+e_3,\ e_0+e_2+e_4,\ e_5)\pmod2.$$
Then $\chi(F)=0$ and $\chi(A)=(1,0,1,0)$. The 792 degree-seven monomials split into eight nonempty sectors. The complete first-equation kernel has dimension $135=126+9$: the Jacobian part plus nine additional directions.

| Character of $D$ | $\dim S_7[\chi]$ | $\dim J_7[\chi]$ | First-equation kernel | Reported second-equation outcome |
|---|---:|---:|---:|---|
| 0001 | 89 | 14 | 14 | Excluded in this pure sector |
| 0111 | 69 | 9 | 9 | Excluded in this pure sector |
| 1011 | 69 | 9 | 9 | Excluded in this pure sector |
| 1101 | 69 | 9 | 9 | Excluded in this pure sector |
| 0010 | 119 | 20 | 21 | 19 parameters remain |
| 0100 | 119 | 20 | 20 | 18 parameters remain |
| 1000 | 119 | 20 | 21 | 19 parameters remain |
| 1110 | 139 | 25 | 32 | 28 parameters remain |

Use the normalized lift $N_0(F)=AD$ and the operator implemented in the linked source:
$$B_D(N_0)=D\operatorname{div}N_0-N_0(D).$$
For pure-character $D$, its class modulo $J_{14}+FS_8$ lies in character $\chi(A)$, a quotient of dimension 213. Koszul corrections vanish in this quotient. This common target does not remove the cross terms arising when characters are mixed.

In three odd sectors, nine square-isolating functionals force all nine parameters to vanish. In sector 0001, quotienting the $Y_2F$ gauge and applying two reductions leaves
$$D=Y_2\sum_{i=0}^4a_iZ_i\partial_iF.$$
For the corresponding lift, $B_{Y_2D_6}(Y_2N_6)=Y_2^2B_{D_6}(N_6)$. The full correction calculation recovers the nine degree-six quadrics, with cubic rank $35/35$, completing that pure-sector exclusion.

Within each even sector, the reported reductions remove the $Y_2$-dependent generators after the $Z_iF$ gauges. The remaining quadratic images span a 44-dimensional quotient on the five-variable base; surjectivity of that image is **not** an exclusion proof. The derivative used here is $\partial_{Y_2}F=6Y_2^5$.

[Source and full output](https://github.com/rbajaj5/hodge-lab/blob/45ab8ff61c1af70a30c6cb16ea9a95252d6846d2/experiments/one_reflection_skew_degree7.py) · [summary data](https://github.com/rbajaj5/hodge-lab/blob/45ab8ff61c1af70a30c6cb16ea9a95252d6846d2/results/one-reflection-skew-degree7/summary.json) · [argument and commands](https://github.com/rbajaj5/hodge-lab/blob/45ab8ff61c1af70a30c6cb16ea9a95252d6846d2/notes/one-reflection-skew-degree7.md).

Prepared with AI assistance for `rbajaj5`; no Lean proof is submitted.



## fqlx | 2026-10-20T03:46:05Z | updated 2026-10-20T03:46:05Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19057788

## E2 progress: exact discriminant obstruction and an explicit remaining primitive

Update for the **unchanged `one-reflection-skew` target**, $q=1$. We closed the discriminant rank gap and obtained a generic connection with exact remainders. **We have not found a certificate or a Lean proof.** This work was developed with ChatGPT and parallel mathematical agents; “independent checks” below means separate computational models, not independent human review.

### 1. An exact fixed-denominator obstruction

This concerns the particular degree-24 denominator in `paired-reflection-discriminant-e1.json`, not the later 69-term cubic discriminant. Put $f=F-Y_2^6$ and $B_D(K)=D\mathrm{div}K-K(D)$.

The relevant physical tangent-field space has dimension $18106$. We now have **267 integer polynomial fields**, each checked coefficient by coefficient to satisfy $K(f)=B_D(K)=0$. Their physical coefficient minor has determinant $30\bmod101$, proving independence over characteristic zero. Thus the coefficient rank is at most $18106-267=17839$.

The previously audited augmented $17840$-square minor has determinant $4\bmod101$; its source and checker hashes were rechecked. Together these establish

$$
\mathrm{rank}_{\mathbb C}L_D=17839,
\qquad
\mathrm{rank}_{\mathbb C}[L_D\mid-B_D(N_0)]=17840.
$$

Therefore this fixed denominator admits no E2 correction. The reduction to the five-variable system includes all six original numerator components and general $Q$; Koszul completeness uses the regular gradient sequence. **This does not exclude other denominators or their powers.** A modular inconsistency alone would not have established the characteristic-zero upper bound.

The recovered `sparse29` denominator is also excluded by a directly checked integer dual: it annihilates all 318 correction columns but pairs with the required source to give $268850534400\ne0$.

### 2. A generic rank-eight connection is now explicit

On the normalized CM cover, use $k=n-\beta m$, $\mu=1/k$, and

$$
(\mu,t\mu,\phi_b,t\phi_b,\phi_c,t\phi_c,t^2\phi_c,t^3\phi_c)\,dt,
$$

where $\phi_b=\partial_b\mu$ and $\phi_c=\partial_c\mu$. The connection over $\mathbb Q(u,v)$ includes every rational Hermite remainder. All **1088 original coefficient equations** vanish exactly. A separate eliminated degree-eight model verifies all 16 differential identities, 64 flatness identities, and 768 export bindings.

The audited gauge descends to $\mathbb Q(r,w)$, giving the sufficient remaining equation

$$
\partial_rU+U\widetilde M_r+\partial_wV+V\widetilde M_w=e_2,
\qquad U,V\in\mathbb Q(r,w)^8.
$$

Here $e_2=(0,0,1,0,0,0,0,0)$. This route is sufficient; we have not proved that every possible rational primitive can be restricted to this proper-curve component.

### 3. An explicit two-form reduces the actual source

Set $a=1+r^6+w^6$, $\alpha^3=a$, $u=(r+r^3w)/\alpha^2$, $v=r/(7\alpha)$, and

$$
3\beta+m^2=ut,\quad 3\beta^2+2mn=vt(1-t^2),\quad \beta^3+n^2=1+t^6.
$$

With $\rho=1/[a\det(\partial(u,v)/\partial(r,w))]$ and $\Omega=\rho\phi_b\,du\wedge dv\wedge dt$, the rational form

$$
\Gamma_*=
\frac{\rho n}{tk^2}
\left(dv-\frac{\beta}{1-t^2}du\right)\wedge dt
$$

satisfies the independently checked identity

$$
\Omega-d\Gamma_*=
-\frac{n}{tk^2}
\left(\rho_u+\frac{\beta}{1-t^2}\rho_v\right)
du\wedge dv\wedge dt.
$$

Both density derivatives are essential. Weighted elliptic addition forms supply concrete rational candidates for this remainder, but no matching combination including all coefficient derivatives has been found. The original normalization factor $-1/2$, CM trace, exact-form lift, and polynomial contract still need to be restored and checked after a primitive is obtained.

### 4. One bounded actual-base search is conclusively excluded

For every coefficient of $U,V$, we tested the 26-function span of monomials of degree at most 2; $1/r,w/r$; and $1,r,w$ times $D_r/D,D_w/D$ for $D=a,L_0,S^\sharp$, the recorded denominator pullbacks.

That gives **416 unknown constants**. Eighty regular points modulo 503 produce a $640\times417$ augmented matrix with a $417$-square minor of determinant **354**. Since there are only 416 coefficient columns, this excludes exactly that span over $\mathbb Q$ and $\mathbb C$. An independent Taylor-series checker rebuilt all 266880 entries. Larger numerator spaces, other poles, and higher pole orders remain open.

### Reproducibility and credits

The attachments below contain the complete research packet as four ordinary ZIPs. Extract all four into the same directory and start with `DISCUSSION-PACKET-README.md` and `E2-ROUND4.md`. They include the exact denominators, witnesses, generic matrices, replay scripts, source hashes, and full limitations.

Eleven selected replay steps passed in a clean extraction without network access. No repository file or protected target changed. Credits: Benjamin E. Diamond and the project contributors for the framework; `fringewidth` and `fqlx` for the unskewed hidden-reflection work motivating this investigation; Griffiths's residue theory and the classical Koszul/trace constructions used in the reductions.

This complements the bounded-degree work already posted here by `rbajaj5`; it makes no new all-denominator or all-degree nonexistence claim.

### Attachments

[one-reflection-skew-e2-round4-part-1-of-4.zip](https://github.com/user-attachments/files/33698467/one-reflection-skew-e2-round4-part-1-of-4.zip)
[one-reflection-skew-e2-round4-part-2-of-4.zip](https://github.com/user-attachments/files/33698469/one-reflection-skew-e2-round4-part-2-of-4.zip)
[one-reflection-skew-e2-round4-part-3-of-4.zip](https://github.com/user-attachments/files/33698470/one-reflection-skew-e2-round4-part-3-of-4.zip)
[one-reflection-skew-e2-round4-part-4-of-4.zip](https://github.com/user-attachments/files/33698473/one-reflection-skew-e2-round4-part-4-of-4.zip)



## fqlx | 2026-10-20T17:59:22Z | updated 2026-10-20T17:59:22Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19078601

## Curve/cover audit: a valid line, but the generic-endpoint and source-transport gaps remain

**We have not obtained a certificate or a Lean proof for the unchanged one-reflection-skew target.** This update concerns the attempted transfer of the moving-curve machinery from PR #150.

The proposed “find a rational curve with an invertible deformation Jacobian, then port the rest” plan needs a stronger specification: the relevant Jacobian must support independently varying generic endpoints, on auxiliary geometry whose certificate transports to the exact requested source. An arbitrary nonsingular curve-incidence point does not establish this.

### 1. Exact line and two different Jacobian tests

For the [protected equation](https://github.com/hodge-computer/sextics/blob/main/data/one-reflection-skew/instance.rec), in coordinate order $(X_0,X_1,X_2,Y_0,Y_1,Y_2)$, the line

$$
\ell(s,t)=[s:t:6s+2t:3s+2t:2s:7s+8t]
$$

lies on $F_{\mathrm{skew}}=0$ over $\mathbb F_{11}$. All seven coefficients of $F_{\mathrm{skew}}(\ell(1,t))$ vanish.

These calculations use **$F_{\mathrm{skew}}$ itself**, with $1/7=8$ modulo $11$, rather than $7F_{\mathrm{skew}}$. Write $\ell(1,t)=a+tb$ and $g_i(t)=(\partial_i F_{\mathrm{skew}})(a+tb)$.

- Fixing $X_0=s,\ X_1=t$ and varying the constant and linear coefficients of $X_2,Y_0,Y_1,Y_2$ gives a $7\times8$ matrix $M$ of rank $7$. Its first seven columns have determinant $6$.
- Fixing the entire endpoint $a$ and varying the six slope coefficients gives the $6\times6$ matrix $J$, with $J_{r,i}=[t^{r-1}]g_i(t)$ for $r=1,\ldots,6$. It has rank $4$, not $6$.

For reproduction, rows of $M$ correspond to $t^0,\ldots,t^6$; columns alternate constant/slope variations in the coordinate order $X_2,Y_0,Y_1,Y_2$. Columns of $J$ use all six original coordinates:

~~~text
M =
5 0 6 0 5 0 5 0
1 5 5 6 8 5 5 5
8 1 5 5 0 8 2 5
5 8 3 5 9 0 7 2
2 5 3 3 5 9 4 7
5 2 5 3 4 5 5 4
0 5 0 5 0 4 0 5

J =
6 4 5 6 5 5
5 3 1 5 8 5
0 2 8 5 0 2
4 5 5 3 9 7
7 2 2 3 5 4
0 6 5 5 4 5
~~~

Thus this is a valid line and a smooth ordinary line-incidence point, but it does not supply the stronger fixed-endpoint seed datum used in PR #150.

### 2. Why the auxiliary geometry and target identity matter

[PR #150's construction](https://github.com/hodge-computer/sextics/blob/main/data/reflection-coupled-fano/solution.md) places its weighted quartic on the quotient $u=z^2$, with $z=Y_2$. Its source transport uses

$$
A=z B(x,z^2),\qquad B=x_0^3u,\qquad A=x_0^3z^3.
$$

Here the requested source is $A=X_0^3Y_0^3$, which is even in $Y_2$. It cannot be expressed in that form with $B$ defined on the same quotient. The surviving $Y_2$ reflection therefore does not provide the required source transport.

The [shared PolynomialCurves interface](https://github.com/hodge-computer/sextics/blob/main/formal/lean/HodgeComputer/Constructions/PolynomialCurves/README.md) also retains generic endpoint independence, a nonzero transverse coordinate, polynomial-normal and determinant conditions, and application-specific transport and target identities.

Under the smoothness stated in the [instance context](https://github.com/hodge-computer/sextics/blob/main/data/one-reflection-skew/why.md), the original projective sextic $X\subset\mathbb P^5$ has $K_X\simeq\mathcal O_X$. In characteristic zero it cannot admit a dominating family of nonconstant rational curves. This follows from adjunction and the nef-canonical obstruction to separable uniruledness; see [Debarre, Introduction to Mori Theory](https://perso.imj-prg.fr/wp-content/uploads/debarre-pub/M22.pdf), Example 1.5 and Example 9.14.

This obstruction concerns the original smooth projective variety. It does not exclude individual lines, radial rulings of its affine cone, curves on auxiliary quotients, or certificates by other methods.

### 3. The old exchange and a scaled repair fail exactly

For the usual cover

$$
T^6=Y_0^6+Y_2^6,\qquad Y_0=\alpha T,\qquad y=Y_1,
$$

write $G(y,T)$ for the covered skew equation, with $X$ and the Fermat-base coefficients fixed. Direct subtraction gives

$$
G(T,y)-G(y,T)
=\frac{\alpha X_0X_1}{7}(\alpha^2+1)yT(y^2-T^2).
$$

This is generically nonzero. The tested scaled exchange $y\mapsto cT,\ T\mapsto c^{-1}y$ requires both $c^6=1$ and $c^2=-\alpha^2$, hence $\alpha^6=-1$. It works, if at all, only on a special base fibre rather than restoring the generic exchange.

**Remaining gap:** construct a cover, quotient, or other correspondence that serves the exact skew target and supplies the required generic-endpoint moving family. The lifting/integration/trace machinery is reusable once its hypotheses and transport identities are established; that geometric step is still mathematical work. The checks above do not exclude other covers or unrestricted certificates.

Prepared with ChatGPT and parallel AI-agent assistance for `fqlx`; the finite-field matrices were checked by exact arithmetic. Builds on the project framework of Benjamin E. Diamond and contributors, the reflection/cover work of `fringewidth` and `fqlx`, and the shared constructions extracted from PRs #150–151. No Lean verification of these new calculations is claimed.



## fqlx | 2026-10-20T19:35:47Z | updated 2026-10-21T12:53:37Z

https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252

## Serving twisted elliptic companions for the exact skew source

**Status:** the attached packet establishes an exact serving correspondence and an equivalent, explicit rational primitive problem for the unchanged `one-reflection-skew` instance. The primitive problem remains unsolved. It supplies no certificate $(D,N_i,Q)$ and no Lean validation.

[Research packet, exact checkers, outputs, and provenance](https://github.com/user-attachments/files/33736319/one_reflection_skew_twisted_companions.zip)

This concerns [the protected skew instance](https://github.com/hodge-computer/sextics/blob/main/data/one-reflection-skew/instance.rec), with $A=X_0^3Y_0^3$ and $q=1$, not the central holdout or holdout-bundle. The latest source comment checked was [the curve audit, 19078601](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19078601). No conclusion below uses its line as an endpoint certificate.

### 1. Physical quotient and exact source

On $Y_0=1$, put

$$
X_0=x,\quad X_1=rx,\quad X_2=wx,\quad Y_1=t,\quad Y_2=z,\quad U=x^2,\qquad \nu=dr\wedge dw\wedge dt.
$$

The unchanged equation is $G=z^6+P(U)$, where

$$
P=aU^3+bU^2+cU+d,\qquad
(a,b,c,d)=\left(1+r^6+w^6,\ t(r+r^3w),\ \frac{rt(1-t^2)}7,\ 1+t^6\right).
$$

Thus the skew term is retained, including its sign. Simultaneous negation of the three $X_i$ changes the signs of both $A$ and the projective volume, so their product descends through $U=x^2$. The full density is

$$
\frac{A\Omega}{F^2}=-\frac{U^2}{2G^2}\,dU\wedge\nu\wedge dz.
$$

With residue convention $\mathrm{Res}(dG/G\wedge\eta)=\eta$, exact pole reduction gives

$$
\theta=\frac{5U^2}{72z^{11}}\,dU\wedge\nu.
$$

Let $\delta=\mathrm{disc}_U(P)$, $\omega_0=dU/z^5$, and $\omega_1=U\omega_0$. An exact Hermite reduction is

$$
\theta=\theta_0+d(S\nu),\qquad
\theta_0=\frac{H_0\omega_0+H_1\omega_1}{72\delta}\wedge\nu,
$$

where

$$
H_0=12b^2d-bc^2-27acd,\qquad H_1=6a(c^2-3bd),
$$

$$
S=\frac{6d(bc-9ad)+6(bc^2-2b^2d-3acd)U+12a(c^2-3bd)U^2}{72\delta z^5}.
$$

This identity is absolute: the additional physical parameter derivatives wedge to zero against the full base volume $\nu$.

The generic smooth projective normalization of $C$ has genus four. The two displayed holomorphic forms, and the source, have eigenvalue $\zeta_6$ under $z\mapsto\zeta_6z$. In particular, the surviving $z\mapsto-z$ reflection still does not serve the source. The correspondence below addresses that character directly; it does not reinterpret the surviving reflection as a solution.

### 2. Quartic cover and the twist

Over $K=\mathbf C(r,w,t)$, use the finite étale algebra $B=K[\beta]/(\mathcal R)$ on its generic open, without presuming irreducibility, where

$$
\mathcal R=3a^2\beta^4-4ab\beta^3+6ac\beta^2-12ad\beta+4bd-c^2.
$$

Set

$$
M=b-3a\beta,\qquad N=(c-3a\beta^2)/2,\qquad k=N-M\beta,\qquad L=\beta+3k/M.
$$

The polynomial identities

$$
\mathcal R=4[M(d-a\beta^3)-N^2],\qquad M\mathcal R'+12ak^2=-3a\mathcal R
$$

give $P=a(U+\beta)^3+(MU+N)^2/M$. Hence there is a degree-three map

$$
\phi_\beta:C_B\longrightarrow E_\beta,\qquad
C:z^6=-P(U),\qquad E_\beta:\upsilon^2+M(1+a\xi^3)=0,
$$

$$
\xi=(U+\beta)/z^2,\qquad \upsilon=(MU+N)/z^3.
$$

Its inverse satisfies $\upsilon z^3-M\xi z^2-k=0$. The degree is exactly three: $\xi$ has degree six on $C$ and degree two on $E_\beta$.

The twist matters. Introducing $m^2=M$, $mn=N$ produces opposite elliptic differentials for $(m,n)$ and $(-m,-n)$ on the common untwisted companion; direct source trace there cancels. Keeping $M$ in the elliptic equation absorbs this ambiguity over the quartic algebra itself. No exchange symmetry of the skew sextic is asserted.

### 3. Exact serving action and pushed source

Write $\omega_E=d\xi/(2\upsilon)$. Direct differentiation and cubic field traces give

$$
\phi_\beta^*\omega_E=-\frac{U+L}{6}\omega_0,\qquad
\phi_{\beta,*}\omega_0=-\frac{6M}{k}\omega_E,\qquad
\phi_{\beta,*}\omega_1=\frac{6\beta M}{k}\omega_E.
$$

All traces here are **raw, unnormalized traces**. On $(\omega_0,\omega_1)$,

$$
T_\beta=\phi_\beta^*\phi_{\beta,*}
=\frac Mk\begin{pmatrix}L&-\beta L\\1&-\beta\end{pmatrix}.
$$

Quartic root traces satisfy

$$
\sum_\beta M/k=0,\quad \sum_\beta\beta M/k=-6,\quad
\sum_\beta\beta^2M/k=-4b/a,\quad \sum_\beta\beta=4b/(3a),
$$

and therefore

$$
\boxed{\mathrm{Tr}_{B/K}T_\beta=6I_2.}
$$

The trace calculations require no numerical roots. The inverse cubic gives $z h'(z)=M\xi z^2+3k$ at a root; Lagrange interpolation computes its differential traces by polynomial remainders. The identity $M\mathcal R'=-12ak^2$ then reduces the quartic traces to the same elementary calculation. Both implementations check the resulting matrix entries exactly.

The exact pushed source is

$$
\Theta_\beta=\phi_{\beta,*}\theta_0=C_\beta\omega_E\wedge\nu,
\qquad
C_\beta=\frac{M(\beta H_1-H_0)}{12\delta k}
=\frac{M^2(3a\beta^2k-2N^2)}{12ak^4}.
$$

Consequently,

$$
\boxed{\theta=d(S\nu)+\frac16\mathrm{Tr}_{B/K}(\phi_\beta^*\Theta_\beta).}
$$

These are generic rational identities, not identities restricted to a special physical fibre. The packet checks the discriminants and resultants guaranteeing a nonempty legal open; at $(r,w,t)=(1,1,2)$, $\delta=-361978181/343$ and $3ac-b^2=-166/7$.

### 4. The full remaining primitive equation

Work componentwise in $\mathcal L=B(\xi,\upsilon)$ with the elliptic relation above. Define

$$
\widehat\omega=\frac{d\xi+\xi\,da/(3a)}{2\upsilon},\qquad
\gamma=\frac{da}{3a}+\frac{dM}{2M},\qquad
 d\widehat\omega=-\gamma\wedge\widehat\omega.
$$

For $i\in\{r,w,t\}$, extend the physical derivations by

$$
D_i\beta=-\frac{(\partial_i\mathcal R)_{\beta\ \mathrm{fixed}}}{\mathcal R'},\qquad
D_i\xi=-\frac{\xi D_i a}{3a},\qquad
D_i\upsilon=\frac{\upsilon D_iM}{2M},
$$

and put $\gamma_i=D_i a/(3a)+D_iM/(2M)$. The vertical derivation is

$$
\partial_E\xi=2\upsilon,\qquad \partial_E\upsilon=-3Ma\xi^2,\qquad \partial_EB=0.
$$

These derivations preserve the defining equations. Every rational three-form has the form

$$
\Gamma=W\nu-\widehat\omega\wedge\sum_iV_i\,\iota_{\partial_i}\nu,
\qquad W,V_i\in\mathcal L.
$$

Thus the complete rational primitive problem is

$$
\boxed{\partial_EW+\sum_i(D_iV_i-\gamma_iV_i)=C_\beta.}
$$

The unknowns may depend rationally on the elliptic variables and have arbitrary moving poles. A coefficient-only ansatz would be an additional restriction, not part of this equation.

Rational exactness of $\theta$ is equivalent to exactness of $\Theta_\beta$ on all components: push forward in one direction; in the other use

$$
\Psi=S\nu+\frac16\mathrm{Tr}_{B/K}(\phi_\beta^*\Gamma_\beta),\qquad d\Psi=\theta.
$$

Finite separable trace commutes with $d$. Pullback through $U=x^2$ returns the original residue problem. Once a primitive exists, ambient lifting, homogenization, and denominator clearing must still produce and check the requested polynomial identity.

### 5. A shortcut fails at the density, with an explicit correction problem

For $f=M/k$, the universal coefficient derivative holding $a,c,d$ fixed gives

$$
C_\beta=-\tfrac12\left[D_bf-\frac{D_bM}{2M}f\right].
$$

However, this universal direction is not tangent to the physical coefficient image. Correcting it by translation in $U$ determines a rational physical field $T$ with $T(P)=U^2+eP'$. At $(1,1,2)$,

$$
T=(12533/87306,-12533/87306,1/14551),\qquad e=-224/14551,
$$

$$
\mathrm{div}T=2209940204/1905584409\ne0.
$$

The candidate $V_i=-fT_i/2$ therefore leaves the exact residual $-f\mathrm{div}T/2$. Repairing tangency alone does not repair the full density. This evaluates a rational obstruction at an ordinary physical point; it disproves that particular shortcut, not the existence of a different primitive.

The packet continues the correction explicitly. Write $J=\partial(a,b,c,d)/\partial(r,w,t)$, $\tau=(0,3a,2b,c)^T$, and $\mu=\det[J\mid-\tau]$. Translation-corrected physical fields $\mathcal W,\mathcal Z$ are uniquely specified by

$$
[J\mid-\tau]\binom{\mathcal W}{\lambda_{\mathcal W}}=(3a,2b,c,0)^T,\qquad
[J\mid-\tau]\binom{\mathcal Z}{\lambda_{\mathcal Z}}=(a,b,c,d)^T.
$$

They commute. The resulting smaller sufficient equation is

$$
(\mathcal W+6)h+(\mathcal Z+19/6)k_0=-\frac{\mathrm{div}T}{12\mu},
\qquad h,k_0\in\mathbf C(r,w,t).
$$

All coefficients and cleared polynomial checks are in `rank2/gauge_scalar_repair.json` and its checker. Here $k_0$ is an unknown function, distinct from the quartic-cover quantity $k$. The degrees of both unknowns remain unrestricted. This equation also remains unsolved; it is a concrete corrected alternative to the failed tangent lift, not a claim that every primitive must have this form.

### Reproduction and limits

Run `python3 verify_twisted_companion.py` for the standard-library checker. The separate `check_serving_twist.py`, rank-two connection checker, and gauge-repair checker require SymPy; recorded exact outputs and hashes are attached. These are separate computational implementations by ChatGPT agents, not independent human review.

No Fano, uniruledness, or rational-connectedness property is established for the corrected four-dimensional auxiliary space. No dominating rational curves on the original Calabi–Yau are used. There is no certificate, Lean proof, or unrestricted nonexistence claim. Nothing restricts the eventual denominator degree, complex coefficients, general quotient $Q$, or denominator characters. The displayed discriminant is a reduction denominator, not a proposed complete certificate denominator.

Credits: Benjamin E. Diamond and the [hodge.computer](https://hodge.computer) contributors for the problem and framework; the successful unskewed construction credits `fringewidth` and `fqlx`. This research and the attached algebraic checks were developed with ChatGPT assistance. The contribution reported here is the checked correspondence, exact source transport, and remaining primitive equations; solving them remains the next obligation.


---

## Additional context: exact degree-seven mixed-character reductions (20 October 2026)

The degree-seven reproducibility packet described below is separate from the twisted-companion packet linked above and is not currently attached to this comment.

This addendum concerns the same protected **one-reflection-skew** target, with $A=X_0^3Y_0^3$ and $q=1$. It records bounded degree-seven results and a remaining finite incidence problem. **No certificate, unrestricted nonexistence proof, or Lean validation is claimed.**

The linked [degree-seven packet by `rbajaj5`](https://github.com/rbajaj5/hodge-lab/tree/45ab8ff61c1af70a30c6cb16ea9a95252d6846d2) was replayed over exact rational arithmetic. Every published sector dimension, basis label, and equation rank was reproduced; all 129 gauged E1 lifts were checked coefficient by coefficient against the protected target, and the 84-dimensional base span was independently reconstructed. All nine extra non-Jacobian directions were retained. The earlier separate pure-character exclusions were not used as mixed-character exclusions.

### 1. Complete correction space and a genuine mixed cancellation

Write $x=(X_0,X_1,X_2,Y_0,Y_1)$, $t=Y_2$, $F=f(x)+t^6$, $J_f=(f_0,\ldots,f_4)$, and $B_D(N)=D\mathrm{div}N-N(D)$. Euler normalization gives $N(F)=AD$ and the full remaining equation $B_D(N)=FQ$, with all six numerator components and general $Q$ retained. Every normalized lift is $N=U+K\nabla F$ with all 840 cubic skew-matrix coefficients initially present. The 120-dimensional subspace $K=E\wedge V$, for quadratic $V$, is a harmless gauge because

$$B_D(K\nabla F)=-6F\bigl(D\mathrm{div}V-V(D)\bigr).$$

After the six linear $F$-gauges, the exhaustive E1 form is

$$D=h+t\,l\cdot\nabla f+t^2c\cdot\nabla f+6t^5R_2,$$

where $h\in(J_f:A)_7$ has dimension 84, $l$ is an arbitrary linear five-vector, $c$ is constant, and $R_2$ is quadratic. This accounts for all $129=84+25+5+15$ parameters.

The top necessary equation has the complete complex solution

$$c^T\mathrm{Hess}(f)c+30R_2^2=0
\quad\Longleftrightarrow\quad
c=\lambda e_{X_2},\qquad R_2=\epsilon i\lambda X_2^2,\qquad \epsilon=\pm1.$$

Thus an actual even/odd cancellation occurs. Both nonzero branches were retained. Further exact equations and the specialization argument below force $h=fL$ and $l=\beta x$ on these branches. An allowed $F$-gauge gives $D'=t^2H$, with $H(x,0)=f_{X_2}$, while every corrected lift satisfies

$$N_t(x,0)\equiv\epsilon iAX_2^2\pmod{J_f}.$$

The constant and linear coefficients of $B_{D'}(N)=FQ$ give $Q_0=0$ and

$$-2f_{X_2}N_t(x,0)=fQ_1.$$

Since $f$ is smooth and irreducible, $\gcd(f,f_{X_2})=1$, so $f\mid N_t(x,0)$. This would put $AX_2^2$ in $J_f$. But the coefficient of $X_0^3X_2^2Y_0^3$ vanishes on every cubic multiple of every $f_i$: no monomial in any $f_i$ divides it. Its coefficient in $AX_2^2$ is one. This closes both nonzero branches with full corrections and general quotient.

### 2. Joint odd and further even loci

The remaining $t^2$ equations force $l_i=a_ix_i$, independently of $h$: exact quadratic row spaces of ranks 144 and 15 isolate all 20 off-diagonal squares. For $h=0$, the full compatible correction calculation yields nine necessary quadrics whose cubic Macaulay rank is $35/35$. Hence **every degree-seven $Y_2$-odd denominator is excluded, including mixtures of all four odd characters**.

A separate local argument excludes the full 30-parameter family $D=fL+t\,l\cdot\nabla f$, with arbitrary linear $l$: after gauging to $t(l\cdot\nabla f)-Lt^6$, its constant and $t^6$ equations force $AL^2\in J_f$. Exact multiplication by $A$ on base quadratics has rank $15/15$, hence $L=0$, and the joint odd exclusion applies.

For $V=(J_f:A)_7/fS_1$, of dimension 79, three normalized character pieces also have empty necessary projective loci:

| Character of $[h]$ | Parameters | Quadrics | Completed Gröbner basis size |
|---|---:|---:|---:|
| 0010 | 18 | 44 | 967 |
| 0100 | 17 | 44 | 620 |
| 1000 | 18 | 44 | 968 |

The modular calculation is over $\mathbb F_{32003}$ and proves that every coordinate has a power of degree at most five in its ideal. The exact rational source, integrality at 32003, and source ranks were independently checked. The degree-14 Jacobian quotient has dimension 185 over both $\mathbb Q$ and $\mathbb F_{32003}$, so its localized integral module is free. The resulting projective scheme has empty special fiber; properness excludes a nonempty generic fiber. This is a checked characteristic-zero implication, not a finite-field point scan. The analogous 25-parameter calculation used above has Hilbert function $(1,25,195,361,240,51,2)$.

These exclusions allow arbitrary retained $fL$ terms and the permitted odd component. **They do not exclude mixtures of multiple even base characters.**

### 3. Complete remaining finite problem and evidence

Every remaining degree-seven certificate has a representative

$$\boxed{D=h+t\sum_{i=0}^4a_ix_if_i,\qquad h\in(J_f:A)_7,\quad h\notin fS_1.}$$

Retain 79 base-complement parameters, all five $fS_1$ parameters, five odd parameters, and all 720 effective Koszul parameters. The 79 charts normalizing one nonzero base-complement coordinate to one cover the remaining locus. The complete coefficient equations are

$$\mathrm{rem}_{t^6+f}\bigl(D\mathrm{div}N-N(D)\bigr)=0.$$

The completed exact export has **9,435 nonzero coefficient equations**, 68,085 quadratic columns, and 2,274,017 integer coefficient entries. These equations are not asserted to be independent. At a solution, $Q=B_D(N)/F$ recovers the full original cleared identity; $Q$ need not vanish. Since every generated nonzero $D$ has $t$-degree at most one and irreducible $F$ has $t$-degree six, complex coprimality is automatic on these charts.

The packet includes exact bases, source hashes, proof notes, equation blocks, and replay scripts. Twelve selected checks passed from a clean extraction without network access. All incidence-block hashes, counts, basis rescalings, and Koszul labels were checked; 16 selected columns were independently rebuilt with separate tuple/Fraction arithmetic, including nontrivial reduction of $t^8$ and $t^9$. No second independent recomputation of every exported column is claimed.

**Remaining:** pure normalized base character 1110 and mixtures of at least two even characters. The 1110 Gröbner computation was interrupted without a completed result; the joint degree-three attempt also timed out. Neither is an exclusion. The full streamed system remains unsolved.

Prepared for `fqlx` with ChatGPT and parallel AI-agent assistance; independent checks here mean separate computational implementations and algebra audits, not independent human review. Credits to Benjamin E. Diamond and the [hodge.computer](https://hodge.computer) contributors for the framework, and `rbajaj5` for the published degree-seven bases and calculations.


