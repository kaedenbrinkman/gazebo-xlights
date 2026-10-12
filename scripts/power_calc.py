# Voltage-drop calculator for the gazebo physical layout (12 V WS2811).
OHM_FT={18:6.385e-3,16:4.016e-3,14:2.525e-3,12:1.588e-3,10:0.999e-3}   # copper, ohm per ft, 20 C
I_PX=0.06; RC=0.010   # A/pixel worst case; loop resistance of one mated 3-pin connector (V+ & GND), assumed
def ladder(n,pitch_in,awg=18,hops=None,i=I_PX):
    """Drop at the far pixel of n pixels fed at pixel 1. hops={k:extra_loop_ohm} = connector/jumper before pixel k."""
    r=2*pitch_in/12*OHM_FT[awg]; v=0; hops=hops or {}
    for k in range(1,n+1):
        seg = r if k>1 else 0
        seg += hops.get(k,0)
        v += (n-k+1)*i*seg
    return v
def lead(ft,awg,amps): return 2*ft*OHM_FT[awg]*amps
hop=RC+2*(6/12)*OHM_FT[18]        # face-to-face jumper ~6" + one connector
rows=[]
def row(name,parts):
    tot=sum(v for _,v in parts); rows.append((name,parts,tot)); return tot
for pitch,tag in((2,'2" lead'),(4,'4" lead')):
    print(f'--- string lead per pixel {tag} ---')
    u=row(f'Unit 75 px fed at ring end ({tag})',[('2 ft 14 AWG hub lead',lead(2,14,4.5)),('injection T',RC*4.5),('string',ladder(75,pitch,hops={26:RC}))])
    rg=row(f'Ring 50 px fed at one point ({tag})',[('2 ft 14 AWG lead',lead(2,14,3)),('T',RC*3),('string',ladder(50,pitch*0.875))])
    r72=row(f'72" rail tap post 4/10, 75 px each way ({tag})',[('8 ft 12 AWG feeder 9 A',lead(8,12,9)),('T',RC*9),('string+2 hops',ladder(75,pitch,hops={26:hop,51:hop}))])
    r36=row(f'36" rail tap post 10, 75 px each way ({tag})',[('11 ft 12 AWG feeder 9 A',lead(11,12,9)),('T',RC*9),('string+2 hops',ladder(75,pitch,hops={26:hop,51:hop}))])
    for n,p,t in rows[-4:]: print(f'{n:52s} {t:5.2f} V  ({t/12*100:4.1f}%)  '+', '.join(f'{a} {b:.3f}' for a,b in p))
print('--- other cases (2" lead) ---')
s=ladder(75,2,hops={26:RC})
print('75 px from one end, bare string        %.3f'%ladder(75,2))
print('150 px paired run fed one end          %.3f'%ladder(150,2,hops={26:RC,76:RC,126:RC}))
print('150 px fed at both ends / middle       %.3f'%s)
print('300 px chain fed at start only         %.3f'%ladder(300,2))
print('unit fed mid (post top) worst half 40  %.3f'%ladder(40,2))
# Option A: everything at post-1 base, 10 AWG DC trunk (3 circuits <=21 A) 14.6 ft to passive ring hub
print('OptA unit via trunk  %.2f'%(lead(14.6,10,21)+lead(2,14,4.5)+RC*4.5*2+s))
print('OptA 36in rail via 19.7ft 10AWG feeder 16.5A + 3ft 14AWG 9A %.2f'%(lead(19.7,10,16.5)+lead(3,14,9)+RC*9+ladder(75,2,hops={26:hop,51:hop})))
print('OptA 72in rail      %.2f'%(lead(19.7,10,16.5)+RC*9+ladder(75,2,hops={26:hop,51:hop})))
# Option E: 12 home runs, 14 AWG, unit fed at base from port, worst post 7 = 6 faces + slack ~27 ft
print('OptE post7 unit 27ft 14AWG %.2f'%(lead(27,14,4.5)+RC*4.5+s))
# Option D (repo plan): 150 px fed at one point one direction
print('OptD 150 px one direction %.2f'%ladder(150,2,hops={26:RC,51:RC,76:RC+2*17*OHM_FT[18],126:RC}))
tot=1525*I_PX; print('Total A %.1f  W %.0f  AC W @88%% %.0f  A@120 %.1f ; typical 1/3: %.1f A'%(tot,tot*12,tot*12/0.88,tot*12/0.88/120,tot/3))
