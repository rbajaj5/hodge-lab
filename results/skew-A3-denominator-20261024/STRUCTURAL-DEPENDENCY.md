# Imported highest-pole reduction, with lower sectors coupled

This batch reuses the published A-divisor irreducibility, residue, bounded
tangent module and support checks. None of those calculations is rerun.
The coordinator supplies the new A-cubed operator and local minimal checks;
those are credited as imported reasoning/evidence, not this worker's executions.

Let F=P0+P1/A+P2/A²+P3/A³, with all six scalar numerator components in
B=span_Q{r^m v^n t^k:-10≤m≤2,0≤n,k≤2}. The common denominator A³ gives
leading v-degree bands18–20,12–14,6–8,0–2, proving the2808-parameter sum
is direct. This assertion concerns input independence, not operator kernels.

At the generic irreducible A divisor, reuse
Ra=[[0,-c/(6b)],[0,-1/3]], regularity of Mb,Mc,Md and the source,
and the nonzero generic b and Delta|a=0=b²(4bd-c²).
The new highest pole is order4 with coefficient (Ra-3I)Q3,
Q3=A_r P3_r+A_v P3_v modulo A. Since det(Ra-3I)=10, every solution
and every homogeneous kernel current must have Q3=0 modulo A.
Lower sectors have at most order3 and cannot cancel that highest pole.

The established bounded tangent parametrization is
P3=(Tr h3,Tv h3,k3), Tr=r²(r6+1),
Tv=r(2r6+1)v-(3r6+2). Each h3 component has r=-10..-6,v=0..1,t=0..2;
each k3 component lies in B. There are60+234=294 top parameters.
Keep all702 coefficients of EACH P2,P1,P0, so the necessary family is2400.
No lower tangency and no separately applied A-squared projection is imposed.

With ell=3r(r6-1), the reused identity T(A)=ell A gives
tau3=div(T)-3ell=(10r7+3r)-3ell=r7+12r. Thus

W3=[Tr*partial_r+Tv*partial_v+tau3*I+ell*A*Ma+t*Tv*Mb]h3
   +(partial_t+Nt)k3.

The exact A³-scaled equation is

A³ Div_N(P0)+A² Div_N(P1)-A Q1+A Div_N(P2)-2 Q2+W3=A³ S,

where Qj=A_r Pj_r+A_v Pj_v and S=r^-4 Mb e0/12. The next pole condition
is coupled: (Ra-2I)Q2+W3|A=0=0. The top residual can cancel the P2 pole.
The search retains this cancellation by keeping P2 unrestricted, rather
than replacing the coupled condition with two separate vanishing conditions.

The author's new implementation differentiates every quotient directly.
The separate new checker uses this reduced operator. The structural
dependency remains explicitly attributed, including for the homogeneous
kernel argument; file binding is not counted as mathematical verification.
