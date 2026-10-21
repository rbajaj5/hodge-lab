"""Render the actual selected coefficient matrices, not a rank claim for all rows."""
from pathlib import Path
import json
from fractions import Fraction
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "results/skew-small-obstruction/three-coefficient-replay.json").read_text(encoding="utf-8"))
maps = data["full_selected_coefficient_maps"]
def coeff(row, component, powers):
    return next((x["coefficient"] for x in maps[row][component]
                 if x["exponents"] == powers), "0")

columns = [(0,[0,0,0,0]), (0,[0,0,0,2]), (1,[0,2,0,3])]
matrix = [[coeff(i,j,e) for j,e in columns] for i in range(3)]
rhs = [str(x) for x in data["rhs_selected_coefficients"]]
fig, axes = plt.subplots(1,2,figsize=(13.8,5.9))
fig.patch.set_facecolor("white")
for ax in axes: ax.axis("off")
rowlabels = ["[r t³]", "[U² w¹²]", "[U² w¹² t²]"]
for ax, n, title in [(axes[0],2,"Degree ≤ 4: contradiction"),
                      (axes[1],3,"Degree 5: these rows can be satisfied")]:
    rows = [[rowlabels[i]]+matrix[i][:n]+[rhs[i]] for i in range(3)]
    labels = ["coefficient", "n₀", "n₂"] + (["[r²t³] Nᵣ"] if n==3 else []) + ["source"]
    table=ax.table(cellText=rows,colLabels=labels,
                   colWidths=[.30]+[.69/(n+1)]*(n+1),
                   cellLoc="center",bbox=[0,.47,.99,.34])
    table.auto_set_font_size(False);table.set_fontsize(11)
    for (i,j),cell in table.get_celld().items():
        cell.set_edgecolor("#c4ccd5")
        if i==0:cell.set_facecolor("#e9f0f5")
        elif j==n+1:cell.set_facecolor("#fff1d5")
        elif n==3 and j==3:cell.set_facecolor("#e1f3ec")
    ax.set_title(title,loc="left",fontsize=14,fontweight="bold",pad=15)
axes[0].text(0,.29,"n₂ = n₀,   n₀ = 1/36,   n₂ = 0",fontsize=13)
axes[0].text(0,.16,"Dual weights:  (3/5, 1/35, −1/35)\nPairing:  0 on every allowed column;  1 on source.",fontsize=11,linespacing=1.7)
axes[1].text(0,.29,"One solution of these rows:  (1/36, 0, −5/3024)",fontsize=12)
axes[1].text(0,.16,"Full residual still has [r t] = 5/3.\nThis is not a primitive or a full degree-5 search.",fontsize=11,linespacing=1.7)
fig.suptitle("One-reflection-skew: a small exact obstruction and its boundary",fontsize=17,fontweight="bold",y=.98)
fig.text(.04,.035,"Actual selected rows of M(N), D = 1 + r⁶ + w⁶. All four components retained.\nThe complete degree-4 check uses 280 columns; this picture shows only the contributing coefficients.",fontsize=10,color="#394754")
fig.subplots_adjust(top=.83,bottom=.18,wspace=.24,left=.04,right=.98)
out=ROOT/"visualizations";out.mkdir(exist_ok=True)
for extension in ("png","svg"):
    target=out/f"skew-small-obstruction.{extension}"
    fig.savefig(target,dpi=150,facecolor="white")
    if extension=="svg":
        target.write_text("\n".join(line.rstrip() for line in
                          target.read_text(encoding="utf-8").splitlines())+"\n",
                          encoding="utf-8",newline="\n")
print("Rendered selected coefficients from the exact replay JSON.")
