# Imported A-seventh highest-pole argument

Consumed coordinator-executed algebra handoff, frozen 2026-10-24 18:10:22 UTC:
seven new exact identities and three wrong-sign/order controls passed;
process 2.297 seconds, algebra 0.187 seconds, ten byte bindings.
Reported algebra source SHA256:
`aca70673f8a5273e56bbe4f60066102678c3a7157199c8fde29415455c7a1cab`.
Reported sparse injection 5616 x 5208 SHA256:
`4b3911f6010235533001c3a042b2106bee6a7282cbb0d677a0951095eff7221e`.
These executions and files belong to the coordinator. Pro consumes their
reasoning; it does not rerun prior source, divisor, tangent-module or support checks.

Write F=sum(j=0..7) Pj/A^j and Qj=A_r*Pj_r+A_v*Pj_v. At the reused generic
A=0 divisor, Ra=[[0,-c/(6b)],[0,-1/3]]. The highest pole is (Ra-7I)Q7.
Since det(Ra-7I)=154/3, **only P7** is forced tangent.

The reused bounded support theorem gives
P7=(T_r*h7,T_v*h7,k7), where T_r=r^2*(r^6+1),
T_v=r*(2*r^6+1)*v-(3*r^6+2), ell=3*r*(r^6-1), and T(A)=ell*A.
Each h7 component has 30 monomials: m=-10..-6,n=0..1,k=0..2.
Each k7 component has the original 117 monomials from B.

The necessary injection is 5616 x 5208. Top h7,k7 contribute 294 parameters.
P6,P5,P4,P3,P2,P1,P0 retain all 702 each: **4914 lower coefficients free**.
No lower tangency or previous exclusion is imposed on the changed residual.

The new zero-order term is tau7=div(T)-7*ell=-11*r^7+24*r, and

W7=[T_r*d_r+T_v*d_v+tau7*I+ell*A*M_a+t*T_v*M_b]h7+(d_t+N_t)k7.

The full scaled equation is

A^7 DivP0 + sum(j=1..6)[A^(7-j) DivPj - j A^(6-j) Qj] + W7 = A^7 S.

Div includes the entire physical connection. The next pole is coupled:
(Ra-6I)Q6+W7|A=0=0. Independent P6 tangency would discard allowed
cancellation and is not used.

The highest-pole condition applies to homogeneous currents too. A nonzero
5209-square augmented minor would establish full rank of all 5208 coefficient
columns and exclusion, without a hidden kernel or redundant-column loophole.
Together with the imported necessary restriction it excludes the original
finite family. A deficient modular rank gap alone would not establish this.
