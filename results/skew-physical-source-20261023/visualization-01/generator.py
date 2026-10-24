#!/usr/bin/env python3
"""Render exact physical-source factors and the remaining connection boundary.

Requires a passing source-bound Lean receipt; writes only a new directory.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time

os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='hodge-source-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
MODULE = 'formal/HodgeLab/OneReflectionSkew/PhysicalSourceNormalization.lean'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--output-dir', required=True)
    a = parser.parse_args()
    started = time.monotonic()
    receipt_path = (ROOT/a.receipt).resolve()
    out = (ROOT/a.output_dir).resolve()
    if not out.is_relative_to(ROOT):
        raise ValueError('Output escapes the repository')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if receipt.get('status') != 'PASS':
        raise ValueError('A passing focused receipt is required')
    source = ROOT/MODULE
    hashes = receipt.get('source_sha256', receipt.get('source_lf_sha256', {}))
    if hashes.get(MODULE.removeprefix('formal/')) != sha(source):
        raise ValueError('Receipt does not match the current Lean module')
    required = ['source_form_transport', 'normalized_source_form_transport',
                'fibre_last_orientation', 'jacobian_eq', 'b_column_rational',
                'b_variation', 'twelve_factor', 'source_four_form_reduction',
                'baseWedge_factor', 'sourceScalar_image', 'sourceScalar_trace']
    declared = set(re.findall(r'^(?:noncomputable )?(?:def|theorem|lemma|abbrev|instance) (\w+)',
                              source.read_text(encoding='utf-8'), re.M))
    if not set(required) <= declared:
        raise ValueError('Missing required checked declarations')
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, out/'generator.py')
    navy, teal, gray, amber = '#17334e', '#007f86', '#4e6372', '#9b5c08'
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':13,
                         'svg.hashsalt':'hodge-physical-source-v1'})
    fig = plt.figure(figsize=(17, 14), facecolor='white')
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(.045,.965,'Physical-source normalization: exact factors and scope',
            fontsize=24,fontweight='bold',color=navy)
    ax.text(.045,.935,r'Protected data: $q=1,\ A=X_0^3Y_0^3$; chart '
            r'$Y_0=1,\ (X_0,X_1,X_2,Y_1,Y_2)=(x,rx,wx,t,\nu),\ U=x^2$',
            fontsize=15,color=gray)

    def panel(x,y,w,h,title,face='#eef5f8',edge='#bfd1dc',style='solid'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',
                                   facecolor=face,edgecolor=edge,linewidth=1.3,linestyle=style))
        ax.text(x+.016,y+h-.030,title,fontsize=16,fontweight='bold',color=navy,va='center')

    panel(.045,.745,.382,.145,'Imported normalized pole term')
    ax.text(.236,.818,r'$\frac{5U^2}{72\nu^{11}}\,dU\wedge dr\wedge dw\wedge dt$',
            ha='center',fontsize=21,color=navy)
    ax.text(.236,.773,'Fibre first; proved normalized pole coefficient',
            ha='center',fontsize=12,color=gray)

    panel(.565,.745,.390,.145,'New actual-form identity')
    ax.text(.760,.818,r'$\frac{5}{72}\frac{r^{11}}{f_r}\frac{V^2}{\nu^{11}}'
            r'\,dV\wedge da\wedge dv\wedge dt$',ha='center',fontsize=20,color=navy)
    ax.text(.760,.773,r'$r\ne0,\quad\nu\ne0,\quad f_r\ne0$',ha='center',fontsize=15,color=gray)
    ax.add_patch(FancyArrowPatch((.441,.818),(.551,.818),arrowstyle='-|>',
                                mutation_scale=19,color=teal,linewidth=2))
    ax.text(.496,.853,r'$V=rU$',ha='center',fontsize=16,color=teal)
    ax.text(.496,.784,r'$v=r^{-1}+rw$',ha='center',fontsize=14,color=teal)

    panel(.045,.620,.910,.080,'The Jacobian accounts for every power of r')
    ax.text(.500,.637,r'$\det\frac{\partial(a,v,t)}{\partial(r,w,t)}'
            r'=\frac{f_r}{r^{14}},\qquad'
            r'dV\wedge da\wedge dv\wedge dt'
            r'=\frac{f_r}{r^{13}}\,dU\wedge dr\wedge dw\wedge dt$',
            ha='center',fontsize=19,color=teal)

    panel(.045,.450,.440,.115,'Why the factor is 1/12')
    ax.text(.265,.503,r'$\nu^6+P(V)=0,\qquad P=aV^3+bV^2+cV+d_0$',
            ha='center',fontsize=15,color=navy)
    ax.text(.265,.469,r'$D_b(\nu^{-5})=\frac{5V^2}{6\nu^{11}},\qquad'
            r'\frac{5}{72}=\frac1{12}\frac56$',ha='center',fontsize=19,color=teal)

    panel(.515,.450,.440,.115,'One pinned fibre-reduction column')
    ax.text(.735,.503,r'$\frac56V^2=-P(M_{00}+M_{10}V)-PR^{\prime}'
            r'+\frac56P^{\prime}R$',ha='center',fontsize=16,color=navy)
    ax.text(.735,.477,'Both rows of b-column 0 and the exact correction R',
            ha='center',fontsize=12,color=gray)
    ax.text(.735,.456,r'Literal packet coefficients; $\Delta\ne0$',ha='center',fontsize=12,color=gray)

    panel(.045,.265,.910,.130,'Proved four-form representative and correction',face='#e8f5f0',edge='#a4ccba')
    ax.text(.500,.325,r'$S_4=\frac{\phi}{12}\frac{M_{00}+M_{10}V}{\nu^5}\,dV\wedge B'
            r'+d\!\left(\frac{\phi R}{12\nu^5}\right)\wedge B$',
            ha='center',fontsize=24,color=navy)
    ax.text(.500,.283,r'$\phi=r^{11}/f_r,\quad B=da\wedge dv\wedge dt;\quad'
            r'd(\phi/12)\wedge B=0$ is proved. Curve relation and $\Delta\ne0$ are explicit.',
            ha='center',fontsize=15,color=teal)

    panel(.045,.115,.440,.100,'Orientation is explicit')
    ax.text(.265,.151,r'$dV\wedge da\wedge dv\wedge dt'
            r'=-\,da\wedge dv\wedge dt\wedge dV$',
            ha='center',fontsize=15,color=teal)

    panel(.515,.115,.440,.100,'Still outside the formal result',face='#fff6e9',edge='#d4aa68',style='dashed')
    ax.text(.735,.157,'Physical curve field and compatible Kähler pullback;',
            ha='center',fontsize=12,color=amber)
    ax.text(.735,.133,'cohomology / connection and full source-class identification.',
            ha='center',fontsize=12,color=amber)

    ax.text(.045,.077,'Packet convention: opposite sign to standard projective Ω with normal differential last.',
            fontsize=13,color=gray)
    ax.text(.045,.048,'Cover scalar = slot 11, trace 0; reported compact system: 17 covering slots × 2 rows = rank 34.',
            fontsize=13,color=navy)
    ax.text(.045,.022,'No 1/864 substitution, arbitrary-vector descent, primitive, global clearing, certificate or solve.',
            fontsize=12,color=gray)
    png, svg = out/'physical-source-normalization.png', out/'physical-source-normalization.svg'
    fig.savefig(png,dpi=160,metadata={'Software':'Hodge Lab reproducible Matplotlib figure'})
    fig.savefig(svg,metadata={'Date':None,'Creator':'Hodge Lab reproducible Matplotlib figure'})
    plt.close(fig)
    # SVG path whitespace is semantically immaterial; normalize before recording hashes.
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8')
    manifest = {'executor':'Pro root integration',
                'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'inputs':{MODULE:sha(source),str(receipt_path.relative_to(ROOT)):sha(receipt_path),
                          'scripts/visualize_skew_physical_source.py':sha(Path(__file__))},
                'outputs':{p.name:sha(p) for p in [png,svg,out/'generator.py']},
                'required_declarations':required, 'matplotlib_version':matplotlib.__version__,
                'python_version':sys.version,'elapsed_seconds':time.monotonic()-started,
                'scope':'Actual chart/factor/orientation identities, selected column and four-form correction; quotient scalar trace; boundary shown explicitly',
                'limits':['Visualization is not additional proof evidence',
                          'Packet global orientation convention is sourced; three-swap identity is Lean proved',
                          'No complete relative cohomology, Gauss-Manin realization or full physical-source class identification']}
    (out/'visualization.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','outputs':manifest['outputs'],'elapsed_seconds':manifest['elapsed_seconds']}))


if __name__ == '__main__':
    main()
