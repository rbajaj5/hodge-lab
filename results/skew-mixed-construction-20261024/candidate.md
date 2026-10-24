# Fixed-a triangular mixed current

All coefficient derivatives below are at fixed a. The physical chi is
`chi=r^-3-v^3/3` on `a=A(r,v)`; its v derivatives include `r_v=-A_v/A_r`.
The packet convention is positive source, column inputs, coefficient connection d+N.

Set C=t(1-t²)/7, D=1+t⁶, K=C²-3tvD, w=CC'-2tvD', q=3DC'-2CD'.
Then G=(0, -tvw+3aq+2vK, -2tK). Its contracted connection is
Gamma=[[3tw/2,-tq],[0,tw/2]]. Write kappa=div(G)I+Gamma and
DG=Gv partial_v+Gt partial_t.

Write the reused centered residual R2=alpha chi_vv+beta(v chi_v-chi), where
alpha=(Nt e1+v e0/(3a))/(36t), beta=Mb e0/(108a).

New candidate:

    S=alpha/Gv
    T=(v beta-DG(S)-kappa S)/Gv
    h=S chi_v+T chi
    Ja=0, Jv=Gv h, Jt=Gt h

Required full identity:

    R2-Div_N(J)=chi Cvec
    Cvec=-beta-DG(T)-kappa T.

Both rows remain. A zero Cvec would give the desired compact-source current
Q+J. A nonzero Cvec rejects this candidate, while eliminating chi_vv and
chi_v from its remainder. Denominators may include Gv, a, Delta and the original
chart factors; eliminating cover-derivative poles is not a claim of global regularity.
Coefficients S,T,Cvec are in the base field; the new current and remainder use
only base-linear combinations of centered chi and its derivative. No independent
trace calculation is planned, and no source exactness is inferred from trace.

The initially dispatched signs `Gv=-tvw+3aq-2vK,Gt=2tK` were wrong.
The first source-matrix check failed, independently detected by the checker.
Run triangular-01 preserves that source and failure. Corrected signs above
come from the actual c,d coefficient velocities and are tested afresh.
