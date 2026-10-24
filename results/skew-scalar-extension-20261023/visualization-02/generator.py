#!/usr/bin/env python3
"""Render the checked scalar-extension diagram into a fresh directory.

This is an equation/dependency visualization, not a numerical root plot.
The input must be a passing focused receipt bound to the current Lean module.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import os
import tempfile
import shutil
import sys
import time

os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='hodge-scalar-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'formal/HodgeLab/OneReflectionSkew/ScalarExtensionTrace.lean'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    started = time.monotonic()
    receipt_path = (ROOT / args.receipt).resolve()
    output = (ROOT / args.output_dir).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError('Output must stay inside the repository')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if receipt.get('status') != 'PASS':
        raise ValueError('A completed passing focused receipt is required')
    source = ROOT / MODULE
    text = source.read_text(encoding='utf-8')
    expected = receipt['source_sha256'][MODULE.removeprefix('formal/')]
    if sha(source) != expected:
        raise ValueError('Receipt is not bound to the current Lean module')
    required = ['beta_tmul', 'beta_theta', 'beta_scalar', 'quotientComparison',
                'trace_baseChange', 'trace_beta', 'trace_quotientComparison',
                'trace_evaluations', 'trace_tmul', 'trace_one', 'trace_two_tmul_one',
                'beta_quotientWeight', 'trace_slot_seventeen', 'trace_slot_eleven']
    declared = set(re.findall(r'^(?:def|abbrev|theorem|lemma|instance) (\w+)', text, re.M))
    if not set(required) <= declared:
        raise ValueError('Required theorem boundary is not present in checked source')
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, output / 'generator.py')

    navy, teal, gray, pale = '#18324b', '#007f86', '#546575', '#edf4f7'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                         'svg.hashsalt': 'hodge-scalar-extension-v1'})
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(.055, .951, 'Scalar extension preserves the algebra trace',
            fontsize=25, fontweight='bold', color=navy)
    ax.text(.055, .909, r'$K=\mathbb{Q}(v)(t)(a),\quad f=X^{18}+X^{12}+(vX-1)^6-aX^{15},'
            r'\quad L=\mathrm{SplittingField}_K(f)$', fontsize=16, color=gray)

    def box(x, y, w, h, title, body, face=pale):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012',
                                   linewidth=1.2, edgecolor='#bbced8', facecolor=face))
        ax.text(x+w/2, y+h-.037, title, ha='center', va='center', fontsize=18,
                fontweight='bold', color=navy)
        ax.text(x+w/2, y+.041, body, ha='center', va='center', fontsize=13, color=gray,
                linespacing=1.5)

    def arrow(a, b, label, pos, rotation=0):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=17,
                                    color=teal, linewidth=1.8, shrinkA=3, shrinkB=3))
        ax.text(*pos, label, ha='center', va='center', fontsize=14, color=teal,
                rotation=rotation, bbox={'facecolor':'white','edgecolor':'none','pad':2})

    box(.055, .655, .23, .158, r'$E=K[X]/(f)$', 'Actual AdjoinRoot quotient\nFree of rank 18 over K')
    box(.386, .655, .23, .158, r'$T=L\otimes_K E$', 'L acts on the left factor\nFree of rank 18 over L')
    box(.717, .655, .23, .158, r'$S=L^{18}$', 'All eighteen components\nCoordinatewise multiplication')
    arrow((.285,.746),(.386,.746),r'$e\mapsto 1\otimes e$',(.3355,.847))
    arrow((.616,.746),(.717,.746),r'$\beta\;\cong$',(.6665,.778))
    ax.text(.6665,.601,r'$\beta(l\otimes e)_j=l\,\sigma_j(e)$',ha='center',fontsize=17,color=navy)
    ax.text(.6665,.568,r'$\beta(1\otimes\theta)=\rho,\quad\beta(l\otimes1)=(l,\ldots,l)$',
            ha='center',fontsize=14,color=gray,bbox={'facecolor':'white','edgecolor':'none','pad':2})

    box(.080,.423,.18,.093,r'$K$', '',face='#f7fafb')
    box(.496,.423,.23,.093,r'$L$', '',face='#f7fafb')
    arrow((.17,.655),(.17,.516),r'$\mathrm{Tr}_{E/K}$',(.105,.586))
    arrow((.501,.655),(.575,.516),r'$\mathrm{Tr}_{T/L}$',(.443,.577))
    arrow((.832,.655),(.690,.516),r'$\sum_j$',(.843,.557))
    arrow((.26,.469),(.496,.469),r'$\kappa:K\hookrightarrow L$',(.377,.502))
    ax.text(.501,.374,r'$\kappa(\mathrm{Tr}_{E/K}(e))=\mathrm{Tr}_{T/L}(1\otimes e)'
            r'=\sum_j\sigma_j(e)\qquad\mathrm{for\ every}\ e\in E$',
            ha='center',fontsize=18,color=navy)
    ax.text(.501,.333,r'$T\;\cong_L\;Q=L[X]/(\kappa(f)),'
            r'\qquad\mathrm{Tr}_{T/L}(z)=\mathrm{Tr}_{Q/L}(\gamma z)'
            r'\quad\mathrm{for\ every}\ z\in T$',ha='center',fontsize=15,color=gray)

    ax.text(.501,.292,r"$w_i=\theta^i\,f'(\theta)^{-1}\in E,\qquad\mathrm{Tr}_{E/K}(w_{17})=1,\quad\mathrm{Tr}_{E/K}(w_{11})=0$",
            ha='center',fontsize=15,color=teal)

    box(.055,.153,.269,.113,r'$\mathrm{Tr}_{E/K}(1)=18$', 'The trace is not normalized')
    box(.366,.153,.269,.113,r'$\mathrm{Tr}_{T/L}(2\otimes1)=36$', 'The tensor scalar is retained')
    box(.677,.153,.270,.113,'Proof mechanism', 'Interpolation + equal dimensions\nMultiplication-map base change')
    ax.text(.055,.095,'Scope: generic field; algebra traces; no irreducibility or field assumption on E.',
            fontsize=13,color=navy)
    ax.text(.055,.060,'Every split vector comes from T; an arbitrary split vector need not come from E.',
            fontsize=13,color=gray)
    ax.text(.055,.026,'No differential-source normalization, primitive, global clearing, certificate or solve is asserted.',
            fontsize=12,color=gray)

    png, svg = output/'scalar-extension-trace.png', output/'scalar-extension-trace.svg'
    fig.savefig(png, dpi=160, metadata={'Software':'Hodge Lab reproducible Matplotlib figure'})
    fig.savefig(svg, metadata={'Date':None,'Creator':'Hodge Lab reproducible Matplotlib figure'})
    plt.close(fig)
    manifest = {
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'executor':'Pro root integration', 'purpose':'Checked algebra map and trace commutative diagram',
        'inputs':{MODULE:sha(source),str(receipt_path.relative_to(ROOT)):sha(receipt_path),
                  'scripts/visualize_skew_scalar_extension.py':sha(Path(__file__))},
        'outputs':{p.name:sha(p) for p in [png,svg,output/'generator.py']},
        'required_declarations':required,
        'matplotlib_version':matplotlib.__version__, 'python_version':sys.version,
        'elapsed_seconds':time.monotonic()-started,
        'limitations':['Equation/dependency rendering, not additional proof or numerical root evidence',
                       'No claim that arbitrary split vectors descend to E',
                       'Does not establish physical differential-source normalization or a primitive'],
    }
    (output/'visualization.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','outputs':manifest['outputs'],'seconds':manifest['elapsed_seconds']}))


if __name__ == '__main__':
    main()
