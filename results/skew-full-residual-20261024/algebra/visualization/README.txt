Final visualization: render-02/mixed-beta-residue-certificate.svg and .png.
The 2800x2275 PNG was opened with view_image and accepted for readability.
See render-02/inspection.json and visualization.json for inspection and hashes.

This generator reads the frozen exact receipt. It does not import SymPy,
rerun the checker, calculate a gcd, solve an equation, or infer correctness
from coefficient sizes. It parses the already-saved numerator coefficients
solely for a signed-log descriptive plot. Gcd degrees are read verbatim.

Reproduce with a fresh output directory, from this directory:
 python render_certificate.py --receipt ../check-01/validation.json --execution ../check-01/execution.json --output-dir NEW_RENDER

The wrapper snapshots the generator and both input receipts, runs the render
with a 60-second external limit, and retains command, stdout, stderr, exit,
timing, input/output hashes, and coefficient display data. All text IO is
explicit UTF-8. Matplotlib 3.11.1 was used for the accepted render.

render-01 is a preserved rendering failure caused by Matplotlib not accepting
the bmod Mathtext command. The final generator uses a supported text operator.
render-02 completed in 1.750 seconds. No mathematical result was rerun or changed.

Final PNG SHA256:
8d88dca410564748f64fcaafce6842a430bb248a87167205616f8838920bb9f2
Final SVG SHA256:
1e550fb6fe9a890ba5ad81af9f023ab314fb517e2f894a72a551f3a6237fded3
Generator SHA256:
a7dccc0291136164a4478371f9a597b9c10b797b9aae9960f29824df6c78548a
