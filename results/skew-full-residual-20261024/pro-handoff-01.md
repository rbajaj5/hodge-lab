# Pro constructive handoff 01 — triangular mixed current

Observed in the existing Pro chat `6adb94ec-665c-8325-9a4b-2b4237c63f19`
on 24 October 2026, about 15:23 UTC. Transcribed from the visible live
response while Pro was still computing; this is a proposal, not a receipt.
The separate local checker received these formulas before any result was
promoted. The requested notebook parent is 84f294e0235c3fd4b5d4849e565536172a74329c.

Use coefficient coordinates (a,v,t), the completed centered chi and R2,
and the pinned full connection. To avoid the displayed response's repeated
letter K, use K0 for its scalar and Kmat for its matrix:

```
C=t(1-t^2)/7; D=1+t^6
K0=C^2-3tvD
w=C C'-2tvD'
q=3D C'-2C D'
G_a=0
G_v=-tv w+3a q-2v K0
G_t=2t K0
Gamma=G_v N_v+G_t N_t=[[3tw/2,-tq],[0,tw/2]]
calD=G_v partial_v+G_t partial_t
Kmat=(partial_v G_v+partial_t G_t) I+Gamma
alpha=(N_t e1+v e0/(3a))/(36t)
beta=M_b e0/(108a)
S=alpha/G_v
T=(v beta-calD S-Kmat S)/G_v
J_a=0
J_v=G_v(S chi_v+T chi)
J_t=G_t(S chi_v+T chi)
R2-Div_N J = chi(-beta-calD T-Kmat T)
```

Derivatives of coefficient functions hold a fixed. Derivatives of chi
include physical root motion; chi_t=0 at fixed (a,v). Both source rows and
the full t derivative remain. The new candidate can introduce G_v poles.
No full cancellation was claimed in this handoff. The final vector was
still being computed. Pro had previously described working directly in
(r,v,t); this particular displayed candidate is stated in (a,v,t), so the
checker must not silently interchange coordinate derivatives or fluxes.
