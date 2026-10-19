"""Port diagram for the 4-line wiring plan (v4): plan view + unrolled elevation + table.
Reads the route from xl_common.PORTS (GAZEBO_LAYOUT=v4), so the drawing always matches the model's node order.
Run from the repo root:  python scripts/k4_ports_diagram_v4.py  ->  docs/k4_ports_v4_diagram.png"""
import os, sys, io, contextlib, textwrap
os.environ.setdefault('GAZEBO_LAYOUT', 'v4')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, FancyBboxPatch, Circle, RegularPolygon
_cwd = os.getcwd(); _tmp = '/tmp/_k4v4'; os.makedirs(_tmp + '/model', exist_ok=True)
import shutil; shutil.copy('model/gazebo.xmodel', _tmp + '/model/'); os.chdir(_tmp)   # g5 writes renders on import
with contextlib.redirect_stdout(io.StringIO()):
    import xl_common as X
os.chdir(_cwd)
assert X.LAYOUT == 'v4'
C = {'P1': '#1f5fbf', 'P2': '#0f9b8e', 'P3': '#c2185b', 'P4': '#e07b00'}
RANGES = {n: (a, b) for n, a, b in X.PORT_RANGES}
# injection plan (see docs/physical_layout_v4.md)
INJ_MAND = [('P1', 4, 0), ('P2', 8, 0), ('P3', 12, 0), ('P4', 12, 36)]       # (line, post, height)
INJ_OPT = [('P1', 2, 0), ('P2', 6, 0), ('P3', 10, 0)]                      # after 200 px ("optional")
LEADS = {'P1': (1, 0, '5 ft'), 'P2': (5, 0, '25 ft'), 'P3': (9, 0, '20 ft'), 'P4': (1, 36, '5 ft')}  # start post, height, BOM ext.

fig = plt.figure(figsize=(24, 17), dpi=100, facecolor='white')
fig.text(0.5, 0.975, "Wiring plan v4: Kulp K4, 4 lines, 1,525 px (400 / 400 / 400 / 325)", ha='center', fontsize=29, fontweight='bold')
fig.text(0.5, 0.952, 'Controller + one 12 V 360 W supply in a Bud box at the base of post 1.  Route as modelled in docs/physical_layout_v4.md (open items listed there).',
         ha='center', fontsize=15, color='#444')

def arr(ax, a, b, c, lw=4, ms=24, ls='-', z=7, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=ms, color=c, lw=lw, linestyle=ls, zorder=z,
                                 shrinkA=0, shrinkB=0, connectionstyle=f'arc3,rad={rad}'))
def bolt(ax, xy, c='#d00000', s=7.5, z=16, hollow=False):
    x, y = xy
    pts = np.array([[0.1, 1], [-0.45, -0.05], [0.0, -0.05], [-0.15, -1], [0.45, 0.15], [0.0, 0.15]]) * s
    ax.add_patch(Polygon(pts + [x, y], fc='white' if hollow else c, ec=c if hollow else 'k', lw=2 if hollow else 1.2, zorder=z))

# ======================= 1. plan =======================
ax = fig.add_axes([0.01, 0.335, 0.40, 0.585], facecolor='#fcfcfa'); ax.set_aspect('equal')
ax.set_xlim(-165, 165); ax.set_ylim(-195, 150); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color('#bbb')
ax.set_title('1. Plan view (from above), posts 1-12 CCW from the entrance', fontsize=19, fontweight='bold', loc='left', pad=8)
R, rin = 100, 24
ang = np.radians(-75 + 30 * np.arange(12)); P = np.c_[np.cos(ang), np.sin(ang)] * R; U = P / R; RR = U * rin
ax.add_patch(Polygon(P, fill=False, ec='#bbb', lw=2.5, zorder=1))
ax.plot(*np.array([P[11], P[0]]).T, color='red', lw=9, solid_capstyle='butt', zorder=2)
ax.text(-25, -150, 'ENTRANCE (face 12, no 36" rail)', ha='center', fontsize=16, color='red', fontweight='bold')
ax.add_patch(Polygon(RR, fc='white', ec='#8b4513', lw=3, zorder=3))
S72, S36 = 0.90, 0.76
def pp(k): return P[(k - 1) % 12]
def plan_seg(name, s):
    c = C[name]
    if s[0] == 'post':
        k = s[1]; q = pp(k) * 1.0
        ax.add_patch(Circle(q, 6.2, fc=c, ec='k', lw=1.2, zorder=12))
        ax.text(*q, '↑' if s[2] == 'up' else '↓', color='white', fontsize=15, fontweight='bold', ha='center', va='center', zorder=13)
    elif s[0] == 'raft':
        k = s[1]; a, b = pp(k) * 0.97, RR[(k - 1) % 12] * 1.05
        if s[2] == 'dn': a, b = b, a
        arr(ax, a, b, c, 4.5, 24)
    elif s[0] in ('R72', 'R36'):
        f = s[1]; sc = S72 if s[0] == 'R72' else S36; a, b = pp(f) * sc, pp(f + 1) * sc
        if s[2] == 'r': a, b = b, a
        ax.plot(*np.array([a, b]).T, color=c, lw=6, ls='-' if s[0] == 'R72' else (0, (3, 1.5)), zorder=5, solid_capstyle='butt')
        m = (a + b) / 2; d = (b - a) / np.linalg.norm(b - a); arr(ax, m - d * 5, m + d * 5, c, 0.1, 26, z=6)
    elif s[0] == 'ring':
        a0 = ang[s[1]]; t = np.linspace(a0, a0 + 2 * np.pi * 0.97, 200); r = rin + 4
        ax.plot(r * np.cos(t), r * np.sin(t), color=c, lw=5, zorder=4)
        arr(ax, (r * np.cos(t[-3]), r * np.sin(t[-3])), (r * np.cos(t[-1]), r * np.sin(t[-1])), c, 5, 22)
