# Imported structural dependency and its exact downstream use

This batch uses the existing bounded tangent parametrization from checkpoint148
and the coordinator's new top-pole argument. It does not rerun those checks.

Work over Q(r,v,t), at the generic irreducible A divisor. The parent proves
irreducibility by w=(rv-1)/r², r³A=w^6+r^6+1 and Eisenstein at r²+1.
The generic connection denominators b and Δ|a=0=b²(4bd-c²) are nonzero
on that divisor. The source M_b column is regular there. The residue is
Ra=[[0,-c/(6b)],[0,-1/3]], so det(Ra-2I)=14/3≠0.

For P0+P1/A+P2/A², the A^-3 coefficient is (Ra-2I)Q2,
Q2=A_rP2_r+A_vP2_v modulo A. P1 contributes at most order2, P0 at most
order1. Thus every solution, and every homogeneous kernel current, has Q2=0.

The parent tangent/support theorem applies to the same numerator box:
P2_r=Tr h2, P2_v=Tv h2, Tr=r²(r6+1),
Tv=r(2r6+1)v-(3r6+2). Each h2 component has r=-10..-6,v=0..1,t=0..2;
k2=P2_t retains r=-10..2,v,t=0..2. This is60+234=294 parameters.
Tr and Tv are coprime in the relevant Laurent polynomial ring and the map
is injective. The parent's exact proof and sparse injection are at
results/skew-A-denominator-audit-20261024/algebra/.

Consumed by the new search: retain all702 parameters in P0, all702 in P1,
and these294 in P2;1698 total. No coupled order-two constraint is imposed.
With ell=3r(r6-1), T(A)=ell A and div T=10r7+3r, the top zero-order
quotient term is div T-2ell=4r7+9r. This gives the displayed W2 operator.

The coordinator later reported a stronger necessary condition h2_second_row
divisible by v, backed by14 exact checks+3 mutations and a separate review.
It would reduce1698 to1683. It is explicitly UNUSED: the larger1698 family
already has full coefficient rank and a nonzero1699 augmented minor.

Evidence attribution: the new top-pole determinant is supplied reasoning,
the parent bounded tangent theorem is reused published evidence, and the
new quotient-rule matrix/minor and its independent reconstruction are fresh
executions in this packet. Coordinator-side new structural scripts/receipts
will accompany integration; no local execution count is claimed for them.
