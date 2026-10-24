# Selected physical-source normalization: mathematical/API derivation

23 October 2026, America/New_York. Pro source_math AI reviewer.
This is a separate mathematical derivation, packet-source inspection and one
bounded exact symbolic check. This role executes no Lean commands. The sole
Lean writer's receipts determine which parts below are formally closed.

## Fixed source conventions

The protected source uses q=1 and A=X0^3 Y0^3. The already formalized
Y0=1 chart is X0=x, X1=rx, X2=wx, Y1=t, Y2=nu, with U=x^2.
The cubic is

    P0(U) = (1+r^6+w^6)U^3 + t(r+r^3w)U^2
            + rt(1-t^2)U/7 + 1+t^6,

and the curve convention is nu^6 = -P0(U). This minus sign is confirmed by
the actual benediamond packet README and its pinned connection JSON.
The JSON calls the sixth-root fibre variable `v`; that variable must not be
confused with the new base coordinate v=r^-1+rw. This note consistently
writes the fibre variable as nu.

The packet connection is nabla=d+M, with columns indexing the input basis
(dU/nu^5, U dU/nu^5). Its source on Y0=1 is reported as
+M_b0 e0/12 in the packet's declared vector-source convention. The original
connection JSON instead uses Y1=1, Y0=alpha, and -alpha^3 M_b e0/12.
The packet README supplies that chart/gauge comparison. This new unit does
not silently identify the two coordinate systems or replay all connection
gauges.

The packet explicitly records an overall sign difference: standard projective
Omega in the physical ordering (X0,X1,X2,Y0,Y1,Y2), with the normal differential
last and base-first order dr,dw,dt,dU, gives the negative of the packet source.
This agrees with the old Lean volume conventions. The old formal normalized
coefficient is +5U^2/(72nu^11) multiplying dU wedge dr wedge dw wedge dt.
Moving dU past the three base forms gives a minus. A positive scalar in
fibre-first order and a negative scalar in base-first order represent the
same actual four-form. Therefore the old positive coefficient alone does not
prove equality to the packet's positive vector source under a fixed order.

## Selected coordinate and coefficient theorem

Put V=rU, v=r^-1+rw and a=(1+r^6+w^6)/r^3. For r nonzero,

    a = r^3+r^-3+(vr-1)^6/r^15,
    b = tv, c=t(1-t^2)/7, d=1+t^6,
    P0(U) = aV^3+bV^2+cV+d.

The physical covering polynomial is the unchanged

    f(r)=r^18+r^12+(vr-1)^6-a r^15.

All appearances of f_r mean derivative at fixed new base a,v,t.
On the cover f_r=r^15 A_r, where A_r differentiates A(r,v) at fixed v.
It would be wrong to differentiate a=(1+r^6+w^6)/r^3 at fixed w and identify
that derivative by itself with A_r.

The two-step Jacobian factor is

    dV wedge dr wedge dw wedge dt
      = r dU wedge dr wedge dw wedge dt,
    da wedge dv wedge dt
      = (f_r/r^14) dr wedge dw wedge dt.

The combined ordered Jacobian is consequently

    det d(V,a,v,t)/d(U,r,w,t) = f_r/r^13.

This combined determinant was computed directly from the four displayed
coordinate functions by the focused exact checker; it was not inferred
solely from the claimed final source. On r*f_r*nu nonzero, its source pullback
identity is

    (5U^2/(72nu^11)) dU wedge dr wedge dw wedge dt
      = (5/72)(r^11/f_r)(V^2/nu^11)
          dV wedge da wedge dv wedge dt.

Equivalently the V=rU fibre change contributes r^-3 to U^2 dU, and the base
change contributes r^14/f_r. Their product is r^11/f_r. No 1/864 factor enters
this calculation. The old 5/72 remains attached to its actual form and is
transported through the coordinate change.

## Why the prospective vector coefficient is 1/12

On nu^6=-(aV^3+bV^2+cV+d), coefficient differentiation at fixed V,a,c,d gives

    partial_b(nu) = -V^2/(6nu^5),
    partial_b(nu^-5) = +(5/6)V^2/nu^11.