for name, segs in X.PORTS:
    for s in segs: plan_seg(name, s)
    # hops (data + GND [+V]) between non-adjacent segment ends
    for s0, s1 in zip(segs, segs[1:]):
        if s0[0] == 'raft' and s1[0] == 'raft':           # centre hop between neighbouring rafter tops
            arr(ax, RR[(s0[1] - 1) % 12] * 1.55, RR[(s1[1] - 1) % 12] * 1.55, C[name], 3.5, 16, ls=(0, (1.5, 1.2)), z=10, rad=-0.35)
        if s0[0] == 'post' and s1[0] == 'post':           # bottom hop between posts
            arr(ax, pp(s0[1]) * 1.1, pp(s1[1]) * 1.1, C[name], 4, 22, ls=(0, (1.5, 1.2)), z=9, rad=-0.15)
        if s0[0] == 'R36' and s1[0] == 'ring':            # hop up to the ring at post 12 / rafter 12
            arr(ax, pp(s0[1]) * S36, RR[s1[1]] * 1.25, C[name], 3.5, 20, ls=(0, (1.5, 1.2)), z=9, rad=0.2)
for k in range(1, 13):
    ax.text(*(U[k - 1] * R * 1.25), str(k), fontsize=24, fontweight='bold', ha='center', va='center')
# controller box at post 1 (outside), leads and injection
box = np.array([-108.0, -160.0])
ax.add_patch(FancyBboxPatch(box - [24, 10], 48, 20, boxstyle='round,pad=1', fc='#222', ec='k', zorder=14))
ax.text(*box, 'Bud box\nK4 + 12 V PSU', color='white', ha='center', va='center', fontsize=10.5, fontweight='bold', zorder=15)
for name, (k, h, ln) in LEADS.items():
    tgt = pp(k) * (1.0 if h == 0 else S36)
    ax.plot(*np.array([box, tgt]).T, color=C[name], lw=2.2, ls=(0, (4, 2)), zorder=8)
    ax.add_patch(Circle(tgt, 4.2, fc='white', ec=C[name], lw=2.5, zorder=14))
    ax.text(tgt[0], tgt[1], 'S', color=C[name], fontsize=9, fontweight='bold', ha='center', va='center', zorder=15)
for name, k, h in INJ_MAND:
    tgt = pp(k) * (1.06 if h == 0 else S36 * 1.06)
    ax.plot(*np.array([box, tgt]).T, color='#d00000', lw=1.4, ls=(0, (1, 2)), zorder=7)
    bolt(ax, tgt)
for name, k, h in INJ_OPT: bolt(ax, pp(k) * 1.06, c=C[name], hollow=True)
ax.text(-160, 146, 'ring drawn ~1.6x true scale\n↑/↓ = post data direction', fontsize=12.5, color='#555', va='top')

