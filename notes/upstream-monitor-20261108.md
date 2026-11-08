# Upstream monitor — 8 November 2026

**Snapshot: 07:30 UTC. Bounded monitoring; no mathematical or Lean replay.**
Benjamin Diamond / `benediamond` merged [PR224](https://github.com/hodge-computer/sextics/pull/224)
and [PR225](https://github.com/hodge-computer/sextics/pull/225). Upstream advanced
six commits from `2d60d08d25fba3e02162b39d4c50f6b467e7f506` to
[`e3936ff366ae2302f21fb9e5730bbbd284c81d69`](https://github.com/hodge-computer/sextics/tree/e3936ff366ae2302f21fb9e5730bbbd284c81d69).
Hodge Lab's parent is `7b7ee8f7194a8779b95d7ab2dcf55c81839a1996`.

All 14 monitored discussions, including their **47 comments and 20 replies**,
are unchanged in IDs, timestamps and body hashes. All target and acceptance
data pins also match. The catalogue remains **82 targets, 66 accepted submissions
and 16 without accepted submissions**. The book's reported existence claims
for #117/#120 remain distinct from accepted publication, as recorded in the
[7 November note](upstream-monitor-20261107.md).

## Ordinary and strict existence: new book statement

[Chapter 5, §5.3](https://github.com/hodge-computer/sextics/blob/e3936ff366ae2302f21fb9e5730bbbd284c81d69/docs/05-computation.md)
now states an ordinary-to-strict homogeneous conversion in characteristic zero
for dimension `n ≥ 1`, nonzero homogeneous `F` of degree `d > 0`, and `q ≥ 1`,
with the prescribed source grading. It asserts equivalence of existence when
the denominator is **unrestricted**; smoothness and irreducibility are not
assumptions of this algebraic statement. We record the published statement and
its scope, not an independently verified theorem or a new formal acceptance.

Starting with a legal homogeneous denominator `D` of degree `e`, the construction
chooses a coordinate `u` with constant nonzero leading coefficient for `F` and
uses `Delta = Res_u(F,D)`. The reported normalized strict field may use
`Delta^q`, of degree `d*q*e`, and satisfies `q*v(F)=A` and `div(v)=0`.
This is a conversion bound **conditional on an existing certificate**. It does
not construct a certificate for an unresolved target or bound an unknown
starting denominator. Optional parity averaging may increase the degree again.

For an arbitrary **fixed `D`**, the conversion can change both its support and
degree. Consequently, fixed-denominator tests must retain the full quotient
term; strictness is not generally a valid extra restriction. The narrower
conical case in §5.1 preserves a supplied denominator independent of `u` under
the stated constant-leading-coefficient hypotheses. Preserving a supplied
`D^2` does not imply existence over `D`.

[Chapter 1](https://github.com/hodge-computer/sextics/blob/e3936ff366ae2302f21fb9e5730bbbd284c81d69/docs/01-certificates.md)
also corrects the degree-six, `q=1` denominator-gauge explanation: replacing
`D` by `D+tF` preserves coprimality. It can still change the field's strictness.
The book distinguishes a regular error on a fixed open set from exactness after
the controlled change of support; it does not say that every regular top form
is rationally exact. These changes do **not** withdraw our bounded exclusions
or justify rerunning the completed Prompt 3 work.

## Contact construction and reusable machinery

The revised [Chapter 3B](https://github.com/hodge-computer/sextics/blob/e3936ff366ae2302f21fb9e5730bbbd284c81d69/docs/03b-weighted-threefolds.md)
replaces the book's former nodal spanning witness with a smooth contact seed
derived from cubic-line geometry. Its finite witness now uses characteristic
37 instead of the earlier characteristic-23 nodal calculation. The companion
verification script changed with it. We read the changed source and recorded
its hashes; **we did not execute the finite calculation or audit its lifting
and support arguments**. The unchanged #120 discussion still describes its
separate fixed-core construction and unfinished rational extraction. A revised
book witness is not a new instance `HasCertificate` proof or a withdrawal of
that historical discussion calculation.

Chapters 3–5 also develop curve-family normal pairings, conditions for passage
from a nonzero supported image to a dominating-family conclusion, and reductions
for rational integration and cubic currents. The new criteria retain their
actual-family, smoothness, dominance and source hypotheses. In particular, a
nonzero pairing at one fixed fourfold does not by itself show that its specified
input class is in the supported image. No general even-sextic solve or new
fixed-target certificate is inferred from these additions.

The [technique guide](https://github.com/hodge-computer/sextics/blob/e3936ff366ae2302f21fb9e5730bbbd284c81d69/formal/TECHNIQUES.md)
adds two shared constructions with visible uses in maintained accepted proofs:

- `RationalFields.CommonDenominatorSubstitution` replaces duplicated clearing
  inductions in `holdout-q2` and `quadric-contact-broken`. Specialized evaluation
  and good-specialization interfaces remain with those applications.
- `ResidueTransport.PiolaContraction` supplies the contraction term used by
  the maintained `residue_piola_pullback`. Applications still supply their
  coordinate chart, inverse/chain-rule hypotheses and source binding.

The new module headers credit preparation for fqlx with ChatGPT/Codex assistance;
the clearing module identifies an unfinished symmetric-sextic draft as its
extraction source. Reuse in existing accepted proofs does not accept that draft
or change the original contributors' solve attribution.

The [formal-library policy](https://github.com/hodge-computer/sextics/blob/e3936ff366ae2302f21fb9e5730bbbd284c81d69/formal/README.md)
now requires a new shared construction to perform substantive proof work in at
least one completed solve. Generality or correctness alone is insufficient;
machinery serving only unfinished reductions stays with research applications.
This is upstream library policy, not a new requirement to formalize our current
notebook research.

The ordinary `Verify`/`HasCertificate` contract still allows a nonzero quotient.
The book's strictification result does not narrow the protected solve contract.

The merge message reports 24 passing CI jobs, including 21 sandboxed accepted
application rechecks. That is a **maintainer-reported CI result**. We did not
replay Lean or inspect those individual jobs, and it is not new acceptance or
new contributor credit. The schema-2 acceptance records remain byte-identical
to the preceding pin; historical verification receipts retain their original
source scope.

## Evidence and publication boundary

We collected complete pages with `work/read_hodge_discussions.py`, using explicit
UTF-8, 45-second request bounds and a 240-second discussion-collection budget.
The separate repository baseline records all 383 target/policy blobs; only
`formal/README.md` changed among those pins. The complete commit comparison has
six commits and 17 changed paths. Paired source capture contains 32 extant
before/after files across those paths, verified against Git blob IDs and SHA256;
the two new shared modules have no before blob.

See the [comparison](../results/upstream-monitor-20261108/comparison.json),
[discussion identity review](../results/upstream-monitor-20261108/discussion-identity-review.json),
[status check](../results/upstream-monitor-20261108/status-review.json),
[source-policy review](../results/upstream-monitor-20261108/policy-review.json)
and [capture/hash manifest](../results/upstream-monitor-20261108/review.json).
These establish source identity and reported scope, not mathematical correctness.

No upstream post, reply, edit, message or PR occurred. Earlier notebook text,
receipts and ledger history remain preserved. No research batch, visualization,
Prompt 3 rerun or alternative-draft proof verification was undertaken. Posts
1–30 and the tally stay **30 discussion contributions, one closed maintenance
PR, zero accepted authored solves**.
