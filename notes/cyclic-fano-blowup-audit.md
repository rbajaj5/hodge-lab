# The pole after a normal-plane blowup

The previous [slice audit](cyclic-fano-slice-audit.md) found pole orders one and five along two approaches to the same slice. This exact two-chart calculation explains the difference: the exceptional divisor has multiplicity **one**. The order-five approach also has contact order four with the strict transform of the denominator. Blowing up records that distinction; it does not remove the scalar pole or repair the rejected denominator.

![Normal-plane denominator and its strict transform](../results/cyclic-fano-blowup-audit-figures/cyclic-fano-blowup-audit.png)

## The fixed polynomial and scalar coefficient

Reconstruct the unchanged `cyclic-triple-fano` source at `d96911d725077e66a8f10848908be01a643b1714`, with $G=Z^2+QZ+H$ and $\Delta=Q^2-4H$. Set $X_0=Y_0=1$, $X_1=u$, $Y_1=y$, $Y_2=z$. The previously excluded $Y_2$ polar becomes

$$
E=\frac{50}{49}y+\frac{50}{49}uy^2+\frac{50}{49}y^2z
-\frac{40}{7}yz-\frac{20}{7}uy^3-24z^5.
$$

The numerator component is $P_{Y_2}=-4/3$, so we track the scalar coefficient

$$
f=\frac{P_{Y_2}}{E}=\frac{-4}{3E}
$$

in its fixed ambient frame. This is **not** the transformation of the entire vector field into blowup tangent coordinates; that would also require the Jacobian and a change of frame. Since $E_y(0,0)=50/49$, the denominator curve is already smooth at the origin for every fixed $u$. The calculation is not a resolution of a singular denominator curve.

## Two exact charts

Blow up the origin of the $(y,z)$ plane, with $u$ retained as a parameter. Here "normal plane" means this chosen two-dimensional transverse plane; it is not the full normal bundle of the curve in the fourfold. In the $y$-chart use $y=r$, $z=rt$. In the $z$-chart use $z=r$, $y=rt$. The total transforms are $rH_y$ and $rH_z$, where

$$
H_y=\frac{50}{49}
+\left(\frac{50u}{49}-\frac{40t}{7}\right)r
+\left(\frac{50t}{49}-\frac{20u}{7}\right)r^2-24r^4t^5,
$$

$$
H_z=\frac{50t}{49}
+\left(\frac{50ut^2}{49}-\frac{40t}{7}\right)r
+\left(\frac{50t^2}{49}-\frac{20ut^3}{7}\right)r^2-24r^4.
$$

Exactly one power of $r$ divides each total transform. The two expressions agree on the overlap: if $r_z=r_yt_y$ and $t_z=1/t_y$, then

$$
H_y(u,r,t)=tH_z(u,rt,1/t).
$$

The script verifies this identity and its reverse coefficient by coefficient. The numerator pulls back to the same nonzero constant in both charts.

On the exceptional divisor $r=0$, we have $H_y=50/49$ and $H_z=50t/49$. Thus the strict transform meets the exceptional curve at one point, represented by $(r,t)=(0,0)$ in the $z$-chart. There

$$
\det\frac{\partial(r,H_z)}{\partial(r,t)}=\frac{50}{49}\ne0.
$$

The strict transform is smooth and crosses the exceptional curve transversely. Locally near this intersection, writing $D=V(E)$ and $\widetilde D$ for its strict transform, the divisor identity is

$$
\pi^*D=\mathrm{Exc}+\widetilde D.
$$

Both multiplicities are one. Because the numerator is a unit, the scalar coefficient has a simple pole along each of these two local divisors. There is no cancellation.

## Why the special arc still has order five

The original arc $z=0$ is $t=0$ in the $y$-chart; $H_y(r,0)$ has nonzero constant term, so its denominator order is one. The arc $y=0$ is $t=0$ in the $z$-chart, where

$$
H_z(u,r,0)=-24r^4,\qquad E\vert_{y=0}=-24r^5.
$$

Its total order is therefore $1+4=5$: one from the exceptional factor and four from contact with the strict transform. The implicit strict-transform branch satisfies

$$
t(r)=\frac{588}{25}r^4+O(r^5).
$$

The exact nonzero derivative and substitution check establish this leading term. A high order along this special arc is not multiplicity five along the exceptional divisor.

Shafarevich's local-intersection definition in Chapter 4, Definition 4.1 (supplied pp.233–234), gives the same distinction as finite local lengths. For fixed $u$ over a characteristic-zero field $k$,

$$
\dim_k\frac{k[[r,t]]}{(r,H_z)}=1,\qquad
\dim_k\frac{k[[r,t]]}{(t,H_z)}=4,\qquad
\dim_k\frac{k[[y,z]]}{(y,E)}=5.
$$

These follow directly from the three exact restrictions above; they add no new search or numerical approximation.

The next supplied excerpt, Chapter 4 §3.1, Theorem 4.6 (pp.260–261), states that the exceptional coefficient is the multiplicity of the original curve at the center. Here that multiplicity is one, since $E_y(0,0)\ne0$. Section 3.2's intersection formula is consistent with the directly computed change from five to four: the denominator curve and the selected axis are both smooth at the center, so their multiplicity product is $1\cdot1$. We use the local quotient calculations above for this particular claim, without inferring any uncomputed global intersection number on the fourfold.

## Scope and verification

Independent reconstruction passed both charts, the overlap, smoothness and crossing checks, the implicit branch term, and both axis orders. It rejected eight deliberately altered inputs. The receipt also distinguishes a local unit along the exceptional divisor from a unit in the entire chart's polynomial ring.

These are charts of a normal-plane blowup, not a constructed blowup of the full fourfold. At $y=z=0$, the branch polynomial is $-367/49-4u^6$. When it is nonzero, a chosen unramified root of $G$ admits a local lift of the base calculation. No global lift or new support is established. Moving a divisor within a linear-equivalence class, discussed elsewhere in the supplied reading, would not by itself preserve the fixed certificate equations.

```sh
python -S experiments/cyclic_fano_blowup_audit.py run
python -S experiments/cyclic_fano_blowup_audit.py verify
python -S experiments/check_cyclic_fano_blowup_audit.py
python experiments/plot_cyclic_fano_blowup_audit.py
```

The producer and primary replay passed using standard-library rational arithmetic. They check both substitutions, exact exceptional-factor removal, both overlap identities, exceptional restrictions, the nonzero crossing Jacobian, the leading implicit-branch term, both axis orders and six altered-packet controls. Independent source reconstruction also passed all these identities and eight mutation controls, including the distinction between exceptional multiplicity one and special-axis order five. Generation and replay each took under 0.03 seconds in the recorded run; there was no iterative search or timeout. Source and dependency hashes are in `results/cyclic-fano-blowup-audit/packet.json`; replay status is in `validation.json`. Prior packets and exclusions are unchanged. This is a geometric audit of a failed candidate, not an additional excluded denominator, certificate or phase transition.

Credit: [Shafarevich, *Basic Algebraic Geometry 1*, third edition](https://link.springer.com/book/10.1007/978-3-642-37956-7), supplied Chapter 2 §§4.2–4.3 on blowup charts and strict transforms, Chapter 3 §§1.1–1.2 on divisor orders, and Chapter 4 Definition 4.1 on local intersections; the preceding branch-polar and slice calculations; and the upstream fixed-target framework. OpenAI Codex assisted implementation and independent review. No upstream post is part of this audit.