# ======================= 2. elevation =======================
ax = fig.add_axes([0.425, 0.335, 0.565, 0.585], facecolor='#fcfcfa')
ax.set_title('2. Unrolled elevation (inside view): posts 1-12 left to right, post 1 repeated at right', fontsize=19, fontweight='bold', loc='left', pad=8)
ax.set_xlim(-0.9, 13.4); ax.set_ylim(-22, 118); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color('#bbb')
for k in range(13):
    ax.plot([k, k], [0, 71], color='#e0c49e', lw=12, solid_capstyle='butt', zorder=1)
    ax.plot([k + 0.2, k + 0.2], [72.5, 89], color='#cfae86', lw=5, zorder=1)
    ax.text(k, -5, f'post {k + 1 if k < 12 else 1}', ha='center', fontsize=14, fontweight='bold')
for f in range(1, 13):
    ax.plot([f - 1, f], [72, 72], color='#ddd5c8', lw=4, zorder=1)
    if f != 12: ax.plot([f - 1, f], [36, 36], color='#ddd5c8', lw=4, zorder=1)
    ax.text(f - 0.5, -12, f'face {f}' + ('\n(entrance)' if f == 12 else ''), ha='center', va='center', fontsize=12, color='#555')
ax.text(11.5, 30, 'no 36" rail', ha='center', fontsize=12, color='red')
ax.add_patch(Rectangle((-0.15, 89), 12.5, 4, fc='#ecdcc8', ec='#8b4513', lw=2, zorder=1))
ax.text(12.45, 91, 'ring', fontsize=12, color='#8b4513', va='center', fontweight='bold')
for z, l in [(72, '72" (top)'), (36, '36" (mid)')]: ax.text(13.35, z + 1.5, l, ha='right', fontsize=12, color='#555')
def ex(name, k): return 12 if (k % 12 == 1 and name == 'P3') else (k - 1) % 12
def elev_seg(name, s):
    c = C[name]
    if s[0] == 'post':
        x = ex(name, s[1]) + 0.06; a, b = (0.8, 70.5) if s[2] == 'up' else (70.5, 0.8); arr(ax, (x, a), (x, b), c, 5, 26)
    elif s[0] == 'raft':
        x = ex(name, s[1]) + 0.2; a, b = (72.8, 88.6) if s[2] == 'up' else (88.6, 72.8); arr(ax, (x, a), (x, b), c, 5, 22)
    elif s[0] in ('R72', 'R36'):
        z = 72 if s[0] == 'R72' else 36; xa, xb = ex(name, s[1]), ex(name, s[1] + 1)
        if s[1] == 12: xa, xb = 11, 12
        if s[2] == 'r': xa, xb = xb, xa
        ax.plot([xa, xb], [z, z], color=c, lw=7, zorder=5, solid_capstyle='butt')
        m = (xa + xb) / 2; d = 0.12 * np.sign(xb - xa); arr(ax, (m - d, z), (m + d, z), c, 0.1, 28, z=8)
    elif s[0] == 'ring':
        x0 = s[1] + 0.2
        ax.plot([x0, 12.3], [91, 91], color=c, lw=5, zorder=4); ax.plot([-0.1, x0 - 0.05], [91, 91], color=c, lw=5, zorder=4)
        arr(ax, (x0 + 0.6, 91), (x0 + 1.1, 91), c, 5, 22); arr(ax, (11.6, 91), (12.3, 91), c, 5, 22)
        ax.text(6.0, 95, 'ring 50 px, once round CCW (direction to verify)', fontsize=12, color=c, ha='center', fontweight='bold',
                bbox=dict(fc='white', ec='none', alpha=.9, pad=1), zorder=9)
for name, segs in X.PORTS:
    for s in segs: elev_seg(name, s)
    for s0, s1 in zip(segs, segs[1:]):
        if s0[0] == 'raft' and s1[0] == 'raft':
            xa, xb = ex(name, s0[1]) + 0.2, ex(name, s1[1]) + 0.2
            arr(ax, (xa, 89.5), (xb, 89.5), C[name], 3.5, 18, ls=(0, (1.5, 1.2)), z=9, rad=-0.6)
        if s0[0] == 'post' and s1[0] == 'post':
            xa, xb = ex(name, s0[1]) + 0.06, ex(name, s1[1]) + 0.06
            arr(ax, (xa, 3), (xb, 3), C[name], 4, 22, ls=(0, (1.5, 1.2)))
            ax.text((xa + xb) / 2, 7, 'bottom hop\n~50" (5 ft ext.)', ha='center', fontsize=10.5, color=C[name], fontweight='bold',
                    bbox=dict(fc='white', ec='none', alpha=.9, pad=1), zorder=9)
        if s0[0] == 'R36' and s1[0] == 'ring':
            x = 11 + 0.12
            arr(ax, (x, 37), (x, 89), C[name], 3.5, 20, ls=(0, (1.5, 1.2)))
            ax.text(x + 0.08, 56, 'hop to top\n~10 ft ext.', ha='left', fontsize=10.5, color=C[name], fontweight='bold',
                    bbox=dict(fc='white', ec='none', alpha=.9, pad=1), zorder=9)
