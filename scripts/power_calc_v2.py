# Voltage-drop calculator for Layout F (gazebo): AC + 12 V supplies in a ground box at post 1,
# 12 V trunk up post 1 / rafter 1 to a sealed controller+distribution box on the center ring,
# every unit (ring end -> rafter -> post) fed only at its ring end, rails fed by drop cables.
# Run: python scripts/power_calc_v2.py      (all numbers in the v2 doc come from here)
OHM_FT={18:6.385e-3,16:4.016e-3,14:2.525e-3,12:1.588e-3,10:0.999e-3,8:0.6282e-3,6:0.3951e-3,
        4:0.2485e-3,2:0.1563e-3,'1/0':0.0983e-3,'2/0':0.0779e-3}          # copper ohm/ft per conductor, 20 C
I_PX=0.06          # A per pixel, worst case (full white)
RC=0.010           # loop ohms of one mated 3-pin pixel connector (V+ & GND), assumed
FUSE={5:0.016,7.5:0.010,10:0.0075,15:0.0045,20:0.0035,30:0.0023}  # ATO/MAXI cold resistance, ohm (typical, assumed)
LUG=0.0005         # loop ohms for a pair of crimped lugs on a stud (both ends of a trunk add 2 of these), assumed
TRUNK_FT=15.0      # one way: ground box -> up post 1 (71") -> along rafter 1 (84") -> ring box, + slack/drip loops
LIMIT=1.0          # pass: total drop <= 1.0 V (far pixel >= 11.0 V with supplies at 12.0 V)
def ladder(n,pitch_in=2,awg=18,hops=None,i=I_PX):
    r=2*pitch_in/12*OHM_FT[awg]; v=0; hops=hops or {}
    for k in range(1,n+1):
        v+=(n-k+1)*i*((r if k>1 else 0)+hops.get(k,0))
    return v
def lead(ft,awg,amps): return 2*ft*OHM_FT[awg]*amps
hop=RC+2*(6/12)*OHM_FT[18]                      # rail face-to-face joint: connector + ~6" of pigtail
RAIL75={26:hop,51:hop}                          # 3 faces (75 px) from a feed point
def rail(n): return {k:hop for k in range(26,n+1,25)}
P=lambda s:print(s)
P('== 1. Trunk: 15 ft one way, ground box -> ring box ==')
P('%-34s %7s %8s %8s'%('option','A/pair','drop V','% of 12'))
trunk={}
for name,awg,amps,fz in [('1 pair 4 AWG (single PSU bus)',4,91.5,None),('1 pair 2 AWG (single PSU bus)',2,91.5,None),
                       ('1 pair 1/0 AWG (single PSU bus)','1/0',91.5,None),('1 pair 2/0 AWG (single PSU bus)','2/0',91.5,None),
                       ('2 pairs 4 AWG (2 x 46 A circuits)',4,45.75,None),
                       ('4 pairs 8 AWG (1 per PSU, 24 A)',8,24,30),('4 pairs 6 AWG (1 per PSU, 24 A)',6,24,30),
                       ('4 pairs 4 AWG (1 per PSU, 24 A)',4,24,30)]:
    v=lead(TRUNK_FT,awg,amps)+2*LUG*amps+(FUSE[fz]*amps if fz else 0)
    trunk[name]=v; P('%-34s %7.1f %8.3f %7.1f%%'%(name,amps,v,v/12*100))
P('  (4-pair rows include a 30 A fuse at the PSU and lugs at both ends; single-bus rows lugs only, fuse ignored)')
# chosen: 4 pairs 6 AWG; circuit currents
circ={'G1 (U1-U5)':22.5,'G2 (U6-U10)':22.5,'G3 (U11 + post-10 rail drop)':22.5,'G4 (U12 + ring + post-4 rail drop)':24.0}
def tr(I): return lead(TRUNK_FT,6,I)+2*LUG*I+FUSE[30]*I
P('\n== 2. Per trunk circuit (6 AWG pair, 30 A fuse at the ground box) ==')
for k,I in circ.items(): P('%-36s %5.1f A  trunk drop %.3f V'%(k,I,tr(I)))
TR=max(tr(I) for I in circ.values())
P('\n== 3. Sections, worst case 0.06 A/px, 18 AWG string, 2" lead/px ==')
rows=[]
def sec(name,parts,I_tr):
    t=tr(I_tr); tot=t+sum(v for _,v in parts); rows.append((name,t,parts,tot))
    P('%-46s trunk %.2f + %s = %.2f V %s'%(name,t,' + '.join('%s %.2f'%(a,b) for a,b in parts),tot,'PASS' if tot<=LIMIT else 'FAIL'))
    return tot
dist=lambda I,f: ('fuse+block',FUSE[f]*I+RC*I)       # top ATO fuse + feed T / pigtail connector
sec('Unit 75 px, fed at ring end only',[('2 ft 14 AWG',lead(2,14,4.5)),dist(4.5,7.5),('string',ladder(75,hops={26:RC}))],22.5)
sec('Ring 50 px, fed at one point',[('2 ft 14 AWG',lead(2,14,3)),dist(3,5),('string',ladder(50,1.75))],24)
for awg in(12,10,8):
    # one cable per side: ring box -> rafter 10 -> T at 72" (8 ft, 18 A) -> on down the post to 36" (3 ft, 9 A)
    d72=lead(8,awg,18); d36=d72+lead(3,awg,9)
    sec(f'72" rails 75 px/dir, post-10 drop {awg} AWG',[('drop',d72),dist(9,20),('string',ladder(75,hops=RAIL75))],22.5)
    sec(f'36" rails 75 px/dir, post-10 drop {awg} AWG',[('drop',d36),dist(9,20),('string',ladder(75,hops=RAIL75))],22.5)
