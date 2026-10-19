"""Power / voltage-drop check for the v4 plan (one 12 V 360 W / 30 A supply, 14 AWG injection leads).
Run: python scripts/power_calc_v4.py   (prints the tables used in docs/physical_layout_v4.md)"""
V = 12.0
R18, R14 = 6.385e-3, 2.525e-3          # ohm per ft per conductor (copper, 20 C): 18 AWG string wire, 14 AWG leads
FT_PER_PX = 0.30                        # Wally's 100 ct ~30 ft (4" shell to shell)
LINES = {'L1': 400, 'L2': 400, 'L3': 400, 'L4': 325}
def report(apx, label):
    tot = sum(LINES.values()) * apx
    print(f'\n== {label}: {apx*1000:.0f} mA/px full white ==')
    print(f'total {tot:.1f} A = {tot*V:.0f} W; 30 A supply = {30/tot*100:.0f}% of full white; at 80% continuous (24 A) = {24/tot*100:.0f}%')
    for n, px in LINES.items(): print(f'  {n}: {px} px = {px*apx:.2f} A full white')
    return tot
def drop_both_ends(px, apx):            # uniform load fed at both ends: worst drop at the middle = I*R/8
    I = px * apx; Rl = 2 * px * FT_PER_PX * R18; return I * Rl / 8
for apx, lab in [(0.022, "Wally's spec (~0.25 W)"), (0.040, 'conservative'), (0.058, 'rule-of-thumb 55-60 mA (5 V-style worst case)')]:
    report(apx, lab)
apx = 0.022
print('\n== string (18 AWG) drop at full white, 22 mA/px ==')
print(f'  L1-L3, 400 px fed at start + end only: {drop_both_ends(400, apx):.2f} V at the middle (post 2/6/10 base)')
print(f'  L1-L3, + optional mid feed at 200 px: {drop_both_ends(200, apx):.2f} V')
print(f'  L4, 275 rail px fed at start (port) + post-12 injection: {drop_both_ends(275, apx):.2f} V')
ring = 50 * apx; print(f'  L4 ring 50 px after a 10 ft hop, fed one end: {ring*(2*10*R18) + ring*(2*15*R18)/2:.2f} V')
print('\n== 14 AWG injection leads (loop = 2 x length), current at full white, 22 mA/px ==')
for name, ft, amps in [('post 4 / post 8 base (end feed, no mid feed)', 25, 4.4), ('post 4 / post 8 base (with mid feed)', 25, 2.2),
                       ('post 12 base (end feed)', 6, 4.4), ('post 12 mid (L4, before ring)', 6, 3.0 + 1.1),
                       ('optional mid feed post 6 (~21 ft path)', 25, 4.4), ('optional mid feed post 10 (~13 ft)', 15, 4.4), ('optional mid feed post 2', 6, 4.4)]:
    d = amps * 2 * ft * R14; pig = amps * 2 * 3 * R18
    print(f'  {name}: {ft} ft, {amps:.1f} A -> {d:.2f} V (+{pig:.2f} V for a 36" 18 AWG pigtail)')
print('\n== K4 port share (port feeds the start of each line) ==')
for n, px in LINES.items():
    I = px * apx; print(f'  {n}: ~{I/2:.1f} A through the port with an end feed, ~{I/4:.1f} A with the mid feed too (full white)')
