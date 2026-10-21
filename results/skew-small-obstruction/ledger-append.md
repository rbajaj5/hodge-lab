
119. **21 October 2026 — Independent small skew certificate and companion-scope comparison.**
     Audited checkpoint 118 against all six comments visible in live discussion
     127 and fqlx's pinned twisted-companion packet. Notebook base
     `e057d7e98ce6ab58a05dc80d76879eaf772f381c`; upstream
     `a6b4cc49452abe31ead0be71d04e8146639896d9`. Both heads were refreshed and
     unchanged. The attachment SHA-256 remains `3901f358ec9f1f46b6f4900cba80aa82160dd50d28e86e766aae826e39a960be`.

     The exact three-coefficient dual for D=a and total numerator degree <=4
     is correct. A standalone Fraction implementation reconstructs the
     coefficient transpose and all 280 columns, with 299 explicit requirements.
     The three equations force n2=n0, n0=1/36 and n2=0. All four components
     are retained. At degree five an explicit numerator satisfies these three
     rows but has full residual [rt]=5/3; it is not a primitive. The small
     dual does not itself detect omission of denominator differentiation;
     checkpoint 118's separate positive control supplies that check.

     Scope comparison: 165 affine-in-U horizontal coefficients map directly
     into fqlx's reported degree-six H/a space. The 70 vertical coefficients
     are fiber-exact in the necessary rank-two equation. Five independent
     polynomial reductions describe the other 45 horizontal coefficients;
     U^2/a already produces genuine a^2 denominators. This does not establish
     increased coverage, disjointness, or absence of another gauge. Relative
     exact corrections need their base derivatives for absolute reconstruction.
     The two historical 504-column / augmented-rank-505 screens remain
     author-reported in this audit; they were not rerun.

     Initial independent calculations took 0.015 and 0.123 seconds internally.
     Final-path checkers under python -O and plotting passed in 4.413 seconds
     total before a label-width-only plot repair. Every process was bounded
     by 60 seconds, with a 180-second computation ceiling. No timeout.
     The source reader's nested-table/ID extraction repairs and plot repair
     are recorded as implementation work, not mathematical evidence.

     [Certificate, overlap, limits and next calculation](notes/skew-small-obstruction-audit.md) ·
     [Input pins](results/skew-small-obstruction/inputs.json) ·
     [Coefficient replay](results/skew-small-obstruction/three-coefficient-replay.json) ·
     [Relative reductions](results/skew-small-obstruction/horizontal-reduction.json) ·
     [Commands and limits](results/skew-small-obstruction/validation.json) ·
     [Review](results/skew-small-obstruction/review.json) ·
     [Reproducible selected-row figure](visualizations/skew-small-obstruction.png).

     **Publication audit:** a concise reply beneath fqlx's companion comment
     19080252 is justified as an independent small certificate and scope
     clarification, not a stronger coverage claim. Push this audit first;
     only then publish, read back and record the actual permalink. The
     [draft](results/skew-small-obstruction/comment-draft.md) and
     [publication record](results/skew-small-obstruction/publication.json)
     distinguish preparation from outcome. No upstream post is claimed here.

     Completed source-transport/covariant-jet audits were reused, not rerun.
     No primitive, unrestricted exclusion, homogeneous certificate-degree
     bound, Lean proof, trace or clearing is constructed. The next targeted
     calculation is containment of the 45 high-U covariant-divergence images
     in the prior 504-column image, retaining absolute correction data.
     Credit fqlx (Ben Burns) for source/connection/companion work, checkpoint
     118 for the dual, and Benjamin E. Diamond and contributors for the
     protected framework. Prepared for rbajaj5 with ChatGPT and parallel
     AI-agent assistance. Independent means separate implementations, not
     human review. Tally remains **28 discussion contributions, one closed
     maintenance PR, zero accepted authored solves** until verified publication.

     **Publication attempt:** the GitHub integration rejected creation of the
     reviewed note blob with HTTP 403, "Resource not accessible by integration",
     before any tree, commit or branch update. One write attempt; no repeated
     authentication requests. Remote main was independently re-read at the
     same e057d7e revision. This audit and reply remain local and unpublished.
     The required ledger-first ordering therefore prevented an upstream post.
     A checked patch is provided for the already authorized Codex workflow;
     no extra publication permission is needed. Contribution tally unchanged.
