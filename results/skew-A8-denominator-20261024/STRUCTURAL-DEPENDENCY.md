# Imported A-eighth highest-pole argument

Consumed coordinator-executed algebra handoff:one process ended
2026-10-24 18:25:55.326UTC,seven exact checks and three controls passed,
2.235seconds process/0.219seconds algebra,no failure or timeout.
Reported checker SHA256:
`b74eb6bd383d55e7c699866974e27e28196dc36c2db62c28507452ed4fbddfd2`.
Reported exact sparse injection is6318x5910 and preserves all5616 lower
coefficients. Reported injection SHA256:
`32dcdb1291e8ee2cc2703978f95a2b62d8e9a6d5295b8db48c6c37e5a10040a2`.
The original coordinator execution and its files are not Pro
runs. Prior source/divisor/bounded tangent/support results are reused.

Write F=sum(j=0..8)Pj/A^j and Qj=A_r*Pj_r+A_v*Pj_v. At the reused generic
A=0 divisor,Ra=[[0,-c/(6b)],[0,-1/3]]. Highest pole is(Ra-8I)Q8;
det(Ra-8I)=200/3,so **only P8** is forced tangent.

The reused bounded support theorem gives P8=(T_r*h8,T_v*h8,k8),where
T_r=r^2*(r^6+1),T_v=r*(2*r^6+1)*v-(3*r^6+2),ell=3*r*(r^6-1),
and T(A)=ell*A. Each h8 component has30 monomials,m=-10..-6,n=0..1,k=0..2;
each k8 component has117 original B monomials.

Top contribution60+234=294; P7,P6,P5,P4,P3,P2,P1,P0 contribute702 each.
**All5616 lower coefficients remain free.** The necessary family has5910
columns. No old exclusion or lower independent tangency is imposed.

tau8=div(T)-8ell=-14*r^7+27*r.

W8=[T_r*d_r+T_v*d_v+tau8*I+ell*A*M_a+t*T_v*M_b]h8+(d_t+N_t)k8.

Full scaled equation:

A^8 DivP0 + sum(j=1..7)[A^(8-j)DivPj-j*A^(7-j)Qj] + W8 = A^8 S.

Div includes the full physical connection. The next pole stays coupled:
(Ra-7I)Q7+W8|A=0=0. Imposing independent P7 tangency would discard allowed
cancellation and is not used.

The necessary condition also applies to homogeneous currents. A nonzero
5911-square augmented minor establishes rank5910 of the coefficient columns,
so neither hidden operator kernels nor redundant columns invalidate the
exclusion. Together with the imported necessary restriction,this excludes
the original finite family. A deficient modular rank gap would not suffice.
