# Full affine covariant-jet replay

21 October 2026. **The actual covariant first variations pass exact replay.**
All six cleared identities have zero polynomial remainder modulo the generic
cubic. This closes the specific algebraic dependency left conditional in the
[physical source transport audit](physical-source-transport-audit.md). No defect
was found in the covariant jets or the moving-map sign. This is an independent
exact calculation, not a new solve or a Lean/kernel replay.

[Source-bound checker](../scripts/audit_covariant_jets.py) ·
[Replay receipt](../results/covariant-jet-audit/replay.json) ·
[Bounded commands and failure tests](../results/covariant-jet-audit/validation.json) ·
[Input pins](../results/covariant-jet-audit/inputs.json) ·
[Independent review](../results/covariant-jet-audit/review.json).

![Six exact polynomial divisions and their scope](../visualizations/covariant-jet-audit.png)

The [renderer](../scripts/visualize_covariant_jets.py) reads the passing receipt.
The bars measure expanded expression size; they are not independent theorems
or a measure of research credit. Each zero is an exactly checked remainder.

## Pins and reused work

The source definitions are pinned at upstream
[`28d14ed300d4d2cb84555466b81cfcfa54854cdd`](https://github.com/hodge-computer/sextics/tree/28d14ed300d4d2cb84555466b81cfcfa54854cdd).
A fresh tree/blob comparison against current upstream
[`b2ee2acb5409e37b6fad800b256fb8f2fee163bf`](https://github.com/hodge-computer/sextics/tree/b2ee2acb5409e37b6fad800b256fb8f2fee163bf)
confirmed that all ten inventoried files are unchanged. Hodge Lab began at
[`f035536f268342a8043c04e687f0c7332b96d927`](https://github.com/rbajaj5/hodge-lab/tree/f035536f268342a8043c04e687f0c7332b96d927).
Every source is SHA-256/Git-blob checked. A file hash is not a replay of all
the theorems in that file.

The new checker reads the actual `Cubic`, `Covariants`, `PhysicalCubicJets`
definitions and the compact right-hand side of `Syzygy.full_syzygy`.
It evaluates all coefficient expressions and the actual assembly functions;
the affine supports have 13, 192 and 873 monomials for $H,\Theta,J$.
It separately evaluates the actual input jets with dual-number multiplication,
then compares their full first variations with polynomial differentiation.
The inverse/quotient definitions are evaluated on small abstract rational
jets and combined with those full polynomial variations.

Reused, without rerunning their complete checkers:

- [Covariant/seed audit, 826ed415](https://github.com/rbajaj5/hodge-lab/commit/826ed4150c9b034f0bcd2e7874323e5d07136213):
  canonical-covariant identification, source model and finite-field seed.
- [Physical transport audit, 3a57584](https://github.com/rbajaj5/hodge-lab/commit/3a57584e6927192164321fa5aefdece066a72ad1):
  protected-target binding, physical coordinate/tangent identification,
  signed density, $1/(144R)$ normalization, and normal-chart correction.

Both receipt hashes are checked and retained in the new manifest. The curve
and invariant differential are evaluated within this new six-identity bundle
because they are direct dependencies of the first variations. The old
receipts, the 65-check count, and the separately reported browser review stay
unchanged; this batch is not added to them.

The protected target remains $q=1$, $A=X_0^3Y_0^3$, with variable order
$(X_0,X_1,X_2,Y_0,Y_1,Y_2)$ and

$$
F=\sum_{i=0}^2(X_i^6+Y_i^6)+X_0^3X_1Y_0Y_1+X_1^3X_2Y_1Y_2
+\frac17X_0^2Y_0^2Y_2^2.
$$

Its record/provenance bytes are pinned, while their mathematical substitution
binding is reused from the earlier audit. There, $F=R^3U$, $R=X_2^2$,
$v=Y_0/X_0$, $x=X_0^2/R$, $y=X_1^2/R$,
$c_1=Y_1/(X_1v)$ and $c_2=Y_2/(X_2v)$, with

$$
(a,b,c,d,e,f)=(1+v^6,1+c_1^6v^6,1+c_2^6v^6,c_1v^2,c_1c_2v^2,c_2^2v^4/7).
$$

## The actual first variations

Work in $\mathbb Q[c,a,b,d,e,f,x,y]$, on the affine chart $z=1$:

$$
U=ax^3+by^3+c+dx^2y+ey^2+fx^2,\qquad G=U_x,\qquad B=U_y.
$$

Let $Q=\Theta$, $S_N=\mathrm{s4Numerator}$ and
$T_N=\mathrm{s6Numerator}$. Write

$$
\xi=Q/H^2,\quad \eta=-J/(2H^3),\quad
a_W=S_N/3,\quad b_W=-T_N/108.
$$

The parsed jets vary $a$ at speed one and $x$ at speed $-x^3/G$;
the other five coefficients and $y$ have zero speed. Define

$$
P=G\partial_a-x^3\partial_x,\qquad
L=G\partial_y-B\partial_x,\qquad E=P/G,\quad D=L/G.
$$

Both $PU=LU=0$. The checker evaluates the full dual-number tables and obtains

$$
N_\xi=H\,PQ-2Q\,PH,\quad N_\eta=H\,PJ-3J\,PH,\quad K_g=PG,
$$

$$
\dot\xi=\frac{N_\xi}{GH^3},\qquad
\dot\eta=-\frac{N_\eta}{2GH^4},\qquad \dot G=K_g/G.
$$

In particular $\dot a_W=0$ and
$\dot b_W=-T_{N,a}/108=-(54ab^2c^2+8ace^3)/4$.

The auxiliary $E$ and relative $D$ commute. However
$[E,GD]=\dot G D$, so differentiating $GD\xi=6\eta$ must retain
$\dot G D\xi$. This is checked algebraically, and deliberately omitting that
term fails the actual polynomial remainder test. Here $E$ lives on the
auxiliary family before specialization. No auxiliary-parameter derivation on
the already specialized physical function field is asserted.

## Six complete polynomial identities

Set $M=HLQ-2QLH$ and
$K_d=GH\,LN_\xi-HN_\xi LG-3GN_\xi LH$.
The following numerators were constructed and divided by $U$:

$$
\begin{aligned}
C&=27J^2-108Q^3-36S_NQH^4+T_NH^6,\\
N_c&=54JN_\eta-(324Q^2+36S_NH^4)N_\xi
-36(PS_N)QH^5+(PT_N)H^7,\\
N_d&=K_d+K_gHM+3GN_\eta,\\
N_j&=-JK_d+GMN_\eta+3J^2K_gH,\\
N_m&=54K_gJ^2+G^2T_{N,a}H^6
-18(GJ\,LN_\xi-N_\xi JLG-N_\xi GLJ).
\end{aligned}
$$

| Rational residual | Cleared numerator | Clearing denominator | Numerator / quotient monomials | Remainder |
| --- | --- | --- | ---: | ---: |
| $\eta^2-\xi^3-a_W\xi-b_W$ | $C$ | $108H^6$ | 20,626 / 13,094 | 0 |
| $2\eta\dot\eta-(3\xi^2+a_W)\dot\xi-\dot a_W\xi-\dot b_W$ | $N_c$ | $108GH^7$ | 38,004 / 25,710 | 0 |
| $GD\xi-6\eta$ | $M+3J$ | $H^3$ | 1,168 / 490 | 0 |
| $GD\dot\xi+\dot G D\xi-6\dot\eta$ | $N_d$ | $G^2H^4$ | 4,751 / 2,529 | 0 |
| $G^2(2\eta D\dot\xi-2D\xi\dot\eta)+12\eta^2\dot G$ | $N_j$ | $GH^7$ | 49,757 / 34,355 | 0 |
| $\dot G/G-(\dot a_W\xi+\dot b_W)/(2\eta^2)+(G/3)D(\dot\xi/(2\eta))$ | $N_m$ | $54G^2J^2$ | 29,574 / 19,563 | 0 |

The fifth row matches the rearranged `PhysicalCubicJets.differential_jet`
statement, not just an informal variant. An independent SymPy checker
verifies the rational denominator clearings before imposing any covariant
identity; it does not assume these abstract residuals vanish.

The main checker also verifies the compact source identity $C=UK$ using the
actual ten-term formula $K$ in
[the pinned full_syzygy statement](https://github.com/hodge-computer/sextics/blob/28d14ed300d4d2cb84555466b81cfcfa54854cdd/formal/lean/HodgeComputer/Constructions/TransitiveCubic/Syzygy.lean).
It checks the first-variation transformations independently:

$$
\begin{aligned}
N_c&=HPC-6C\,PH,\\
N_d&=G\{HP(M+3J)-3(M+3J)PH\},\\
N_j&=-JN_d+(M+3J)(GN_\eta+K_gHJ).
\end{aligned}
$$

Since $U$ is monic linear in $c$, exact division introduces no denominators.
The quotient ring is equivalently obtained by substituting
$c=-ax^3-by^3-dx^2y-ey^2-fx^2$. Every division is checked by multiplication
back: numerator equals $U$ times quotient plus remainder. The receipt records
deterministic hashes of all sparse rational numerator and quotient arrays;
the checker reconstructs these arrays from source rather than trusting saved
answers. No modular-to-characteristic-zero inference or point sampling is used.

## What closes, and what remains imported

**Closed:** the complete affine covariant curve/differential first variations
and moving-map scalar identity for this generic cubic family. Together with
the reused physical substitutions, these remove the abstract-jet premises
from the earlier scalar transport calculation on the stated open chart.
The $1/(144R)$ normalization and pulled + moving − normal assembly retain
their previously checked values.

**Still outside this replay:** Lean elaboration/kernel checking, generated
Lean coefficient-proof files, existence/construction of the Jacobian primitive,
the full Piola/field-embedding chain, trace descent, admissibility and homogeneous
denominator clearing. The physical chart's nonzero elements are imported
function-field hypotheses; this calculation does not prove that each is
nonzero on the specialized target, much less at every point. The rational
interpretation requires characteristic zero, $G,H\ne0$, and $J\ne0$ for the
moving quotient. These are audit boundaries, not findings of a defect in the
accepted construction.

No finite-field seed, acceptance status, Prompt 3 result or previous comment
correction was reopened. No upstream post, edit or PR was made.

## Bounded execution and reproduction

The main source-bound replay passed **62 required checks**, including six
exact divisions with zero remainder. The separate denominator reviewer passed
**15 exact symbolic identities plus four deliberately wrong denominator
rejections**. These counts have different scopes and are not combined.
Three full-checker mutations fail at their intended algebraic conditions:

- Reversing the $x$-jet direction: `actual cubic jet tangent failed`.
- Perturbing one parsed $J$ coefficient: `actual full_syzygy RHS failed`.
- Omitting $\dot G D\xi$: `differential_first_variation remainder failed`.

The validator checks the specific failure messages as well as nonzero exit
codes, and runs with `python -O` to ensure the checks do not depend on removable
assertions. One implementation attempt failed while serializing FLINT integer
exponents; converting them to Python integers fixed the output. That failed
attempt is recorded as an implementation failure, not a mathematical result.
Staging validation also caught a Windows CRLF/LF byte mismatch. Explicit LF
output and a fresh bounded validation fixed the hash/committed-byte mismatch;
no mathematical formula changed.

Versions: Python 3.11.9, python-flint 0.9.0, SymPy 1.14.0; Matplotlib 3.11.1
for the visualization. Final validation took 14.219 seconds including process
startup; the passing main calculation took 1.453 seconds. Each main process
had a 120-second bound, the independent review 60 seconds, and the batch a
600-second computation ceiling. No timeout occurred. No GPU was needed.

From the repository root with those libraries installed:

```sh
python scripts/validate_covariant_jet_audit.py
python scripts/visualize_covariant_jets.py
```

For the main replay alone: `python scripts/audit_covariant_jets.py`.
The independent checker is
[review_covariant_jet_denominators.py](../scripts/review_covariant_jet_denominators.py).
The [validation receipt](../results/covariant-jet-audit/validation.json)
records commands, outputs, time bounds and the implementation failure.

Credit the classical cubic-invariant work, including Tom Fisher; the
cycle-three construction of hodgepodgeconjecture, fqlx's transitive adaptation,
benediamond's accepted specialization, shared-library contributors and Mathlib.
This notebook replay was prepared for rbajaj5 with OpenAI Codex assistance and
an independent read-only review agent. It audits existing work and claims no
new authored solve. No Grok prompt was needed: the bounded calculation resolved.
