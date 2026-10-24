# Independent current audit

This directory verifies the proposed further current reduction for the fixed
one-reflection-skew problem. It does not contain a solution of the remaining
twisted equation, a homogeneous certificate, or a Lean proof.

The only external algebra input is the public connection JSON, SHA-256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
Its columns index the input basis and its coefficient connection is `d+M`.
The orientation is the benediamond follow-up packet's orientation. The checker
does not import the proposer's implementation or any prior source, chart,
rank, or trace checker.

Run with Python 3 and SymPy, passing the public JSON's location explicitly:

```text
python check_current.py --run --connection /path/to/source-rank2-connection.json
python check_regular_current.py --run --connection /path/to/source-rank2-connection.json
```

Both scripts use UTF-8 JSON/log IO and put a 60-second bound on the symbolic
child process. The child also has a 58-second watchdog after importing SymPy.
The finalized first checker uses exact rational-field cover arithmetic to
avoid symbolic expression expansion.

`check_current.py` checks the proposed two-direction meromorphic current Y,
the scalar derivative identity for k, both rows of its exact residual, generic
regularity of that residual at t=0, and an ordinary rational point. It rejects
four deliberate sign mutations. Its 11 checks are not claims about older
source/chart/rank results.

`check_regular_current.py` independently checks the direct current Q identity
coefficient by coefficient in chi, chi_a, chi_v, and chi_vv. It proves that all
six reduced Q components are regular at generic t=0, derives the new centering
from reciprocal Newton sums, checks a centered nonzero witness, and rejects
three sign mutations. It has 16 checks. The new trace calculation concerns
chi=r^-3-v^3/3 only; it is not a replay of an older source trace claim.

The exact centered witness is a=3, v=2, r=1, t=1, where A_r=-3 and Delta=1036.
The remaining source there is
`(105778/440559, -52889/97902)`.
On the same cover point at t=0 it is `(19/15876, 19/1134)`.
Thus the checked remainder is nonzero in both rows.

Regularity means regularity across t=0 on the generic open where r, a, A_r,
and Delta are nonzero. At t=0, Delta=27a^2. It does not assert regularity at
a=0, cover ramification, or the cubic discriminant. Centering preserves the
original source because chi_a=psi_a. Finite separable trace commutes with
base derivations; linearity over the base therefore makes the centered Q
and residual trace-free.

The initial expression-based prototype took 59.422 seconds once, then a
duplicate replay reached its 60-second subprocess timeout. A direct replay
was stopped by the 58-second watchdog. Those incomplete replays contributed
no final evidence. Replacing expression expansion with exact rational-field
arithmetic gave the finalized first replay in about two seconds. The final
regular-current replay took 6.063 seconds. See `prototype-run-notes.json`.

Provenance: an independent parallel Codex checker using the pinned public
fqlx connection and the benediamond packet's coordinate conventions. No
commits, pushes, broad research, or Lean work were performed.