P('\n== 4. Rail loop with a SINGLE feed point (is "no extra feed" possible?) ==')
one_end=ladder(300,hops=rail(300)); P('300 px loop fed at one end (string only)             %.2f V  -> FAIL by %.1fx'%(one_end,one_end/LIMIT))
one_end275=ladder(275,hops=rail(275)); P('275 px 36" C fed at one end (string only)            %.2f V'%one_end275)
mid=ladder(150,hops=rail(150)); P('150 px each way (one feed at the loop middle), string %.2f V'%mid)
f1=lead(8,10,18)+FUSE[20]*18+RC*9+mid+tr(22.5)
P('  + 10 AWG drop (18 A) + fuse + trunk                  %.2f V  -> FAIL'%f1)
cap=None
for pct in range(100,0,-1):
    s=pct/100
    v=s*(lead(8,10,18)+FUSE[20]*18+RC*9+mid)+tr(22.5*1)    # trunk still loaded by its other unit worst case
    if v<=LIMIT: cap=pct; break
P('  brightness cap that makes 1 feed/loop pass (trunk at full load): %d%%'%cap)
v_typ=(lead(8,10,18)+FUSE[20]*18+RC*9+mid)/3+tr(22.5)/3; P('  at typical (~1/3 of full white) 1 feed/loop:          %.2f V'%v_typ)
P('125 px one direction (36" from post 7 to post 2), string %.2f V'%ladder(125,hops=rail(125)))
P('100 px one direction, string %.2f V ; 90 px %.2f V'%(ladder(100,hops=rail(100)),ladder(90,hops=rail(90))))
P('\n== 5. Sensitivity: 4" lead per pixel (or ~20 AWG wire) ==')
P('Unit: %.2f V   72" rail (10 AWG drop): %.2f V   36" rail: %.2f V'%(
  tr(22.5)+lead(2,14,4.5)+FUSE[7.5]*4.5+RC*4.5+ladder(75,4,hops={26:RC}),
  tr(22.5)+lead(8,10,18)+FUSE[20]*9+RC*9+ladder(75,4,hops=RAIL75),
  tr(22.5)+lead(11,10,18)+FUSE[20]*9+RC*9+ladder(75,4,hops=RAIL75)))
P('\n== 6. 24 V trunk option (step-down at the ring) ==')
W=1525*I_PX*12; eff=0.95; I24=W/eff/24
P('Load %.0f W; at 24 V with %.0f%% DC-DC efficiency: %.1f A total, %.1f A per circuit (4)'%(W,eff*100,I24,I24/4))
for awg in(10,8):P('  4 pairs %d AWG: trunk drop %.2f V of 24 (%.1f%%) - absorbed by the regulators'%(awg,lead(TRUNK_FT,awg,I24/4),lead(TRUNK_FT,awg,I24/4)/24*100))
P('  heat at the ring from converters: %.0f W worst, ~%.0f W typical'%(W/eff-W,(W/eff-W)/3))
P('\n== 7. Totals ==')
tot=1525*I_PX; P('Total %.1f A, %.0f W at 12 V; AC @88%% PSU eff: %.0f W, %.1f A at 120 V; typical ~1/3: %.1f A DC'%(tot,tot*12,tot*12/0.88,tot*12/0.88/120,tot/3))
P('Supply heat in ground box: %.0f W worst, ~%.0f W typical'%(tot*12/0.88-tot*12,(tot*12/0.88-tot*12)/3))
P('Ring box dissipation (fuses, blocks, lugs, controller ~8 W) worst: %.1f W'%(
  12*4.5**2*(FUSE[7.5]+RC)+3**2*(FUSE[5]+RC)+2*18**2*FUSE[20]+sum(I**2*2*LUG for I in circ.values())+8))
P('Number check: 12*75+50+300+275 = %d px; circuits sum %.1f A'%(12*75+50+300+275,sum(circ.values())))
P('\n== 8. Far-pixel voltage, worst case (pass = >= 11.0 V) ==')
for n,t,parts,tot in rows:
    P('%-46s drop %.2f  @12.0 V: %.2f %s  @12.4 V: %.2f %s'%(n,tot,12-tot,'ok' if 12-tot>=11 else 'LOW',12.4-tot,'ok' if 12.4-tot>=11 else 'LOW'))
P('\n== 9. Fallback if strings have 4" leads / thinner wire: 4 rail feed points per loop (posts 1,4,7,10) ==')
v=tr(22.5)+lead(8,10,18)+FUSE[20]*4.5+RC*4.5+ladder(50,4,hops={26:hop})
P('72" rail, max 50 px per direction, 4" lead: %.2f V (far px @12.4 V: %.2f)'%(v,12.4-v))