ax.text(1.7, 104, 'dotted arcs at the top = centre hops between neighbouring rafter ends (~10")', fontsize=12, color='#333')
for name, (k, h, ln) in LEADS.items():
    for x in ([ex(name, k)] if not (name == 'P4') else [0]):
        ax.scatter([x - 0.12], [h + 1.5], s=330, c='white', edgecolors=C[name], linewidths=2.5, zorder=14)
        ax.text(x - 0.12, h + 1.5, 'S', color=C[name], fontsize=10, fontweight='bold', ha='center', va='center', zorder=15)
        ax.text(x - 0.12, h - 3.8 if h else -17.5, f'{name[1:] and "L"+name[1:]} start\n({ln} lead)', fontsize=9.5, ha='center', va='top',
                color=C[name], fontweight='bold', zorder=15)
for name, k, h in INJ_MAND:
    x = ex(name, k) + (0.3 if h == 0 else -0.3)
    ax.scatter([x], [h + 2.5], marker='v', s=300, c='#d00000', edgecolors='k', linewidths=1.2, zorder=16)
    ax.text(x + 0.12, h + 7 if h else 9.5, 'inject', fontsize=10.5, color='#d00000', fontweight='bold', zorder=16)
for name, k, h in INJ_OPT:
    x = ex(name, k) + 0.3
    ax.scatter([x], [2.5], marker='v', s=300, c='white', edgecolors=C[name], linewidths=2.2, zorder=16)
ax.add_patch(FancyBboxPatch((-0.75, 104), 1.45, 11, boxstyle='round,pad=0.02', fc='#222', ec='k', zorder=10))
ax.text(-0.03, 109.5, 'Bud box\nat post 1', color='white', ha='center', va='center', fontsize=11, fontweight='bold', zorder=11)

# ======================= 3. table =======================
ax = fig.add_axes([0.01, 0.015, 0.98, 0.3]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
for x, h in [(1, 'Line'), (7.5, 'Pixels / nodes'), (17, 'Start'), (27, 'Path (data order)'), (80, 'Power injection')]:
    ax.text(x, 95, h, fontsize=16, fontweight='bold', va='center')
ax.plot([0, 100], [90, 90], color='k', lw=2)
start = {'P1': 'post 1 base', 'P2': 'post 5 base', 'P3': 'post 9 base', 'P4': 'post 1, mid-height'}
inj = {'P1': 'post 4 base (mandatory)\npost 2 base after 200 px (optional)', 'P2': 'post 8 base (mandatory)\npost 6 base (optional)',
       'P3': 'post 12 base (mandatory)\npost 10 base (optional)', 'P4': 'post 12 mid-height, before the\nhop to the ring'}
for i, (name, segs) in enumerate(X.PORTS):
    y = 78 - i * 17; a, b = RANGES[name]
    ax.add_patch(Rectangle((0.6, y - 6.5), 5, 13, fc=C[name], ec='none'))
    ax.text(3.1, y, f'L{name[1:]}\n= {name}', color='white', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(7.5, y, f'{b - a + 1}\n({a}-{b})', fontsize=15, va='center')
    ax.text(17, y, start[name], fontsize=14, va='center')
    ax.text(27, y, textwrap.fill(X.PORT_DESC[name].replace('rafter', 'raf.'), 98), fontsize=12.2, va='center', linespacing=1.15)
    ax.text(80, y, inj[name], fontsize=12.5, va='center')
ax.plot([0, 100], [8, 8], color='#aaa', lw=1.2)
ax.text(0.6, 3.5, 'Key: solid arrows = pixel strings (direction of data)   dotted = hops / X-connect extensions (data, GND, V+)   dashed = controller leads from the Bud box   S = line start\n'
        'red bolt / triangle = mandatory power injection   hollow = optional injection (after 200 px)   plan: 72" (top) rail solid, 36" (mid) dashed   "72\\" f2 (3>2)" = face 2 run from post 3 to post 2',
        fontsize=12.5, color='#333', va='center', linespacing=1.5)
out = 'docs/k4_ports_v4_diagram.png'
plt.savefig(out, dpi=100, facecolor='white'); print(out)
