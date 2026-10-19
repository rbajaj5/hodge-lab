#!/usr/bin/env python3
"""Complete degree-6 E1 + E2 exclusion analysis and figure generator for one-reflection-skew."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fresh_instance_e1 as e1
import fresh_instance_degree6 as d6

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'one-reflection-skew-degree6'
e1.OUT = OUT
d6.OUT = OUT

INSTANCE = 'one-reflection-skew'

# Hodge Lab publication palette
INK = '#17323B'
TEAL = '#166A70'
CORAL = '#CA584C'
GOLD = '#D5AB3E'
SLATE = '#53666D'
PAPER = '#FAFAF5'
PANEL = '#FFFFFF'
GRID = '#D9D6CA'

_ORIG_TARGET = e1.target


def _custom_target(instance):
    if instance == 'one-reflection-skew':
        fields = {
            'F': 'X0**6 + X1**6 + X2**6 + Y0**6 + Y1**6 + Y2**6 + X0**3*X1*Y0*Y1 + X1**3*X2*Y0*Y1 + (1/7)*X0*X1*Y0*Y1*(Y0**2 - Y1**2)',
            'A': 'X0**3*Y0**3',
            'q': '1',
        }
        F, A = e1.parse_poly(fields['F']), e1.parse_poly(fields['A'])
        bindings = {
            'upstream_commit': 'f63ca5eb45e29d184323b165e2d03692c8719ca1',
            'upstream_instance_rec_sha256': '10d66957c87e65d0380fd1b4b65c3b6599c7224d8983134bf982e897bc3b5816',
        }
        return F, A, fields, bindings
    return _ORIG_TARGET(instance)


e1.target = _custom_target


def cubic_multipliers(equations, pairs):
    """Bounded degree-three Macaulay rows on the 5 gauged diagonal parameters."""
    columns = e1.monos(3, 5)
    lookup = {m: i for i, m in enumerate(columns)}
    rows, labels = [], []
    for r, eq in enumerate(equations):
        for mon in e1.monos(1, 5):
            out = {}
            for c, v in eq.items():
                i, j = pairs[c]
                exponent = list(mon)
                exponent[i] += 1
                exponent[j] += 1
                out[lookup[tuple(exponent)]] = v
            rows.append(out)
            labels.append((r, mon))
    basis = e1.column_basis(rows)
    witnesses, unresolved = [], []
    for a in range(5):
        mon = tuple(3 if i == a else 0 for i in range(5))
        target = {lookup[mon]: e1.Q(1)}
        rem, combo = e1.reduce_vector(target, basis, {})
        if rem:
            unresolved.append(a)
            continue
        combo = {r: -c for r, c in combo.items()}
        assert e1.linear_combination(rows, combo) == target
        witnesses.append({
            'parameter': a,
            'power': 3,
            'multipliers': [[labels[r][0], list(labels[r][1]), str(c)] for r, c in sorted(combo.items())],
        })
    return {
        'degree': 3,
        'coefficient_columns': len(columns),
        'multiplier_rows': len(rows),
        'row_rank': len(basis),
        'identities': witnesses,
        'unresolved_parameters': unresolved,
    }


def run_pipeline(recompute: bool = False):
    OUT.mkdir(parents=True, exist_ok=True)
    e1path = OUT / INSTANCE / 'degree-6.json'
    e2path = OUT / INSTANCE / 'degree-6-e2.json'
    diagpath = OUT / INSTANCE / 'degree-6-diagonal.json'

    if recompute or not e1path.exists():
        print(">>> Stage 1: Complete E1 at degree 6", flush=True)
        d6.worker(INSTANCE)
    d6.verify([INSTANCE])

    if recompute or not e2path.exists():
        print(">>> Stage 2: Hessian E2 cascade in S_12 / J_12", flush=True)
        start = time.perf_counter()
        packet = json.loads(e1path.read_text(encoding='utf-8'))
        assert packet['dimensions']['denominator_kernel_dimension'] == packet['gauge']['J6_rank'] == 36
        rows, _, _, jac, _, target, bindings = e1.matrices(INSTANCE, 6)
        jb = e1.column_basis(jac, track=False)
        syzygies = d6.quadratic_koszul(INSTANCE)
        assert all(not e1.linear_combination(jac, s) for s in syzygies)
        syzygy_rank = len(e1.column_basis(syzygies, track=False))
        assert syzygy_rank == len(jac) - len(jb) == 315
        parameters, pairs, cols = d6.cycle_hessian_columns(INSTANCE)
        residual = [e1.reduce_vector(c, jb)[0] for c in cols]
        steps, allowed = [], list(range(35))
        while allowed:
            step = d6.square_step(allowed, pairs, residual, jb, jac, cols)
            steps.append(step)
            print(json.dumps({
                'instance': INSTANCE,
                'E2_step': len(steps),
                'allowed': len(allowed),
                'rank': step['quotient_rank'],
                'forced_squares': [w['parameter'] for w in step['forced_squares']],
            }), flush=True)
            if not step['forced_squares']:
                break
            allowed = step['unresolved_parameters']

        data = {
            'schema': 'fresh-instance-degree6-hessian-v1',
            'instance': INSTANCE,
            'target': target,
            'source_sha256': bindings,
            'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
            'degree6_E1_sha256': e1.sha(e1path),
            'gauge': 'L=MZ; replace M by M-M55*I, D by D-6*M55*F, N by N-M55*A*Z; then M55=0.',
            'parameters': [[e1.NAMES[i], e1.NAMES[j]] for i, j in parameters],
            'quadratic_column_pairs': pairs,
            'dimensions': {
                'coefficient_rows': len(rows),
                'jacobian_rank': len(jb),
                'Koszul_fields': len(syzygies),
                'Koszul_rank': syzygy_rank,
                'numerator_kernel_dimension': len(jac) - len(jb),
                'parameters_after_F_gauge': 35,
                'quadratic_columns': len(cols),
            },
            'steps': steps,
            'remaining_parameters': allowed,
            'degree6_excluded': not allowed,
            'matrix_plot': {
                'residual_entries': [[r, c, str(v)] for c, col in enumerate(residual) for r, v in sorted(col.items())]
            },
            'elapsed_seconds': time.perf_counter() - start,
            'scope': 'Necessary Hessian quotient after complete E1 and Euler/F gauge. A surviving parameter is not a certificate. No higher-degree conclusion.',
        }
        e1.write_json(e2path, data)
    d6.verify_e2(INSTANCE)

    if recompute or not diagpath.exists():
        print(">>> Stage 3: Full diagonal E2 with 315 Koszul corrections", flush=True)
        start_diag = time.perf_counter()
        rows_d, corrections, pairs_d, quadratics = d6.diagonal_maps(INSTANCE)
        cb = e1.column_basis(corrections, track=False)
        residual_d = [e1.reduce_vector(c, cb)[0] for c in quadratics]
        rowkeys = sorted(set().union(*(set(c) for c in residual_d)))
        eq = [{j: c[r] for j, c in enumerate(residual_d) if r in c} for r in rowkeys]
        rb = e1.column_basis(eq)
        consequences = []
        for pivot, (coefficients, combo) in sorted(rb.items()):
            raw = {rowkeys[k]: v for k, v in combo.items()}
            dual = e1.quotient_dual(raw, cb)
            assert all(e1.dot(dual, c) == 0 for c in corrections)
            assert {j: e1.dot(dual, c) for j, c in enumerate(quadratics) if e1.dot(dual, c)} == coefficients
            consequences.append({
                'pivot': pivot,
                'quadratic_coefficients': e1.pack(coefficients),
                'functional': e1.pack(dual),
            })
        active = [j for j, (a, b) in enumerate(pairs_d) if a < 5 and b < 5]
        gauged_pairs = [pairs_d[j] for j in active]
        active_lookup = {j: i for i, j in enumerate(active)}
        gauged_equations = [
            {active_lookup[j]: v for j, v in e1.unpack(item['quadratic_coefficients']).items() if j in active_lookup}
            for item in consequences
        ]
        powers = d6.quartic_multipliers(gauged_equations, gauged_pairs)
        _, _, target, bindings = e1.target(INSTANCE)
        diag_data = {
            'schema': 'fresh-instance-degree6-diagonal-v1',
            'instance': INSTANCE,
            'target': target,
            'source_sha256': bindings,
            'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
            'hessian_packet_sha256': e1.sha(e2path),
            'gauge': 'a5=0 after D -> D-6*a5*F and N -> N-a5*A*Z; an admissible D cannot become zero.',
            'correction_column_order': 'F times degree6 monomials, then i=0..5, Koszul pair j<k, quadratic monomial; products a_i*t_k relaxed independently.',
            'dimensions': {
                'coefficient_rows': len(rows_d),
                'correction_columns': len(corrections),
                'correction_rank': len(cb),
                'quadratic_columns': len(quadratics),
                'necessary_quadratic_rank': len(rb),
            },
            'quadratic_column_pairs': pairs_d,
            'consequences': consequences,
            'gauged_column_pairs': gauged_pairs,
            'gauged_equations': [e1.pack(eq) for eq in gauged_equations],
            'quartic_search': powers,
            'degree6_excluded': not powers['unresolved_parameters'],
            'matrix_plot': {
                'residual_entries': [[r, c, str(v)] for c, col in enumerate(residual_d) for r, v in sorted(col.items())]
            },
            'elapsed_seconds': time.perf_counter() - start_diag,
            'scope': 'Necessary full E2 consequences with all 315 numerator corrections and unrestricted quotient retained before independent-product relaxation. Quartic identities imply degree-six exclusion over C; no higher-degree or existence conclusion.',
        }
        e1.write_json(diagpath, diag_data)
    d6.verify_diagonal(INSTANCE)

    # 4. Build summary report and cubic Macaulay verification
    diag_data = json.loads(diagpath.read_text(encoding='utf-8'))
    e2_data = json.loads(e2path.read_text(encoding='utf-8'))
    e1_val = json.loads((OUT / 'validation.json').read_text(encoding='utf-8'))[0]
    e2_val = json.loads((OUT / INSTANCE / 'e2-validation.json').read_text(encoding='utf-8'))
    diag_val = json.loads((OUT / INSTANCE / 'diagonal-validation.json').read_text(encoding='utf-8'))

    gauged_pairs = [tuple(p) for p in diag_data['gauged_column_pairs']]
    gauged_eqs = [e1.unpack(eq) for eq in diag_data['gauged_equations']]
    cubic_res = cubic_multipliers(gauged_eqs, gauged_pairs)
    assert cubic_res['row_rank'] == cubic_res['coefficient_columns'] == 35
    assert cubic_res['unresolved_parameters'] == []

    summary = {
        'instance': INSTANCE,
        'degree': 6,
        'degree6_excluded_over_C': True,
        'packets': {
            'degree_6_e1_sha256': e1.sha(e1path),
            'degree_6_e2_sha256': e1.sha(e2path),
            'degree_6_diagonal_sha256': e1.sha(diagpath),
        },
        'stage1_complete_e1': e1_val,
        'stage2_hessian_e2': {
            'validation': e2_val,
            'step_summary': [
                {
                    'step': idx + 1,
                    'allowed_in': len(s['allowed_parameters']),
                    'active_quadratic_columns': len(s['active_columns']),
                    'quotient_rank': s['quotient_rank'],
                    'forced_squares_count': len(s['forced_squares']),
                    'unresolved_out': len(s['unresolved_parameters']),
                }
                for idx, s in enumerate(e2_data['steps'])
            ],
            'step2_kramers_bridge_doublet': [['X1', 'Y0'], ['X1', 'Y1']],
            'pure_hessian_diagonal_equations': [
                'Q_node: (3*a1 - a2 - a3 - a4)^2 + 2*((a2 - a3)^2 + (a3 - a4)^2 + (a4 - a2)^2) = 0',
                'Q_Kramers: (a3 - a4)*(a0 + a1 - a3 - a4) = 0',
                'Q_bridge: (a0 - a3)*(a0 - a1 + a3 - a4) = 0',
                'Q_anchor: a0*a1 - a0*a4 + 10/9*a1*a2 - 5/9*a1*a3 - 14/9*a1*a4 - 25/27*a2^2 + 10/27*a2*a3 + 10/27*a2*a4 + 47/27*a3^2 - 89/27*a3*a4 + 74/27*a4^2 = 0',
            ],
        },
        'stage3_full_diagonal_e2': {
            'validation': diag_val,
            'dimensions': diag_data['dimensions'],
            'gauged_column_pairs': diag_data['gauged_column_pairs'],
            'gauged_equations': diag_data['gauged_equations'],
            'cubic_macaulay': cubic_res,
            'quartic_macaulay': {
                k: v for k, v in diag_data['quartic_search'].items() if k != 'identities'
            },
        },
    }
    summary_path = OUT / 'summary.json'
    e1.write_json(summary_path, summary)
    figure_paths = render_figure(summary, e2_data, diag_data)
    print(json.dumps({
        'status': 'SUCCESS',
        'summary_sha256': e1.sha(summary_path),
        'cubic_macaulay_rank': f"{cubic_res['row_rank']}/{cubic_res['coefficient_columns']}",
        'quartic_macaulay_rank': f"{diag_data['quartic_search']['row_rank']}/{diag_data['quartic_search']['coefficient_columns']}",
        'figures': figure_paths,
    }), flush=True)


def render_figure(summary: dict, e2_data: dict, diag_data: dict) -> dict[str, str]:
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 9.5,
        'axes.edgecolor': INK,
        'axes.linewidth': 0.9,
    })
    fig = plt.figure(figsize=(14.2, 9.2), facecolor=PAPER, dpi=180)
    gs = fig.add_gridspec(
        2, 2,
        left=0.055, right=0.965, top=0.885, bottom=0.075,
        wspace=0.22, hspace=0.31,
    )

    fig.suptitle(
        'one-reflection-skew — Complete Degree-6 E1 + E2 Exclusion (Kramers-Bridge Cascade & Rank-9 Diagonal Quotient)',
        fontsize=13.0, fontweight='bold', color=INK, y=0.955,
    )
    fig.text(
        0.5, 0.922,
        'F = sum Z_i^6 + X0^3 X1 Y0 Y1 + X1^3 X2 Y0 Y1 + (1/7) X0 X1 Y0 Y1 (Y0^2 - Y1^2),   A = X0^3 Y0^3,   q = 1   |   All arithmetic exact over Q',
        ha='center', va='center', fontsize=9.5, color=SLATE,
    )

    # Panel A: Complete E1 kernel dimensions across degrees 0 <= d <= 6
    ax1 = fig.add_subplot(gs[0, 0], facecolor=PANEL)
    degrees = np.arange(0, 7)
    ker_ors = [0, 0, 0, 0, 0, 6, 36]
    j_dim = [0, 0, 0, 0, 0, 6, 36]
    ker_cycfano = [0, 0, 0, 0, 0, 6, 38]

    w = 0.27
    ax1.bar(degrees - w, ker_ors, width=w, color=TEAL, edgecolor=INK, linewidth=0.8,
            label=r'$\dim\ker(E_1)_d$ (one-reflection-skew / cycle-three)')
    ax1.bar(degrees, j_dim, width=w, color=GOLD, edgecolor=INK, linewidth=0.8,
            label=r'$\dim J_d(F)$ (Jacobian subspace)')
    ax1.bar(degrees + w, ker_cycfano, width=w, color=CORAL, edgecolor=INK, linewidth=0.8, alpha=0.85,
            label=r'$\dim\ker(E_1)_d$ (cyclic / fano: $36+2$ at $d=6$)')

    for d_idx, val in enumerate(ker_ors):
        ax1.text(d_idx - w, val + 0.9, str(val), ha='center', va='bottom', fontsize=8, fontweight='bold', color=TEAL)
    ax1.text(6 + w, 38 + 0.9, '38\n(+2 extra)', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=CORAL)

    ax1.set_xticks(degrees)
    ax1.set_xticklabels([f'd={d}' for d in degrees])
    ax1.set_ylim(0, 46)
    ax1.set_ylabel('Subspace dimension over Q', color=INK, fontweight='bold')
    ax1.set_title('A. Complete E1 Kernel Across Degrees 0 <= d <= 6 (ker(E1)_6 = J_6)',
                  loc='left', fontsize=10.5, fontweight='bold', color=INK, pad=8)
    ax1.grid(axis='y', color=GRID, linestyle='--', linewidth=0.6, alpha=0.8)
    ax1.legend(loc='upper left', frameon=True, facecolor=PAPER, edgecolor=GRID, fontsize=8.0)
    ax1.text(
        0.03, 0.56,
        'Degree-6 E1 exact dimensions:\n'
        '• S_12 rows: 6,188   |   S_6 cols: 462\n'
        '• (S_7)^6 cols: 4,752 |   rank(J_12): 4,437\n'
        '• rank([J_12 | A S_6]): 4,863\n'
        '• dim ker(E1)_6 = 462 - 426 = 36 = dim J_6(F)\n'
        '• Extra non-J_6 directions: 0',
        transform=ax1.transAxes, va='top', ha='left', fontsize=8.0, color=INK,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=PAPER, edgecolor=TEAL, linewidth=0.9),
    )

    # Panel B: 6x6 Jacobian Matrix M_ij Elimination Cascade
    ax2 = fig.add_subplot(gs[0, 1], facecolor=PANEL)
    names = ['X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2']
    # Codes: 0 = F-gauge (M55), 1 = Step 1 (28 off-diag), 2 = Step 2 (Kramers bridge X1-Y0, X1-Y1), 3 = Stage 3 (5 diag a0..a4)
    grid_stage = np.ones((6, 6), dtype=int)
    grid_stage[5, 5] = 0
    for i in range(5):
        grid_stage[i, i] = 3
    grid_stage[1, 3] = 2
    grid_stage[1, 4] = 2

    palette_map = {
        0: '#D9D6CA',  # Gauge M55=0
        1: '#E8EEF0',  # Step 1 killed (28 off-diagonals)
        2: GOLD,       # Step 2 killed (Kramers bridge M13, M14)
        3: CORAL,      # Stage 3 killed (5 diagonals a0..a4 via 9 quadrics)
    }
    rgb_grid = np.zeros((6, 6, 3))
    for r in range(6):
        for c in range(6):
            hex_c = palette_map[grid_stage[r, c]].lstrip('#')
            rgb_grid[r, c] = [int(hex_c[k:k+2], 16) / 255.0 for k in (0, 2, 4)]

    ax2.imshow(rgb_grid, aspect='equal')
    for r in range(6):
        for c in range(6):
            code = grid_stage[r, c]
            if code == 0:
                txt = 'M55=0\n(F-gauge)'
                col = INK
                fw = 'bold'
            elif code == 1:
                txt = f'M_{r}{c}=0\n(Step 1)'
                col = SLATE
                fw = 'normal'
            elif code == 2:
                txt = f'M_{r}{c}=0\n(Step 2)'
                col = INK
                fw = 'bold'
            else:
                txt = f'a_{r}=0\n(Stage 3)'
                col = '#FFFFFF'
                fw = 'bold'
            ax2.text(c, r, txt, ha='center', va='center', fontsize=7.5, color=col, fontweight=fw)

    ax2.set_xticks(range(6))
    ax2.set_yticks(range(6))
    ax2.set_xticklabels([names[j] for j in range(6)], fontweight='bold', color=INK, fontsize=9.0)
    ax2.set_yticklabels([f'd/d{names[i]}' for i in range(6)], fontweight='bold', color=INK, fontsize=8.5)
    ax2.set_xticks(np.arange(-0.5, 6, 1), minor=True)
    ax2.set_yticks(np.arange(-0.5, 6, 1), minor=True)
    ax2.grid(which='minor', color=INK, linestyle='-', linewidth=0.8)
    ax2.tick_params(which='minor', bottom=False, left=False)
    ax2.set_title('B. 6x6 Jacobian Matrix M_ij Cascade (Steps 1-2 & Stage 3)',
                  loc='center', fontsize=10.2, fontweight='bold', color=INK, pad=8)

    # Panel C: 9 x 15 Gauged Diagonal Quadratic System Heatmap
    ax3 = fig.add_subplot(gs[1, 0], facecolor=PANEL)
    pairs = diag_data['gauged_column_pairs']
    eqs = diag_data['gauged_equations']
    mat = np.zeros((len(eqs), len(pairs)))
    text_mat = [['' for _ in range(len(pairs))] for _ in range(len(eqs))]
    for r, eq in enumerate(eqs):
        for c, v_str in eq:
            q_val = e1.Q(v_str)
            mat[r, c] = float(q_val)
            text_mat[r][c] = v_str

    im = ax3.imshow(np.sign(mat) * np.log1p(np.abs(mat)), cmap='RdBu_r', vmin=-2.5, vmax=2.5, aspect='auto')
    for r in range(len(eqs)):
        for c in range(len(pairs)):
            if text_mat[r][c]:
                val = abs(mat[r, c])
                t_col = '#FFFFFF' if val > 1.2 else INK
                ax3.text(c, r, text_mat[r][c], ha='center', va='center', fontsize=6.5, fontweight='bold', color=t_col)

    pair_labels = [f'a{i}a{j}' if i != j else f'a{i}^2' for i, j in pairs]
    ax3.set_xticks(range(len(pairs)))
    ax3.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=7.8, fontweight='bold', color=INK)
    ax3.set_yticks(range(len(eqs)))
    ax3.set_yticklabels([f'Q_{r+1}' for r in range(len(eqs))], fontsize=8.0, fontweight='bold', color=INK)
    ax3.set_xticks(np.arange(-0.5, len(pairs), 1), minor=True)
    ax3.set_yticks(np.arange(-0.5, len(eqs), 1), minor=True)
    ax3.grid(which='minor', color=GRID, linestyle='-', linewidth=0.5)
    ax3.tick_params(which='minor', bottom=False, left=False)
    ax3.set_title('C. Exact Rational 9x15 Diagonal E2 Quotient System (RREF over Q, a5=0 Gauge)',
                  loc='left', fontsize=10.5, fontweight='bold', color=INK, pad=8)

    # Panel D: Macaulay Rank Saturation & Factored Casimir/Kramers Modes
    ax4 = fig.add_subplot(gs[1, 1], facecolor=PANEL)
    ax4.axis('off')
    ax4.set_title('D. Factored Hessian Modes & Cubic/Quartic Macaulay Exclusion over C',
                  loc='left', fontsize=10.5, fontweight='bold', color=INK, pad=8)

    card1 = (
        "1. Pure Hessian Quotient Modes in S_12 / J_12 (Rank 4 before Koszul lifts):\n"
        "   • Chain-node positive-definite Casimir (from X1^3 X2 Y0 Y1):\n"
        "     9 Q_node = (3 a1 - a2 - a3 - a4)^2 + 2[(a2-a3)^2 + (a3-a4)^2 + (a4-a2)^2] = 0\n"
        "   • Kramers reflection-splitting mode (Y0 <-> Y1 parity):\n"
        "     Q_Kramers = (a3 - a4)(a0 + a1 - a3 - a4) = 0\n"
        "   • Bridge-node factorization:\n"
        "     Q_bridge = (a0 - a3)(a0 - a1 + a3 - a4) = 0"
    )
    ax4.text(
        0.01, 0.97, card1, transform=ax4.transAxes, va='top', ha='left',
        fontsize=8.1, color=INK, family='monospace',
        bbox=dict(boxstyle='round,pad=0.45', facecolor=PAPER, edgecolor=TEAL, linewidth=1.0),
    )

    card2 = (
        "2. Full Diagonal E2 with All 315 Koszul Syzygies + 462 F-Multiples:\n"
        "   • Correction subspace rank: 1,486 / 2,352 in S_12 (dim = 6,188)\n"
        "   • Necessary diagonal quadratic rank: 9 / 15 (vs 7 / 15 in cycle-three)\n"
        "   • Includes factored Koszul-lift equations:\n"
        "     4 Q_3 = a2 (4 a0 + a1 - 5 a2 + 4 a3 + a4) = 0\n"
        "     4 Q_4 = a3 (4 a0 + a1 + a2 - 2 a3 + a4) = 0"
    )
    ax4.text(
        0.01, 0.58, card2, transform=ax4.transAxes, va='top', ha='left',
        fontsize=8.1, color=INK, family='monospace',
        bbox=dict(boxstyle='round,pad=0.45', facecolor=PAPER, edgecolor=GOLD, linewidth=1.0),
    )

    card3 = (
        "3. Bounded Macaulay Elimination (No Groebner / Numerical Oracle):\n"
        "   • Cubic multipliers (9 x 5 = 45 rows in 35 cubic monomials):\n"
        "     Rank = 35 / 35 (FULL RANK)  =>  a0^3 = a1^3 = a2^3 = a3^3 = a4^3 = 0\n"
        "   • Quartic multipliers (9 x 15 = 135 rows in 70 quartic monomials):\n"
        "     Rank = 70 / 70 (FULL RANK)  =>  a0^4 = a1^4 = a2^4 = a3^4 = a4^4 = 0\n"
        "   => Complete degree-6 exclusion over C: D in C*F (violates coprimality)."
    )
    ax4.text(
        0.01, 0.23, card3, transform=ax4.transAxes, va='top', ha='left',
        fontsize=8.1, color=INK, family='monospace',
        bbox=dict(boxstyle='round,pad=0.45', facecolor='#FDF2F0', edgecolor=CORAL, linewidth=1.1),
    )

    png_path = OUT / 'one-reflection-skew-degree6-exclusion.png'
    svg_path = OUT / 'one-reflection-skew-degree6-exclusion.svg'
    fig.savefig(png_path, dpi=180)
    fig.savefig(svg_path)
    plt.close(fig)
    return {
        'png': str(png_path.relative_to(ROOT)).replace('\\', '/'),
        'svg': str(svg_path.relative_to(ROOT)).replace('\\', '/'),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recompute', action='store_true', help='Recompute packets from scratch')
    args = parser.parse_args()
    run_pipeline(recompute=args.recompute)
