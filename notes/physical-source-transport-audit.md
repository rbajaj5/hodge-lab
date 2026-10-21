# Physical source transport: the 144 and the two corrections

21 October 2026. **No discrepancy found in this bounded audit.** The exact
coordinate determinant and residue density support the normalization
$P=-V_\alpha|_{\alpha=1}/(144R)$. The normal-chart and moving-map corrections
have the signs needed to recover the protected physical source. The latter
conclusion is conditional on the covariant curve and differential first
variations, plus the function-field transport hypotheses listed below.

This extends the [earlier covariant and seed audit](moving-branch-weierstrass-audit.md).
It does not repeat that calculation or claim an independent replay of the
entire accepted proof. No upstream comment was changed or added.

[Checker](../scripts/audit_physical_source_transport.py) ·
[Exact receipt](../results/physical-source-transport-audit/replay.json) ·
[Commands and deliberate-error checks](../results/physical-source-transport-audit/validation.json) ·
[Pinned inputs](../results/physical-source-transport-audit/inputs.json) ·
[Independent review scope](../results/physical-source-transport-audit/review.json).

![Transport factors and verification boundary](../visualizations/physical-source-transport-audit.png)

The [reproducible diagram](../scripts/visualize_physical_source_transport.py)
shows actual factors and correction dependencies. Its final cancellation
uses the stated hypotheses; it is not an additional existence proof.

## Inputs and conventions

