**Degree six: bounded denominator exclusion for `mixed-biweight`.** The exact-rational packet reports that no degree-six certificate exists over $\mathbb C$, including the full numerator space and unrestricted $Q$.

The first-equation kernel has dimension $39=36+3$: the Jacobian space and three additional directions. After the Euler/$F$ gauge, all 38 parameters and 315 Koszul corrections are retained. Necessary second-equation identities reduce these parameters to five.

The degree-four multiplier matrix for the remaining five quadrics has rank $65/70$, so that rank calculation alone does not finish the exclusion. Its surviving locus has
$$a_0=a_1=a_3=a_4=s,\qquad a_2=t,\qquad 5t^2-8ts+8s^2=0.$$
The chart $s=0$ gives zero. On $s=1$, the two candidates have $t=(4\pm2\sqrt{-6})/5$. An exported coefficient functional annihilates all 462 $FS_6$ columns and all 315 Koszul corrections, but evaluates to one on the obstruction for each candidate. Equivalently, the correction rank is 742 and the augmented rank 743. Both candidates are therefore excluded.

[Argument, exact functional, output and reproduction commands](https://github.com/rbajaj5/hodge-lab/blob/b5d294e8efea1512d76c50acbe0039e4073dd2c8/notes/mixed-degree6-extra.md).

Together with the lower-degree calculation, the reported lower bound is $\deg D\ge7$. The instance remains unsolved. No conclusion about unrestricted higher degrees or Lean acceptance is claimed. Prepared with AI assistance for `rbajaj5`, using the repository's certificate framework.
