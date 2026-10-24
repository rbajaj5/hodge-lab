Presentation-only fallback figure
================================
Final outputs are render-01/A3-receipt-summary.png and .svg.
The PNG was inspected using view_image: text is legible, arrows and labels
do not overlap, scope box and boundary/ordinary-open distinction are clear.
No layout repair or additional rendering was necessary.

Only the two authorized frozen JSON receipts were read. No mathematical
calculation, determinant replay, source review or new search was performed.
The copied input bytes, generator snapshot, render command, package version,
input/output hashes and elapsed rendering time are in render-01 and its
visualization.json. The figure is a receipt visualization, not a proof.

Reproduce from the workspace, using a fresh output directory:
  python -O work/A3-denominator-20261024/local-figure/render_receipts.py
    --algebra work/A3-denominator-20261024/algebra/check-01/result/validation.json
    --checker work/A3-denominator-20261024/checker/A3-minor.json
    --output work/A3-denominator-20261024/local-figure/render-new

The checker receipt reports an independently reconstructed fixed matrix.
It did not compare delivered Pro CSV bytes in that execution; the figure
does not claim that such a comparison occurred. No Pro archive was read.
