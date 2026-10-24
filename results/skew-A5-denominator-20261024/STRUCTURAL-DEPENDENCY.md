# Imported A-fifth top-pole argument

Consumed coordinator handoff: 7 new exact identities and 3 controls passed
in 2.250 seconds. Reported script SHA256:
bad3f26c1f1f07c944024b6acdfa91f0c4953951a3c8f434ebd66b24850e8d8c.
These are imported executions, not new Pro calculations. Earlier generic
divisor, bounded tangent module, support and source arguments are reused
with their existing hypotheses and were not rerun.

Let F=P0+P1/A+P2/A^2+P3/A^3+P4/A^4+P5/A^5, and
Qj=A_r*Pj_r+A_v*Pj_v. At generic A=0, the reused residue is
Ra=[[0,-c/(6b)],[0,-1/3]]. The highest pole has coefficient (Ra-5I)Q5.
The new determinant is80/3, so only P5 is necessarily tangent.

Reuse the bounded tangent parametrization
P5=(T_r*h5,T_v*h5,k5), with
T_r=r^2*(r^6+1), T_v=r*(2*r^6+1)*v-(3*r^6+2),
ell=3*r*(r^6-1), and T(A)=ell*A.
Each h5 component has30 monomials with m=-10,...,-6, n=0,1, k=0,1,2.
Each k5 component has117 monomials from the original box B.

Thus only the top sector is reduced from702 to294 parameters. The five
lower sectors each retain702: **294+3510=3804**, versus4212 originally.
In particular, previous A4 exclusion does not impose a restriction on the
changed lower residual in this family.

The new zero-order term is tau5=div(T)-5*ell=-5*r^7+18*r, and

W5=[T_r*d_r+T_v*d_v+tau5*I+ell*A*M_a+t*T_v*M_b]h5+(d_t+N_t)k5.

The full scaled equation is

A^5 DivP0 + A^4 DivP1 - A^3 Q1 + A^3 DivP2 - 2A^2 Q2
+ A^2 DivP3 - 3A Q3 + A DivP4 - 4Q4 + W5 = A^5 S.

Div includes the complete physical connection. The next pole stays coupled:
(Ra-4I)Q4+W5|A=0=0. No separate P4 tangency is imposed.

The imported highest-pole condition also applies to homogeneous currents.
If the proposed3805-square augmented minor is nonzero, it proves full rank
of the3804 coefficient columns, rules out a hidden operator kernel in this
necessary family, and excludes an inhomogeneous solution. Together with
the imported necessary restriction, it excludes the original finite family.
A deficient modular rank gap alone would not establish that conclusion.
