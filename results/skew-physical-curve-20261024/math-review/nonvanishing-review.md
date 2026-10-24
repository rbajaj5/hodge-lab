# Read-only check of the proposed nonvanishing certificates

Executor: Pro curve_math_review AI. This is algebraic review only; no
symbolic checker or Lean command was executed by this reviewer.

## Cover derivative

Using v=r^-1+rw and a=(1+r^6+w^6)/r^3, the existing literal derivative is

    18*r^17 + 12*r^11 + 6*v*(v*r-1)^5 - 15*a*r^14.

On r != 0, v*r-1=r^2*w. Expanding and collecting yields

    3*r^17 - 3*r^11 - 9*r^11*w^6 + 6*r^9*w^5.

Its polynomial value at r=w=1 is -3, so this polynomial is nonzero. The
injective independent-base polynomial map carries it to a nonzero element
of the realized field. This is a polynomial nonzero certificate, not a
specialization map from the entire rational-function field.

## Cubic Delta

Write A=1+r^6+w^6, B=t*(1+r^2*w), C=t*(1-t^2), and D=1+t^6. The new
physical cubic coefficients are a=A/r^3, b=B/r, c=C/7, d0=D. For

    Delta = 27*a^2*d0^2 -18*a*b*c*d0 +4*a*c^3 +4*b^3*d0 -b^2*c^2,

multiplication by343*r^6 gives exactly

    9261*A^2*D^2 -882*A*B*C*D*r^2 +4*A*C^3*r^3
      +1372*B^3*D*r^3 -7*B^2*C^2*r^4.

The five integer factors are respectively 27*343, -18*49, 4, 4*343,
and -343/49. The powers of r follow from denominators r^6, r^4, r^3,
r^3 and r^2 in the original five terms.

Evaluation of this CLEARED polynomial at all base variables zero gives
9261. That witnesses that the polynomial is not identically zero. The
zero evaluation is not a physical chart point (r=0), and no specialization
of the rational-function field at r=0 is used. The formal base embedding
is injective and its actual generic r is nonzero, so the cleared identity
then proves Delta nonzero in the constructed field.

If the writer compiles these two certificates, the fixed realization's
f_r and Delta hypotheses are discharged, rather than left as concrete-field
assumptions. The old generic normalization theorem can then be instantiated
without adding an unproved chart-nonzero premise. This does not prove any
universal statement about all specializations; singular or zero-denominator
specializations remain outside the result.
