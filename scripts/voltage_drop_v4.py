"""Voltage-drop map for the v4 wiring (4-line plan) on an unwrapped 12-side diagram.
Run: python scripts/voltage_drop_v4.py  -> docs/voltage_drop_v4.png
Model: each line is a resistive ladder. Every pixel is a constant-current load (0.022 A x brightness, full white);
the string wire between pixels (4" shell to shell) is a resistor, V+ and GND both counted (x2 round trip).
Feeds are ideal 12.4 V sources behind their lead resistance (14 AWG lead + 36" 18 AWG pigtail). Solved by nodal analysis."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); os.environ.setdefault('GAZEBO_LAYOUT', 'v4')
import xl_common as xc, g5
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
VS, APX = 12.4, 0.022
M = 0.3048
R_STR = 0.0333 * 2          # 20 AWG pixel wire, ohm/m, round trip (assumed; Wally's lists 18 AWG -> results are conservative)
R18, R14 = 0.0210 * 2, 0.0083 * 2
SEG = 4 * 0.0254            # 4" wire between pixels
PIG = 3 * M * R18           # 36" 18 AWG injection pigtail
def lead14(ft): return ft * M * R14 + PIG
# extra wire in the chain (after pixel index k, 0-based within the line): hops
HOPS = {**{k: 1 * M * R18 for k in (99, 299)},            # centre hops ~1 ft jumper
        199: 5 * M * R18}                                  # bottom hop 5 ft X-connect
HOPS_L4 = {274: 10 * M * R18}                              # mid rail -> ring 10 ft X-connect
# feeds: (pixel index in line, lead resistance, label, post for drawing)
START = {'L1': (0, 5 * M * R18, 'port, 5 ft X-connect'), 'L2': (0, lead14(25), '14 AWG 25 ft (data+GND ext.)'),
         'L3': (0, lead14(20), '14 AWG 20 ft (data+GND ext.)'), 'L4': (0, 5 * M * R18, 'port, 5 ft X-connect')}
END = {'L1': (399, lead14(25), 'post 4 base, 25 ft'), 'L2': (399, lead14(25), 'post 8 base, 25 ft'),
       'L3': (399, lead14(6), 'post 12 base, 6 ft'), 'L4': (274, lead14(6), 'post 12 mid, ~6 ft (next to the box)')}
MID = {'L1': (199, lead14(6), 'post 2 base, 6 ft'), 'L2': (199, lead14(25), 'post 6 base, 25 ft'),
       'L3': (199, lead14(15), 'post 10 base, 15 ft')}
SCEN = [('A', 'start only', ['S'], 1.0), ('B', 'start + end', ['S', 'E'], 1.0),
        ('C', 'start + end + mid', ['S', 'E', 'M'], 1.0), ('D', 'C at 70 %', ['S', 'E', 'M'], 0.7)]
LINES = [(n, a - 1, b) for n, a, b in xc.PORT_RANGES]; LN = {'P1': 'L1', 'P2': 'L2', 'P3': 'L3', 'P4': 'L4'}
def solve(name, n, feeds, bright):
    hops = HOPS_L4 if name == 'L4' else HOPS
    G = np.zeros((n, n)); I = -np.full(n, APX * bright)
    for k in range(n - 1):
        g = 1 / (SEG * R_STR + hops.get(k, 0)); G[k, k] += g; G[k + 1, k + 1] += g; G[k, k + 1] -= g; G[k + 1, k] -= g
    for idx, r, _ in feeds: G[idx, idx] += 1 / r; I[idx] += VS / r
    return np.linalg.solve(G, I)
def feeds_for(name, kinds):
    d = {'S': START, 'E': END, 'M': MID}; return [d[k][name] for k in kinds if name in d[k]]
V = {}
for s, _, kinds, br in SCEN:
    v = np.zeros(xc.N)
    for p, a, b in LINES: v[a:b] = solve(LN[p], b - a, feeds_for(LN[p], kinds), br)
    V[s] = v
# unwrapped coordinates (x in face units, post i at x=i-1; y in inches; rafters drawn above posts, ring on top)
mem, mi, u, z = xc.MEMARR, xc.MIDX, xc.U, xc.Z
X = np.where(np.isin(mem, ['rails36', 'rails72']), mi + u, mi.astype(float)); Y = z.copy()
X = np.where(mem == 'ring', u * 12, X)
rf = mem == 'rafters'; Y[rf] = 78 + u[rf] * 80; Y[mem == 'ring'] = 172
Y[mem == 'rails72'] = 72; Y[mem == 'rails36'] = 36
cmap = LinearSegmentedColormap.from_list('v', ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641'])
norm = Normalize(10.5, 12.4)
def node_xy(line, k): a = [a for p, a, b in LINES if LN[p] == line][0]; return X[a + k], Y[a + k]
fig = plt.figure(figsize=(24, 18), facecolor='white')
gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 0.7], hspace=0.38, wspace=0.12)
lc = {'L1': '#1f77b4', 'L2': '#d62728', 'L3': '#2ca02c', 'L4': '#9467bd'}
summary = {}
for i, (s, desc, kinds, br) in enumerate(SCEN):
    ax = fig.add_subplot(gs[i // 2, (i % 2) * 2:(i % 2) * 2 + 2])
    for p in range(12): ax.plot([p, p], [0, 71], color='#ccc', lw=6, zorder=0); ax.plot([p, p], [78, 158], color='#e6d8c0', lw=6, zorder=0)
    ax.plot([0, 12], [72, 72], color='#ccc', lw=4, zorder=0); ax.plot([0, 11], [36, 36], color='#ccc', lw=4, zorder=0)
    ax.plot([0, 12], [172, 172], color='#ccc', lw=4, zorder=0)
    ax.scatter(X, Y, c=V[s], cmap=cmap, norm=norm, s=14, zorder=2, edgecolors='none')
    for p in range(12): ax.text(p, -9, f'post {p+1}', ha='center', fontsize=8)
    ax.text(11.5, -17, 'entrance (f12)', ha='center', fontsize=8, color='gray')
    txt = []
    for p, a, b in LINES:
        ln = LN[p]; vv = V[s][a:b]; k = int(np.argmin(vv)); summary[(s, ln)] = vv.min()
        x0, y0 = node_xy(ln, k); ax.scatter([x0], [y0], s=160, facecolors='none', edgecolors='black', lw=1.5, zorder=4)
        ax.annotate(f'{ln} min {vv.min():.2f} V' if vv.min() > 7 else f'{ln} <7 V: brown-out', (x0, y0), xytext=(6, 8), textcoords='offset points', fontsize=8, weight='bold', zorder=5,
                    bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=lc[ln], alpha=0.85))
        for kind, mk, col in (('S', 's', 'black'), ('E', '^', '#0050ff'), ('M', 'D', '#ff00aa')):
            if kind in kinds:
                for idx, _, _ in feeds_for(ln, [kind]):
                    fx, fy = node_xy(ln, idx); ax.scatter([fx], [fy], marker=mk, s=110, c=col, edgecolors='white', zorder=6)
        txt.append(f'{ln} {vv.min():.2f}' if vv.min() > 7 else f'{ln} <7')
    w = int(np.argmin(V[s])); ax.set_title(f'({s}) {desc}' + (f'  brightness {int(br*100)} %' if br < 1 else '  full white') +
                                            f'\nworst pixel: node {w+1} = ' + (f'{V[s][w]:.2f} V' if V[s][w] > 7 else '<7 V (brown-out)') + '  |  ' + '   '.join(txt), fontsize=11)
    ax.set_xlim(-0.6, 12.4); ax.set_ylim(-22, 185); ax.set_yticks([0, 36, 72, 118, 172]); ax.set_yticklabels(['0"', '36" rail', '72" rail', 'rafters', 'ring'])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xticks([])
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], marker='s', ls='', color='black', ms=10, label='line start (K4 port / 14 AWG feed)'),
                    Line2D([], [], marker='^', ls='', color='#0050ff', ms=10, label='end injection (post 4/8/12 base, post 12 mid)'),
                    Line2D([], [], marker='D', ls='', color='#ff00aa', ms=9, label='mid injection (post 2/6/10 base)'),
                    Line2D([], [], marker='o', ls='', mfc='none', mec='black', ms=12, label='lowest pixel of each line')],
           loc='upper center', ncol=4, fontsize=11, bbox_to_anchor=(0.5, 0.97))
cax = fig.add_axes([0.25, 0.925, 0.5, 0.008]); cb = fig.colorbar(plt.cm.ScalarMappable(norm, cmap), cax=cax, orientation='horizontal')
cb.set_label('voltage at pixel (V)  -  12.4 V supply; ≤10.5 V = red (whites go warm / color shift)')
for j, (p, a, b) in enumerate(LINES):
    ax = fig.add_subplot(gs[2, j]); ln = LN[p]
    for s, desc, _, _ in SCEN: ax.plot(np.arange(1, b - a + 1), V[s][a:b], label=f'{s}: {desc}', lw=1.6)
    ax.axhline(10.5, color='red', ls=':', lw=1); ax.set_ylim(8.0, 12.5); ax.set_title(f'{ln} ({b-a} px): V vs pixel index'); ax.grid(alpha=0.3)
    ax.set_xlabel('pixel # in line (data order)')
    if j == 0: ax.set_ylabel('V'); ax.legend(fontsize=8, loc='lower left')
fig.suptitle('Gazebo v4 voltage drop, unwrapped 12 sides (nodal solve, 0.022 A/px, 20 AWG string wire, 14 AWG injection leads)', fontsize=17, y=1.0)
out = os.path.join(os.path.dirname(__file__), '..', 'docs', 'voltage_drop_v4.png'); fig.savefig(out, dpi=90, bbox_inches='tight')
for s, d, _, _ in SCEN: print(s, d, ' '.join(f'{l}={summary[(s,l)]:.2f}' for l in ('L1', 'L2', 'L3', 'L4')))
