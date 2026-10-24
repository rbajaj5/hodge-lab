# Imported necessary top-pole reduction

This file records the structural handoff consumed by the new matrix. Its
symbolic identities and earlier divisor/support arguments were not rerun
by Pro. The coordinator reports 7 exact new identities and 3 sign/order
controls in 2.453 seconds; see `coordinator-reported.json`.

For F=P0+P1/A+P2/A^2+P3/A^3+P4/A^4, set
Qj=A_r*Pj_r+A_v*Pj_v. At the generic irreducible A=0 divisor, the reused
connection residue is Ra=[[0,-c/(6b)],[0,-1/3]]. The highest pole is
(Ra-4I)Q4. Since det(Ra-4I)=52/3, only P4 is forced tangent.

The earlier bounded tangent/support theorem gives
P4=(T_r*h4,T_v*h4,k4), with T_r=r^2*(r^6+1),
T_v=r*(2*r^6+1)*v-(3*r^6+2), ell=3*r*(r^6-1), and T(A)=ell*A.
Each h4 component has m=-10,...,-6, n=0,1, k=0,1,2;
each k4 component lies in the original117-monomial box B.
The top has294 parameters and four lower sectors retain702 each:3102.

tau4=div(T)-4*ell=-2*r^7+15*r, and

W4=[T_r*d_r+T_v*d_v+tau4*I+ell*A*M_a+t*T_v*M_b]h4+(d_t+N_t)k4.

The full scaled identity is

A^4 DivP0 + A^3 DivP1 - A^2 Q1 + A^2 DivP2 - 2A Q2
+ A DivP3 - 3Q3 + W4 = A^4 S.

The next pole is coupled: (Ra-3I)Q3+W4|A=0=0.
No separate lower-sector tangency, old A2 secondary projection, or previous
family exclusion is imposed on P3,P2,P1,P0.

Imported structural sources are the A-denominator divisor/tangency/support
audit and coordinator's new order-four handoff. The earlier irreducibility
argument, generic b/Delta nonvanishing and support proof keep their original
scope. Pro's new source reconstruction checks the resulting operator at all
saved samples; it is not a replacement proof of those imported generic facts.

The necessary reduction also holds for homogeneous currents. A nonzero
3103-square augmented minor implies full rank of all3102 coefficient
columns. Hence no hidden kernel or redundant column defeats the finite-family
exclusion. This is not an inference from a deficient modular rank gap.
