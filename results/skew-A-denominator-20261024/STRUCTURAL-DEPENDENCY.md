# Imported necessary restriction: provenance and explicit algebra

The coordinator supplied this theorem during the active batch and reported
16 exact author checks, two sign controls, and agreement by a separate local
checker. Those executions and their original receipts remain coordinator-side;
they are **not** claimed as executions by this Pro worker. This file records
the supplied theorem and the algebra used to consume it. No old generic
source/curve/trace calculation was replayed.

Let R=Q[r,r^-1,v,t] and B be the stated Laurent box. Consider all six flux
components F_i=L_i+P_i/A, with L_i,P_i in B and two compact rows. The scalar
spaces B and B/A have zero intersection: deg_v A=6, whereas a nonzero element
of B has degree at most2, so AL cannot belong to B for nonzero L in B.

## The generic A divisor and the necessary leading equation

With w=(rv-1)/r², r³A=w⁶+r⁶+1. This polynomial is Eisenstein in w at the
prime r²+1 of Q[r], because r⁶+1=(r²+1)(r⁴-r²+1), with the second factor
congruent to3 modulo r²+1. Thus A is irreducible in the Laurent chart.
The generic b and the discriminant restricted to A=0 are nonzero there,
since their degrees in v are smaller than6. With the literal pinned JSON's
sign convention, Delta|a=0=b²(4bd-c²); the opposite signed expression in
one relayed message has the same nonzero locus and does not change this argument.

The residue of M_a is

    R_a = [[0,-c/(6b)],[0,-1/3]],  det(R_a-I)=4/3.

M_b, M_c, M_d are regular at the generic A divisor. The leading A^-2 term
of Div_N(P/A) is (R_a-I)(A_r P_r+A_v P_v)/A². The source and Laurent-sector
operator have no double A pole. Consequently any solution, and any homogeneous
operator-kernel current in the original sum family, must satisfy

    A_r P_r+A_v P_v = 0 mod A

in each compact row. This is a necessary condition, not a solution or kernel.

## Low-v-degree parametrization

Set x=v-r^-1, C0=r³+r^-3 and H0=12r²+6r^-4. Then

    A=C0+r^-9*x⁶,  A_v=6r^-9*x⁵,
    A_r = H0 + A_v/r² - 9A/r.

Write P_r=p0+p1*x+p2*x² and S=P_v+P_r/r²=s0+s1*x+s2*x².
Reducing the necessary condition modulo A gives

    (H0*p0-6C0*s1) + (H0*p1-6C0*s2)x
      + H0*p2*x² + 6r^-9*s0*x⁵ = 0.

Hence p2=s0=0 and S=(H0/(6C0))*x*P_r. Equivalently

    P_r=T_r*h, P_v=T_v*h,
    T_r=r²(r⁶+1), T_v=r(2r⁶+1)v-(3r⁶+2).

T_r and T_v are coprime in R: modulo r⁶+1, T_v is 1-rv, so it has no
common factor with T_r. Their primitive pair therefore forces h to lie
in R, not to acquire an unallowed denominator. The original box implies:

- deg_v h<=1 and deg_t h<=2;
- the largest r exponent of T_r h is the largest exponent of h plus8,
  so max_r h<=-6;
- the lowest r term in T_v is the nonzero constant -2, so
  min_r h>=-10.

Thus h has30 monomials per compact row. P_t remains unrestricted in B,
117 per row. The denominator sector has294 necessary parameters, and with
the702 Laurent-sector parameters the joint search has996.

## Reduced operator and exact-kernel gate

T(A)=3r(r⁶-1)A. Multiplying the full equation by A gives

    [T_r partial_r+T_v partial_v+(7r⁷+6r)I
       +3r(r⁶-1) A M_a+t T_v M_b]h
       +(partial_t+N_t)P_t + A Div_N(L)
       = A*r^-4*M_b*e0/12.

The author assembled these columns by DIRECT quotient differentiation;
the checker used this reduced formula. Their independent entry agreement is
a new execution; the generic necessity theorem above is imported evidence.

The reduced coefficient matrix has full column rank996. Thus there is no
reduced operator kernel. Any original homogeneous current must obey the same
necessary pole restriction and hence belong to this reduced space, so its
coefficients also vanish. This accounts for original-family kernels without
inferring a characteristic-zero result from a rank-deficient modular gap.