The sign is positive because the curve equation has a minus. Therefore
5/72=(1/12)(5/6). This is a coefficient-variation identity, not by itself a
construction of a Gauss-Manin connection or an identification of its matrix.

## One selected exact fibre-reduction column

The actual packet supplies a small exact correction for the b direction,
input basis column zero. Let

    Delta = 27a^2d^2-18abcd+4ac^3+4b^3d-b^2c^2,
    P = aV^3+bV^2+cV+d,
    N0 = 27acd-12b^2d+bc^2,
    N1 = a(3bd-c^2),
    NR = 2N1 V^2+(3acd+2b^2d-bc^2)V+(9ad^2-bcd).

Then the pinned JSON's first b column is

    m0=N0/(6Delta), m1=N1/Delta,

and its exact correction is R=NR/Delta. The substantive identity is the
polynomial equality

    5Delta V^2 = -P(N0+6N1 V)-6P NR' + 5P' NR.

No nonzero Delta assumption is needed for this cleared polynomial identity.
For the rational version Delta must be nonzero. With nu nonzero and
nu^6=-P, a fibre derivation D satisfying D(V)=1 and D(a)=D(b)=D(c)=D(d)=0
has D(nu)=-P'/(6nu^5). The cleared identity then yields

    (5/6)V^2/nu^11 = (m0+m1V)/nu^5 + D(R/nu^5).

After multiplication by dV this is the exact representative identity needed
to identify the variation with the specified matrix column modulo a relative
exact differential. It keeps both matrix rows and the exact correction.
Dropping the correction or transposing the input column changes the identity;
the focused mutation controls detect both errors. This is a single selected
column, not a replay of all eight packet reductions or its later current and
pole-exclusion calculations.

The precise formal boundary still matters: proving this representative
identity does not itself build the relative de Rham quotient, a rank-two
Gauss-Manin module, its identification with the physical residue class, or
compatibility with every base direction. A Lean derivation statement may
have the coordinate derivation as an explicit hypothesis; that hypothesis is
not the desired source identity. The final source inventory and proof types
must identify which construction obligations remain.

## Quotient factor and remaining boundary

The completed ScalarExtensionTrace unit already constructs quotientWeight11
in E=K[X]/(f), with image rho^11/f'(rho) in every splitting-field component.
Thus the newly derived scalar factor r^11/(12f_r) is represented by
(1/12) quotientWeight11, once instantiated at those already constructed roots.
This is scalar quotient identification. It does not automatically identify
the rank-two vector-valued physical source or its connection/cohomology class.

Nonzero/chart conditions are Y0=1, X0=x nonzero for the ratio chart and U=x^2
coordinate recovery, r nonzero for the fibre/base gauge, nu nonzero for the
normal and relative inverse powers, f_r nonzero for inverse base Jacobian,
and Delta nonzero for the rational matrix column. Characteristic zero permits
the denominators 2,6,7,12,72. The previous generic root construction proves
r and f_r nonzero at its roots; no such assertion is made for every
specialization. No rational primitive, general residue/de Rham theory,
denominator search, global clearing, certificate or solve is supplied.

## Actual execution by this reviewer

`check_selected_normalization.py` uses explicit exceptions under Python -O
and reads only the selected pinned connection column. It passed ten new
identities and five mutations in 0.265866 seconds under a 600-second limit,
with Python 3.12.14 and SymPy 1.14.0. Whole-process time was 1.724669 seconds.
The mutation controls cover sign, r exponent, unrelated 1/864 scaling,
matrix-column transposition and omission of the relative exact correction.

The first command failed at import because SymPy was unavailable. Its stdout,
stderr and exit are retained in execution-01. One 45-second-bounded install
to an isolated /tmp dependency directory completed in 5.272 seconds; no
toolchain or repository environment was modified. Execution-02 then passed.
No missing dependency, interrupted calculation or packet-authored receipt is
counted as this reviewer's mathematical result. No Lean was executed here.
