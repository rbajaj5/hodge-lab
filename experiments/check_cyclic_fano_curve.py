"""Independent exact audit of the new cyclic-triple-fano covering-family seed.

No imports from the primary construction or earlier Hodge Lab algebra modules.
The source target is read directly from the readonly fresh upstream checkout.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

import sympy as sp

HERE = Path(__file__).resolve().parents[1] / "results/cyclic-fano-curve"
SOURCE = HERE / "source/instance.rec"
PACKET = HERE / "cyclic-free-curve.json"
TARGET = HERE / "target.json"
EXPECTED_SOURCE_SHA = "d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c"
VARS = sp.symbols("X0 X1 X2 Y0 Y1 Y2")
X0, X1, X2, Y0, Y1, Y2 = VARS
Z, s, t = sp.symbols("Z s t")
I = sp.I


def normalized_sha(path):
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def read_expression(name):
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    pos = next(i for i, line in enumerate(lines) if line.startswith(name + ":"))
    expr = lines[pos].split(":", 1)[1].strip()
    for line in lines[pos + 1 :]:
        if not line.startswith("  "):
            break
        expr += " " + line.strip()
    return sp.Poly(sp.sympify(expr, locals=dict(zip(map(str, VARS), VARS))), *VARS,
                   domain=sp.QQ).as_expr()


def binary_coefficients(expr, degree):
    poly = sp.Poly(sp.expand(expr), s, t)
    assert all(sum(m) == degree for m in poly.monoms()) or poly.is_zero
    return sp.Matrix([poly.coeff_monomial(s ** (degree-k) * t ** k)
                      for k in range(degree+1)])


def serialize_matrix(matrix):
    return [[str(sp.simplify(x)) for x in row] for row in matrix.tolist()]


def expect_failure(function):
    try:
        function()
    except AssertionError:
        return 1
    raise AssertionError("mutation was not detected")


def assert_line(G, coords, line):
    assert sp.expand(G.subs(dict(zip(coords, line)), simultaneous=True)) == 0


def assert_minor(matrix, columns, value):
    assert sp.simplify(matrix[:, columns].det() - value) == 0


def assert_matrix(actual, expected):
    assert actual.shape == expected.shape
    assert sp.simplify(actual - expected) == sp.zeros(*actual.shape)


def assert_rank(matrix, expected):
    assert matrix.rank() == expected


def decode_matrix(raw):
    return sp.Matrix([[sp.Rational(x[0]) + I*sp.Rational(x[1]) for x in row]
                      for row in raw])


assert __debug__, "Run without -O"
assert normalized_sha(SOURCE) == EXPECTED_SOURCE_SHA
frozen = json.loads(TARGET.read_text(encoding="utf-8"))
packet = json.loads(PACKET.read_text(encoding="utf-8"))
assert frozen["instance"] == packet["instance"] == "cyclic-triple-fano"
assert frozen["upstream_commit"] == packet["upstream_commit"] == "d96911d725077e66a8f10848908be01a643b1714"
assert frozen["upstream_source_sha256"]["data/cyclic-triple-fano/instance.rec"] == EXPECTED_SOURCE_SHA
assert packet["raw_instance_sha256"] == EXPECTED_SOURCE_SHA
assert packet["frozen_target_sha256"] == normalized_sha(TARGET)
assert packet["source_sha256"] == frozen["upstream_source_sha256"]
F = read_expression("F")
A = read_expression("A")
assert read_expression("q") == 1
for data in (frozen["target"], packet["target"]):
    assert int(data["q"]) == 1
    assert sp.expand(sp.sympify(data["F"], locals=dict(zip(map(str,VARS),VARS))) - F) == 0
    assert sp.expand(sp.sympify(data["A"], locals=dict(zip(map(str,VARS),VARS))) - A) == 0
terms = sp.Poly(F, *VARS, domain=sp.QQ).terms()
assert all(m[2] % 3 == 0 for m, c in terms)
G = sp.expand(sum(c * X0**m[0] * X1**m[1] * Z**(m[2]//3)
                  * Y0**m[3] * Y1**m[4] * Y2**m[5] for m, c in terms))
coords = (X0, X1, Z, Y0, Y1, Y2)
weights = (1, 1, 3, 1, 1, 1)
assert sp.expand(G.subs(Z, X2**3) - F) == 0
assert all(sum(w*e for w, e in zip(weights, m)) == 6
           for m in sp.Poly(G, *coords).monoms())
density = X0 * Y0**3 / 3
assert sp.expand(3*X2**2*density - A) == 0
line = (0, s, 0, I*s, t, I*t)
assert_line(G, coords, line)
partials = [sp.expand(sp.diff(G, c).subs(dict(zip(coords, line)), simultaneous=True))
            for c in coords]
expected_partials = [5*I*s*t**4/7, 6*s**5, 5*I*s**2*t/7,
                     6*I*s**5, 6*t**5, 6*I*t**5]
assert partials == expected_partials

# H0(O^5 + O(2)) -> H0(O(5)); ordinary binary monomials, no binomial factors.
column_labels = ["dX0", "dX1", "dY0", "dY1", "dY2", "s^2 dZ", "s t dZ", "t^2 dZ"]
columns = [partials[k] for k in (0, 1, 3, 4, 5)]
columns += [partials[2]*m for m in (s**2, s*t, t**2)]
matrix = sp.Matrix.hstack(*[binary_coefficients(c, 5) for c in columns])
assert matrix.shape == (6, 8)
minor_columns = (0, 1, 3, 5, 6, 7)
minor = sp.simplify(matrix[:, minor_columns].det())
assert abs(minor) == sp.Rational(22500, 2401)
assert matrix.rank() == 6
gram = sp.simplify(matrix * matrix.conjugate().T)
assert gram == sp.diag(72, sp.Rational(25, 49), sp.Rational(25, 49),
                      sp.Rational(25, 49), sp.Rational(25, 49), 72)
assert gram.det() == 72**2*sp.Rational(25, 49)**4
small, large = sp.Rational(25,49), sp.Integer(72)
projector_small = (large*sp.eye(6)-gram)/(large-small)
projector_large = (gram-small*sp.eye(6))/(large-small)
for projector, value in ((projector_small,small),(projector_large,large)):
    assert projector*projector == projector
    assert projector.conjugate().T == projector
    assert gram*projector == value*projector
assert projector_small*projector_large == sp.zeros(6)
assert projector_small + projector_large == sp.eye(6)
gram_inverse = projector_small/small + projector_large/large
assert gram*gram_inverse == sp.eye(6)
right_inverse = matrix.conjugate().T*gram_inverse
assert matrix*right_inverse == sp.eye(6)
lower_bound_remainder=gram-small*sp.eye(6)
assert lower_bound_remainder == sp.diag(large-small,0,0,0,0,large-small)
assert all(x>=0 for x in lower_bound_remainder.diagonal())
assert right_inverse.conjugate().T*right_inverse == gram_inverse
assert max(gram_inverse.diagonal()) == sp.Rational(49,25)
assert sp.sqrt(max(gram_inverse.diagonal())) == sp.Rational(7,5)

# These exact columns use the producer's natural weighted order only for comparison.
natural_matrix = matrix[:,[0,1,5,6,7,2,3,4]]
assert_matrix(decode_matrix(packet["twisted_map"]["matrix"]), natural_matrix)
assert packet["twisted_map"]["rank"] == 6
assert_minor(natural_matrix, packet["twisted_map"]["selected_columns"],
             sp.Rational(packet["twisted_map"]["minor_determinant"]))
assert_matrix(decode_matrix(packet["spectral"]["gram_matrix"]), gram)
assert_matrix(decode_matrix(packet["spectral"]["gram_inverse"]), gram_inverse)
assert_matrix(decode_matrix(packet["spectral"]["right_inverse"]),
              natural_matrix.conjugate().T*gram_inverse)
assert_matrix(decode_matrix(packet["spectral"]["small_eigenspace_projector"]),projector_small)
assert_matrix(decode_matrix(packet["spectral"]["large_eigenspace_projector"]),projector_large)
assert gram_inverse == ((small+large)*sp.eye(6)-gram)/(small*large)
assert_matrix(decode_matrix(packet["spectral"]["lower_bound_remainder"]),lower_bound_remainder)
assert_matrix(decode_matrix(packet["spectral"]["right_inverse_gram"]),gram_inverse)
assert sp.Rational(packet["spectral"]["right_inverse_operator_norm"]) == sp.Rational(7,5)
assert sp.Rational(packet["spectral"]["matrix_full_row_rank_perturbation_radius"]) == sp.Rational(5,7)
assert sp.Rational(packet["spectral"]["gram_invertibility_perturbation_radius"]) == sp.Rational(25,49)
assert packet["spectral"]["eigenvalues"] == {"72":2,"25/49":4}
assert sp.expand(sp.sympify(packet["quotient_equation"],locals=dict(zip(map(str,coords),coords))) - G) == 0
assert [sp.sympify(x,locals={"s":s,"t":t}) for x in packet["curve"]] == list(line)
assert packet["weights"] == list(weights)

# Good reduction at five independently verifies projective smoothness of F.
def reduce_at_five(expr):
    return sp.Poly(sum((int(coef.p)*pow(int(coef.q),-1,5)%5)*sp.prod(z**k for z,k in zip(VARS,mon))
                       for mon,coef in sp.Poly(expr,*VARS,domain=sp.QQ).terms()),
                   *VARS, modulus=5)
for variable in VARS:
    assert reduce_at_five(sp.diff(F,variable)) == sp.Poly(variable**5,*VARS,modulus=5)

# Complete untwisted incidence and its four-dimensional marked evaluation.
untwisted_polynomials=[]
untwisted_components=[]
for k,w in enumerate(weights):
    for ell in range(w+1):
        untwisted_polynomials.append(partials[k]*s**(w-ell)*t**ell)
        untwisted_components.append(k)
untwisted=sp.Matrix.hstack(*[binary_coefficients(x,6) for x in untwisted_polynomials])
assert untwisted.shape == (7,14) and untwisted.rank() == 7
assert_matrix(decode_matrix(packet["untwisted_map"]["matrix"]),untwisted)
kernel=decode_matrix(packet["untwisted_map"]["incidence_kernel_basis"])
assert kernel.shape == (14,7) and kernel.rank() == 7
assert untwisted*kernel == sp.zeros(7,7)
point=[sp.sympify(x).subs({s:1,t:1}) for x in line]
untwisted_evaluation=sp.Matrix([[int(component==k)-weights[k]*point[k]*int(component==1)
                               for component in untwisted_components] for k in (0,2,3,4,5)])
assert_matrix(decode_matrix(packet["untwisted_map"]["affine_evaluation_at_1_1"]),
              untwisted_evaluation*kernel)
assert (untwisted_evaluation*kernel).rank() == 4

# Separate diagnostic family: its parameter changes F, not the protected target.
coupling=sp.Symbol("coupling",real=True)
fermat=sum(z**6 for z in (X0,X1,Y0,Y1,Y2))+Z**2
diagnostic=sp.expand(fermat+(G-fermat)*7*coupling/5)
assert_line(diagnostic,coords,line)
diagnostic_partials=[sp.expand(sp.diff(diagnostic,z).subs(dict(zip(coords,line)),simultaneous=True)) for z in coords]
diagnostic_columns=[diagnostic_partials[k] for k in (0,1,3,4,5)]
diagnostic_columns += [diagnostic_partials[2]*m for m in (s**2,s*t,t**2)]
diagnostic_matrix=sp.Matrix.hstack(*[binary_coefficients(x,5) for x in diagnostic_columns])
assert sp.simplify(diagnostic_matrix*diagnostic_matrix.conjugate().T) == sp.diag(72,coupling**2,coupling**2,coupling**2,coupling**2,72)
assert diagnostic_matrix.subs(coupling,0).rank() == 2

# Three-parameter local algebraic family, obtained by fixing X1=s and Y1=t.
a, b, c, y, d, e, f, g, h, j = sp.symbols("a b c y d e f g h j")
parameters = (a, b, c)
unknowns = (y, d, e, f, g, h, j)
family = (a*s+b*t, s, f*s**3+g*s**2*t+h*s*t**2+j*t**3,
          y*s+c*t, t, d*s+e*t)
family_equation = sp.expand(G.subs(dict(zip(coords, family)), simultaneous=True))
equations = sp.Matrix([sp.expand(family_equation).coeff(s, 6-k).coeff(t, k)
                       for k in range(7)])
base = {a:0, b:0, c:0, y:I, d:0, e:I, f:0, g:0, h:0, j:0}
assert equations.subs(base) == sp.zeros(7, 1)
jacobian = equations.jacobian(unknowns).subs(base)
parameter_jacobian = equations.jacobian(parameters).subs(base)
jacobian_determinant = sp.simplify(jacobian.det())
assert jacobian_determinant == -135000*I/2401
implicit_derivatives = sp.simplify(-jacobian.inv()*parameter_jacobian)
assert jacobian*implicit_derivatives + parameter_jacobian == sp.zeros(7, 3)
family_jacobian = (sp.Matrix(family).jacobian(parameters)
                   + sp.Matrix(family).jacobian(unknowns)*implicit_derivatives).subs(base)
assert family_jacobian[:,0] == sp.Matrix([s,0,-t**3,0,0,0])
assert family_jacobian[:,1] == sp.Matrix([t,0,0,0,0,-5*s/42])
assert family_jacobian[:,2] == sp.Matrix([0,0,-42*s**3/5,t,0,0])
# On X1=1 use (X0,Z,Y0,Y1,Y2) as ambient affine coordinates.
affine_rows = (0,2,3,4,5)
curve_direction = sp.Matrix(line).diff(t).subs({s:1,t:1})
evaluation_jacobian = sp.Matrix.hstack(family_jacobian.subs({s:1,t:1}), curve_direction)
evaluation_jacobian = evaluation_jacobian[list(affine_rows),:]
assert evaluation_jacobian.rank() == 4
assert evaluation_jacobian[:4,:].det() == 1
target_first_variation = sp.expand(sum(sp.diff(density, coord).subs(dict(zip(coords,line)), simultaneous=True)
                                       * family_jacobian[k,0] for k,coord in enumerate(coords)))
assert target_first_variation == -I*s**4/3
local=packet["local_family"]
family_lookup={str(x):x for x in parameters+unknowns+(s,t)}
assert local["free_parameters"] == list(map(str,parameters))
assert local["dependent_parameters"] == list(map(str,unknowns))
assert [sp.sympify(x,locals=family_lookup) for x in local["curve"]] == list(family)
assert len(local["coefficient_equations"]) == 7
for raw,computed in zip(local["coefficient_equations"],equations):
    assert sp.expand(sp.sympify(raw,locals=family_lookup)-computed) == 0
assert_matrix(decode_matrix(local["dependent_Jacobian"]),jacobian)
assert_matrix(decode_matrix(local["free_Jacobian"]),parameter_jacobian)
assert_matrix(decode_matrix(local["dependent_tangent_matrix"]),implicit_derivatives)
assert_matrix(decode_matrix(local["evaluation_matrix_at_base_r_1"]),evaluation_jacobian)
assert local["evaluation_rank"] == 4
rawdet=local["dependent_Jacobian_determinant"]
assert sp.Rational(rawdet[0])+I*sp.Rational(rawdet[1]) == jacobian_determinant
rawminor=local["evaluation_minor"]
assert evaluation_jacobian[local["evaluation_minor_rows"],:].det() == sp.Rational(rawminor[0])+I*sp.Rational(rawminor[1])

mutations = 0
mutations += expect_failure(lambda: assert_line(G, coords, (0,s,0,I*s,t,2*I*t)))
mutations += expect_failure(lambda: assert_minor(matrix, minor_columns, minor+1))
bad = matrix.copy()
bad[:,5] = sp.zeros(6,1)
mutations += expect_failure(lambda: assert_minor(bad, minor_columns, minor))
mutated_gram=sp.Matrix(gram);mutated_gram[0,0]+=1
mutations += expect_failure(lambda: assert_matrix(mutated_gram,gram))
mutated_jacobian=sp.Matrix(jacobian);mutated_jacobian[0,0]+=1
mutations += expect_failure(lambda: assert_matrix(mutated_jacobian,jacobian))
mutated_evaluation=sp.Matrix(evaluation_jacobian);mutated_evaluation[:,3]=sp.zeros(5,1)
mutations += expect_failure(lambda: assert_rank(mutated_evaluation,4))

result = {
    "schema": "new-atlas-cyclic-free-line-independent-v1",
    "status": "PASS",
    "source_commit": "d96911d725077e66a8f10848908be01a643b1714",
    "source_file": "data/cyclic-triple-fano/instance.rec",
    "source_lf_sha256": normalized_sha(SOURCE),
    "checker_lf_sha256": normalized_sha(Path(__file__)),
    "primary_packet_lf_sha256": normalized_sha(PACKET),
    "frozen_target_lf_sha256": normalized_sha(TARGET),
    "source_bindings_F_A_q_verified": True,
    "primary_packet_exact_comparisons":["target F,A,q", "quotient and curve", "twisted derivative", "Hermitian Gram and projectors", "Gram inverse and right inverse", "untwisted derivative and full kernel", "marked evaluation", "all seven local-family equations", "dependent and free Jacobians", "implicit tangent matrix", "local marked evaluation matrix and minor"],
    "smooth_reduction_prime":5,
    "smooth_reduction_partials":[str(z**5) for z in VARS],
    "field": "Q(i), i^2=-1; exact SymPy arithmetic",
    "quotient_coordinates": list(map(str, coords)),
    "quotient_weights": list(weights),
    "G": str(G),
    "density": str(density),
    "density_pullback_verified": True,
    "curve": list(map(str,line)),
    "restricted_partials": list(map(str,partials)),
    "basepoint_free_reason": "X1=s and Y1=t have no common projective zero",
    "ambient_vertex_avoided": True,
    "twisted_derivative": {
        "source": "H0(O^5 plus O(2))", "target": "H0(O(5))",
        "row_basis": [str(s**(5-k)*t**k) for k in range(6)],
        "column_basis": column_labels,
        "matrix": serialize_matrix(matrix),
        "rank": 6, "minor_columns": list(minor_columns), "minor": str(minor),
        "hermitian_gram": serialize_matrix(gram),
        "gram_eigenvalues": [["72",2],["25/49",4]],
        "spectral_projector_small":serialize_matrix(projector_small),
        "spectral_projector_large":serialize_matrix(projector_large),
        "projector_ranks":[projector_small.rank(),projector_large.rank()],
        "gram_inverse":serialize_matrix(gram_inverse),
        "right_inverse_our_column_order":serialize_matrix(right_inverse),
        "exact_projector_and_right_inverse_identities_verified":True,
        "lower_bound_remainder":serialize_matrix(lower_bound_remainder),
        "right_inverse_gram":serialize_matrix(gram_inverse),
        "right_inverse_operator_norm":"7/5",
        "matrix_perturbation_sufficient_radius":"5/7",
        "gram_perturbation_sufficient_radius":"25/49",
        "perturbation_scope":"For coefficient operator 2-norm: ||E||<5/7 implies ||ER||<1, so R(I+ER)^-1 is a right inverse of M+E. This does not assert that perturbed coefficients describe a curve on the fixed hypersurface.",
        "spectral_scope": "Coefficient Gram matrix in these monomial bases; not an intrinsic geometric spectrum"
    },
    "untwisted_incidence":{"shape":[7,14],"rank":7,"complete_kernel_rank":7,"evaluation_rank":4},
    "auxiliary_coupling_diagnostic":{"gram_diagonal":["72","coupling^2","coupling^2","coupling^2","coupling^2","72"],"rank_at_zero":2,"fixed_target_coupling":"5/7","scope":"A separate family varying F; no alteration of the protected target"},
    "three_parameter_family": {
        "coordinates": list(map(str,family)), "parameters": list(map(str,parameters)),
        "unknowns": list(map(str,unknowns)),
        "equations_s6_to_t6": list(map(str,equations)),
        "basepoint": {str(k):str(v) for k,v in base.items()},
        "unknown_jacobian": serialize_matrix(jacobian),
        "unknown_jacobian_determinant": str(jacobian_determinant),
        "implicit_first_derivatives": serialize_matrix(implicit_derivatives),
        "evaluation_jacobian_at_s_t_1": serialize_matrix(evaluation_jacobian),
        "evaluation_rank": 4,
        "evaluation_minor_rows": [0,1,2,3], "evaluation_minor": "1",
        "density_first_variation_in_a": str(target_first_variation),
        "scope": "A smooth local algebraic incidence component with dominant generically finite marked evaluation; graph boundaries and support equation are not yet computed"
    },
    "geometric_reason": [
        "The quotient avoids the sole weighted ambient vertex because G=Z^2 there; smoothness follows from the source smoothness and the finite cover.",
        "The weighted Euler sequence twisted by O(-1) identifies its tangent global sections with H0(O^5 plus O(2)), since H0 and H1 of O(-1) vanish.",
        "The displayed rank-six normal derivative implies H1(phi^*T_W(-1))=0. The splitting theorem on P1 then makes phi free.",
        "After fixing X1=s and Y1=t, the seven coefficient equations have an invertible unknown Jacobian. Their component through the displayed point is smooth of dimension three.",
        "The marked evaluation derivative has rank four, so this component supplies a dominant, generically finite family after taking a suitable smooth affine open.",
        "No support equation, rational primitive, cleared certificate, or Lean proof has been constructed."
    ],
    "negative_controls_rejected": mutations
}
out = Path(sys.argv[1]) if len(sys.argv)>1 else HERE / "independent-validation.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8", newline="\n")
print(json.dumps({"status":"PASS", "twisted_rank":6, "minor":str(minor),
                  "family_jacobian":str(jacobian_determinant), "evaluation_rank":4,
                  "negative_controls":mutations, "output":str(out)}))