- Upstream: [28d14ed300d4d2cb84555466b81cfcfa54854cdd](https://github.com/hodge-computer/sextics/tree/28d14ed300d4d2cb84555466b81cfcfa54854cdd).
- Hodge Lab starting revision: [2887b40c4b555a6fb3e1836efb2be7615ede8e8a](https://github.com/rbajaj5/hodge-lab/tree/2887b40c4b555a6fb3e1836efb2be7615ede8e8a).
- At the publication check upstream had advanced to
  `b2ee2acb5409e37b6fad800b256fb8f2fee163bf`; all 22 audited source blobs
  were unchanged. The [head comparison](../results/physical-source-transport-audit/heads.json)
  retains both pins. Unrelated new commits were not audited.
- The checker reads $F,A,q$ from the pinned `instance.rec`, and the variable
  order from `provenance.json`. Twenty-two files have SHA-256 and Git blob
  checks. Hash verification does not mean all twenty-two proofs were replayed.
- The [refreshed discussion snapshot](../results/physical-source-transport-audit/discussion-context.json)
  includes all comments/replies in #146 at 18:39:34 UTC: our one existing
  [independent-check comment](https://github.com/hodge-computer/sextics/discussions/146#discussioncomment-19103930),
  zero replies, unchanged. Acceptance remains credited to benediamond's
  [PR #172](https://github.com/hodge-computer/sextics/pull/172); this is a
  notebook audit, not a new submission or acceptance replay.

In order $p=(X_0,X_1,X_2,Y_0,Y_1,Y_2)$, the protected target is

$$
F=\sum_{i=0}^2(X_i^6+Y_i^6)+X_0^3X_1Y_0Y_1+X_1^3X_2Y_1Y_2
 +\tfrac17X_0^2Y_0^2Y_2^2,\qquad A=X_0^3Y_0^3,\quad q=1.
$$

All computations here are exact rational functions over $\mathbb Q$;
the application is to the characteristic-zero function field of this
complex hypersurface. Put

$$
R=p_2^2,\quad v=p_3/p_0,\quad c_1=p_4/(p_1v),\quad
c_2=p_5/(p_2v),\quad x=p_0^2/R,\quad y=p_1^2/R.
$$

The parsed coordinate definitions give $F=R^3U$ and $A=v^3R^3x^3$, where

$$
U=ax^3+by^3+c+dx^2y+ey^2+fx^2,
$$

$$
(a,b,c,d,e,f)=(1+v^6,1+c_1^6v^6,1+c_2^6v^6,c_1v^2,c_1c_2v^2,c_2^2v^4/7).
$$

The auxiliary variation replaces $a$ by $\alpha+v^6$, differentiates
before setting $\alpha=1$, and uses $\dot x=-x^3/G$, $\dot y=0$,
where $G=U_x$. This preserves $U=0$ to first order. The checker parses the
actual jet pairs and verifies this fact and the first variation of $G$.
It does not invent a parameter derivation on an already specialized field.

## Two determinant calculations give the same factor

Write $F_i=\partial_iF$ and
$\tau_i=\partial_{i+1}-(F_{i+1}/F_0)\partial_0$, for $i=0,\ldots,4$.
The target has ordered coordinates $(Y,T,c_1,c_2,R,X)$ and

$$
T=Rv^6,\quad X=R^2\xi,\quad Y=R^3\eta,\qquad
V=Y^2-X^3-A_4X-B_6.
$$

The matrix convention is $M_{ji}=\tau_i(T,c_1,c_2,R,X)_j$.
All **25 entries** are independently differentiated and compared with
the parsed `rawMatrix`. Its determinant is computed by a small exact minor,
not taken from the saved theorem. With the source's `volumeVector` denoted $W$,

$$
F_0\det M=-48R^4W(\xi),\qquad W(\xi)=v^3G D\xi.
$$

The relative direction $D=\partial_y-(U_y/G)\partial_x$ fixes
$R,v,c_1,c_2$. These properties and tangency to $F$ are checked from the
parsed physical velocity. Reusing the **previously checked** invariant
differential $GD\xi=6\eta$ gives

$$
\rho=\frac{F_0\det M}{2Y}
 =\frac{-48R^4v^3(6\eta)}{2R^3\eta}=-144Rv^3.
$$

An independent coordinate-chart route checks the sign and powers. The
physical ambient coordinate volume becomes
$R^2v^2/8\,dx\wedge dy\wedge dR\wedge dv\wedge dc_1\wedge dc_2$.
On $F=R^3U=0$ its residue density is $v^2/(8RG)$ in the remaining five
coordinates. The ordered target passive determinant is
$-6R^3v^5D\xi$, giving pulled-back target residue density
$-3v^5D\xi/\eta=-18v^5/G$. The quotient is again $-144Rv^3$.

This is a **residue-volume identity on the hypersurface**. It is not a
six-dimensional ambient Jacobian identity, and $D\xi$ cannot be replaced
by the ambient partial $\partial_y\xi$.

## Source normalization and both corrections

The integral model is $E=111132V$. Parsing its small coefficient
polynomials and differentiating in $\alpha$ gives

$$
E_\alpha|_1=-16003008RP,\qquad
P=-\frac{V_\alpha|_1}{144R}=-\frac{E_\alpha|_1}{16003008R}.
$$

The apparent division by $R$ cancels: $P=N/576$ is a polynomial, with
$N$ the actual parsed `sourceNumerator`. The invariant derivatives satisfy
$\dot a_W=0$ and $\dot b_W=-(54ab^2c^2+8ace^3)/4$, and

$$
P\circ\phi=\frac{R^5}{144}(\dot a_W\xi+\dot b_W).
$$

The subscripts distinguish the Weierstrass coefficients from the cubic
coefficient $a$ being varied. Forgetting the integral scale $111132$ would
change the source. The checker compares the model coefficients with the
parsed cubic invariants; it does not assume this polynomial identification.

For the physical source set

$$
S=\frac{\partial_0A}{F_0}-\frac{AF_{00}}{F_0^2},\quad
H_p=p_0F_0+p_3F_3,\quad
C=-p_0^3p_3^4/H_p.
$$

Here $H_p$ is a paired gradient, not the covariant Hessian. Exact
differentiation checks the generic normal-chart identity and its physical
specialization:

$$
S=v^3\dot G/G+\operatorname{Div}_{F_0}(Ce_2),\qquad
\dot G=3x^2-x^3G_x/G.
$$

The tangent slot $e_2$ corresponds to $Y_0$. Direct generic-gradient and
symmetric-Hessian arithmetic also checks $\operatorname{Div}_{F_0}W=0$;
all five components of $W=v^3G\,(\text{relative tangent direction})$
are checked. Product differentiation therefore supplies

$$
\operatorname{Div}_{F_0}\bigl((z/3)W\bigr)=v^3(G/3)Dz.
$$

The moving-map scalar identity is

$$
\frac{\dot G}{G}=
\frac{\dot a_W\xi+\dot b_W}{2\eta^2}
-\frac G3D\left(\frac{\dot\xi}{2\eta}\right).
$$

We check this rational identity **given** the differentiated curve,
$GD\xi=6\eta$, and its first variation. We have not evaluated the full
covariant `xiJet` and `etaJet` to reprove those premises. The existing
`PhysicalCubicJets` uses a full polynomial syzygy and a cleared differential
identity over dual numbers to supply them; the prior universal differential
audit is reusable, but a new full covariant-jet replay is not claimed here.

With the accepted Jacobian primitive and Piola hypotheses, its pulled
divergence is $-v^3(\dot a_W\xi+\dot b_W)/(2\eta^2)$. Consequently

$$
w_{\rm physical}=w_{\rm pulled}+\frac{\dot\xi}{6\eta}W-Ce_2,
\qquad \operatorname{Div}_{F_0}w_{\rm physical}=-S.
$$

Thus a correct volume multiplier alone is insufficient: the moving-map
term is added, and the normal correction is subtracted. The checker rejects
omitting the former or reversing the latter. These are deliberate mutations
of the test, not defects discovered in the accepted construction.

## Verification boundary and reproduction

The relevant localization requires nonzero coordinate denominators,
$F_0$, $G$, covariant Hessian and $\eta$ (the latter from the covariant
Jacobian). These are nonzero **function-field elements**, not claims of
nonvanishing at every point. The generic algebra does not independently prove
irreducibility, field embeddings or that each chart is available.

The shared moving-map theorem needs the curve, coefficient constancy,
invariant differential and **both first variations**. The Piola theorem
additionally needs two inverse-matrix identities, nonzero determinant, a
chain rule for every field element, mixed partial compatibility and both
nonzero normals. Those source statements were read and pinned. The density
and matrix calculations here do not replace all those field-level proofs.

Executed: **65 exact equalities**, including 25 matrix-entry comparisons;
three intentional mutations exit nonzero. Python 3.11.9, SymPy 1.14.0,
60-second bound per checker process; the final baseline took 0.625 seconds
inside the checker. No run timed out. The primary checker uses explicit
exceptions, not removable Python `assert` statements. Two independent
read-only reviewers separately checked normal/moving algebra and the
coordinate-volume route; their scopes are recorded separately.

Not executed: Lean compilation/kernel replay, full Weierstrass syzygy or
full covariant first-variation expansion, a fresh seed replay, and the
trace/admissibility/clearing chain. The accepted primitive-existence theorem
remains an imported result for this audit. These are limits of this audit,
not findings that the accepted proof lacks them. No Grok escalation was
needed: the bounded algebra completed without a computational obstruction.

From the repository root, with SymPy and Matplotlib installed:

```sh
python scripts/audit_physical_source_transport.py
python scripts/audit_physical_source_transport.py --perturb normalization
python scripts/audit_physical_source_transport.py --perturb omit-moving
python scripts/audit_physical_source_transport.py --perturb normal-sign
python scripts/visualize_physical_source_transport.py
```

The three `--perturb` commands must fail, with nonzero exit codes. Normalization
changes 144 to 143; the other two remove a correction or change its sign.
The receipt records executed commands, outputs and the checker hash. The
visualization reads the passing receipt and can be regenerated independently.

Credit the classical cubic invariants, including Tom Fisher's work;
hodgepodgeconjecture's cycle-three construction, fqlx's transitive adaptation,
benediamond's accepted specialization, shared-library contributors and
Mathlib. This independent notebook audit was prepared for rbajaj5 with
OpenAI Codex assistance and read-only review agents. The browser audit
supplied by the user agrees with the determinant factors; we do not count
its transcript as an additional local execution receipt.

## Independent browser-review follow-up

The user supplied the browser review's completed report on 21 October 2026,
after this audit was published in
[`3a57584`](https://github.com/rbajaj5/hodge-lab/commit/3a57584e6927192164321fa5aefdece066a72ad1).
It reports, at the same upstream pin `28d14ed`, reconstruction of 25 tangent
matrix entries and 36 entries of a separate coordinate Jacobian, 18 exact
rational identities, three sign-sensitivity checks, and Git blob matches for
20 downloaded sources. It found no defect in the normalization or either
correction sign under the stated function-field hypotheses.

These are **reviewer-reported checks**. The separate scripts, full execution
logs and 20-file manifest were not supplied with the report, so they are not
added to our 65 executed checks, three deliberate-error tests or 22-file
input inventory. The reviewer explicitly did not perform a new Lean build,
full primitive construction, finite-trace replay or denominator-clearing
replay. Our own receipts and verification boundary remain unchanged.
This is documentation maintenance; no new calculation or upstream publication.
