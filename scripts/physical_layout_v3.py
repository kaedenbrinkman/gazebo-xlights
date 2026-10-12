# Physical layout diagram, Layout F v3 (Kulp K4-PB, 4 ports, rails chained onto the unit ports): AC + 12 V supplies in a ground box at post 1, 12 V trunk up post 1 /
# rafter 1, controller + fused distribution in a sealed box on the center ring, every unit fed at its ring end,
# rails fed by two drop cables (rafters/posts 4 and 10). Writes a 2400x1600 PNG.
# Run from the repo root: python scripts/physical_layout_v3.py docs/physical_layout_v3.png
import numpy as np, matplotlib, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle
out = sys.argv[1] if len(sys.argv) > 1 else 'physical_layout_v3.png'
N=12; R=97.75; ROUT=14.75/np.cos(np.pi/12); RIN=11.25/np.cos(np.pi/12)
ang=np.radians(-105+30*np.arange(N)); P=np.c_[R*np.cos(ang),R*np.sin(ang)]
RC=np.c_[ROUT*np.cos(ang),ROUT*np.sin(ang)]
def u(i): return np.array([np.cos(ang[i]),np.sin(ang[i])])
def nrm(i,s=1): return np.array([-u(i)[1],u(i)[0]])*s
C={'P1':'#1f5fbf','P2':'#0f9b8e','P3':'#c2185b','P4':'#7b3fb3','ac':'#d62728','trunk':'#7a3e00','dc':'#ff8c00','inj':'#ffd000'}
port={10:'P1',11:'P1',0:'P1',1:'P2',2:'P2',3:'P2',4:'P3',5:'P3',6:'P3',7:'P4',8:'P4',9:'P4'}   # index = unit-1
down={10,0,1,3,4,6,7,9}        # data ring -> base: U11,U1,U2,U4,U5,U7,U8,U10
R72={0:('P1',1),1:('P1',1),2:('P1',1),3:('P2',-1),4:('P2',-1),5:('P2',-1),6:('P3',-1),7:('P3',-1),8:('P3',-1),9:('P4',-1),10:('P4',-1),11:('P4',-1)}  # face idx -> port, dir
R36={1:('P1',-1),2:('P1',-1),3:('P2',1),4:('P2',1),5:('P2',1),6:('P3',1),7:('P3',1),8:('P3',1),9:('P4',1),10:('P4',1),11:('P4',1)}
fig=plt.figure(figsize=(24,16),dpi=100)
fig.text(0.5,0.977,'Gazebo pixels - Layout F v3: Kulp K4-PB (4 ports) in the ring box, supplies on the ground at post 1, 12 V trunk up post 1',ha='center',va='center',fontsize=23,weight='bold')
fig.text(0.5,0.951,'1,525 px | 4 ports: 400 / 375 / 375 / 375 px, all data leads ~2 ft | ports carry data + GND only | 4 x LRS-350-12 (12.4 V) on the ground | trunk 4 x 6 AWG pairs | units fed at ring ends | rails: 2 drop cables (posts 4 & 10)',ha='center',fontsize=14.5,color='#333')

# ---------------- PLAN ----------------
ax=fig.add_axes([0.005,0.02,0.50,0.91]); ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-152,152); ax.set_ylim(-192,160)
ax.set_title('1. Plan view (from above)   posts numbered CCW from the entrance; face k = post k to post k+1',fontsize=16,weight='bold',loc='left')
for i in range(N):
    ax.plot(*zip(P[i],P[(i+1)%N]),color='#888',lw=2,zorder=1)
    ax.plot(*zip(P[i],RC[i]),color='#a0522d',lw=3,zorder=1,alpha=.5)
ax.add_patch(Polygon(RC,closed=True,fill=False,ec='#8b4513',lw=3))
ax.add_patch(Polygon(np.c_[RIN*np.cos(ang),RIN*np.sin(ang)],closed=True,fill=False,ec='#8b4513',lw=1.5))
def off(i,j,d):
    a,b=P[i],P[j]; m=(a+b)/2; n=m/np.linalg.norm(m); t=(b-a)/np.linalg.norm(b-a)
    return a+n*d+t*5,b+n*d-t*5
for f in range(N):        # 72" rails (outer line), 36" rails (inner line), coloured by port, arrow = data direction
    pt,dr=R72[f]; a,b=off(f,(f+1)%N,6)
    if dr<0: a,b=b,a
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C[pt],lw=2.2,mutation_scale=14))
    if f!=0:
        pt,dr=R36[f]; a,b=off(f,(f+1)%N,-6)
        if dr<0: a,b=b,a
        ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C[pt],lw=2.2,mutation_scale=14,linestyle=(0,(3,1.5))))
m=(P[0]+P[1])/2; ax.plot(*zip(P[0],P[1]),color='red',lw=6,zorder=2)
ax.text(m[0]+40,m[1]-13,'ENTRANCE (no 36" rail)',color='red',ha='center',fontsize=13,weight='bold')
for i in range(N):
    a=P[i]+(RC[i]-P[i])*0.12; b=P[i]+(RC[i]-P[i])*0.78; n=nrm(i,4.5)
    s,e=(b+n,a+n) if i in down else (a+n,b+n)
    ax.annotate('',xy=e,xytext=s,arrowprops=dict(arrowstyle='-|>',color=C[port[i]],lw=3.2,mutation_scale=20),zorder=4)
    ax.add_patch(Rectangle(P[i]-3.5,7,7,fc='#deb887',ec='k',zorder=5))
    ax.text(*(u(i)*(R+20)),f'{i+1}',fontsize=20,weight='bold',ha='center',va='center',color='#222',zorder=6)
    ax.text(*(u(i)*(R+33)),f"U{i+1} {'down' if i in down else 'up'}\n{port[i]}",fontsize=10.5,ha='center',va='center',color=C[port[i]],weight='bold')
def arc(i,j,col,r,ls='-',n=30,z=3):
    t=np.linspace(ang[i],ang[j],n); ax.plot(r*np.cos(t),r*np.sin(t),color=col,lw=3,ls=ls,zorder=z)
for i,j,p in((10,11,'P1'),(1,2,'P2'),(4,5,'P3'),(7,8,'P4')):   # base hops, floor level
    a1,a2=ang[i],ang[j]
    t=np.linspace(a1,a2,30); ax.plot((R+9)*np.cos(t),(R+9)*np.sin(t),color=C[p],lw=3,ls=(0,(4,2)),zorder=3)
for i,j,p in((11,12,'P1'),(2,3,'P2'),(5,6,'P3'),(8,9,'P4')):        # ring hops
    t=np.linspace(ang[i],ang[i]+np.radians(30),10); ax.plot((ROUT+5)*np.cos(t),(ROUT+5)*np.sin(t),color=C[p],lw=3,zorder=7)
# vertical data jumpers on posts 1, 4, 7, 10 (base->rail and rail->rail)
for i,txt in((0,'J: base>72" (P1)\n36">72" (P4)'),(3,'J: 72">36" (P1)\nbase>36" (P2)'),(6,'J: 36">72" (P2)\nbase>36" (P3)'),(9,'J: 36">72" (P3)\nbase>36" (P4)')):
    ax.plot(*(P[i]+u(i)*8.5),marker='o',ms=12,mfc='white',mec='k',mew=2,zorder=11)
    ax.text(*(P[i]+u(i)*-44+(nrm(i,-12) if i in(3,9) else nrm(i,12))),txt,fontsize=9.5,ha='center',va='center',color='#333',zorder=12,bbox=dict(fc='white',ec='#bbb',alpha=.85,pad=1.5))
ax.add_patch(Circle((0,0),ROUT-1.5,fill=False,ec=C['P1'],lw=3,ls=':',zorder=7))          # ring pixels (P1 first, entered at rafter 11)
# unit feeds: ring box -> ring end of every rafter
for i in range(N):
    ax.plot([0,RC[i][0]],[0,RC[i][1]],color=C['dc'],lw=1.6,zorder=7.5)
    ax.plot(*RC[i],marker='*',ms=15,mfc=C['inj'],mec='k',zorder=10)
# rail drop cables along rafters 4 and 10, feed points at posts 4 and 10
for i in(3,9):
    n=nrm(i,-5); ax.plot([RC[i][0]+n[0],P[i][0]+n[0]],[RC[i][1]+n[1],P[i][1]+n[1]],color=C['dc'],lw=5,zorder=6)
    ax.plot(*(P[i]+u(i)*-9),marker='*',ms=22,mfc=C['inj'],mec='k',zorder=10)
    t=P[i]+u(i)*-22+nrm(i,14)
    ax.text(*t,f'10 AWG drop\nfeeds 72" + 36"\nat post {i+1}',fontsize=10.5,ha='center',va='center',color='#b35900',weight='bold')
for i in(6,0): ax.plot(*P[i],marker='X',ms=15,mfc='white',mec='k',mew=2,zorder=11)        # V+ breaks on rails
# ring box
ax.add_patch(FancyBboxPatch((-10,-7),20,14,boxstyle='round,pad=0.5',fc='#dfe9ff',ec='k',lw=2,zorder=8))
ax.text(0,0,'K4-PB\nBOX',ha='center',va='center',fontsize=10,weight='bold',zorder=9,color='#1f3f8f')
# ground box + outlet near post 1, trunk up post 1 along rafter 1
gb=np.array([-62.,-108.]); ax.add_patch(Rectangle(gb-np.array([11,7]),22,14,fc='#fff4d6',ec='k',lw=2,zorder=8))
ax.text(-104,-122,'GROUND BOX on post 1\n(4 x LRS-350-12,\nAC terminals, 30 A fuses)',fontsize=11.5,ha='center',va='center',weight='bold',color='#7a3e00')
outl=np.array([-62,-150]); ax.add_patch(Rectangle(outl-np.array([5,4]),10,8,fc='#ffd9d9',ec=C['ac'],lw=2,zorder=8))
ax.plot([outl[0],gb[0]],[outl[1]+4,gb[1]-7],color=C['ac'],lw=3,zorder=7)
ax.text(-150,-176,'GFCI outlet - ASSUMED within ~6 ft of post 1.\nAC (red) stays on the ground: 6 ft cord to the\nground box. Nothing at height carries mains.',fontsize=11,color=C['ac'],ha='left',weight='bold')
n=nrm(0,-6); pa=[gb+[11,4],P[0]+n+u(0)*2,RC[0]+n*0.6]
ax.plot([p[0] for p in pa],[p[1] for p in pa],color=C['trunk'],lw=7,zorder=6,solid_capstyle='round')
ax.text(-58,-58,'12 V TRUNK\n4 x 6 AWG pairs\n15 ft: up post 1,\nalong rafter 1',fontsize=11,color=C['trunk'],weight='bold',ha='center',rotation=0,zorder=12,
        bbox=dict(fc='white',ec='none',alpha=.8,pad=1))
# legend
L=[('P1: ring, U11, U12, U1, rails f1-f3 (400 px)',C['P1'],'-'),('P2: U2, U3, U4, rails f4-f6 (375 px)',C['P2'],'-'),
   ('P3: U5, U6, U7, rails f7-f9 (375 px)',C['P3'],'-'),('P4: U8, U9, U10, rails f10-f12 (375 px)',C['P4'],'-'),
   ('rails: outer solid = 72", inner dashed = 36"',"#555",'-'),
   ('dashed arc = base hop (floor); solid arc = ring hop',"#555",'--'),('12 V trunk (ground box > ring box)',C['trunk'],'-'),
   ('12 V feed from ring box (unit lead / rail drop)',C['dc'],'-'),('AC mains (ground level only)',C['ac'],'-')]
lx,ly=55,-128
ax.add_patch(FancyBboxPatch((lx-3,ly-66),100,72,boxstyle='round,pad=1',fc='white',ec='#999',zorder=12))
for k,(t,c,ls) in enumerate(L):
    yy=ly-k*6.4; ax.plot([lx,lx+9],[yy,yy],color=c,lw=3 if c!=C['trunk'] else 6,ls=ls,zorder=13); ax.text(lx+11,yy,t,fontsize=10,va='center',zorder=13)
ax.plot(lx+4.5,ly-9*6.4,marker='*',ms=15,mfc=C['inj'],mec='k',zorder=13); ax.text(lx+11,ly-9*6.4,'feed point (fused)   X = V+ break   O = post jumper',fontsize=10,va='center',zorder=13)
ax.text(-150,158,'Arrow = data direction (unit down = ring to post base). Each port: 3 units\n(down, floor hop, up, ring hop, down), then a post jumper (O) up to the\nrails. Power: every unit fed ONLY at its ring end (star). All hops and\njumpers carry data + GND only (V+ cut).',fontsize=11,va='top',color='#333')

# ---------------- ELEVATION ----------------
ex=fig.add_axes([0.548,0.475,0.447,0.44]); ex.set_xlim(-172,125); ex.set_ylim(-16,124)
ex.set_title('2. Elevation (developed section post 1 - ring - post 10; inches, vertical x1.5)',fontsize=16,weight='bold',loc='left')
ex.set_xticks([]); ex.set_yticks([0,36,72,89]); ex.tick_params(labelsize=12); ex.grid(axis='y',ls=':',alpha=.5)
for s in('top','right','bottom'): ex.spines[s].set_visible(False)
ex.axhline(0,color='#6b4f2a',lw=4)
for xs,col in((-R,C['P1']),(R,C['P4'])):
    ex.add_patch(Rectangle((xs-1.75,0),3.5,71,fc='#deb887',ec='k'))
    sg=np.sign(xs)
    ex.plot([xs,sg*ROUT],[72.5,89],color='#a0522d',lw=7,solid_capstyle='butt')
    for z in(36,72): ex.add_patch(Rectangle((xs-sg*1.75-(14 if sg>0 else 0),z-1.75),14,3.5,fc='#f0d9a8',ec='k',lw=.8))
    zz=np.arange(1,70,2); ex.plot([xs-sg*3]*len(zz),zz,'o',ms=2.6,color=col)
    t=np.linspace(0.03,0.97,40); ex.plot(xs+(sg*ROUT-xs)*t,72.5+(89-72.5)*t-2.5,'o',ms=2.6,color=col)
ex.add_patch(Rectangle((-ROUT,89),2*ROUT,3.5,fc='#8b4513',ec='k'))
ex.add_patch(FancyBboxPatch((-9,93.5),18,8,boxstyle='round,pad=0.4',fc='#dfe9ff',ec='k',lw=2))
ex.text(0,115,'RING BOX (sealed, ~12x10x5", ~7 lb) on top of ring\nK4-PB + PocketBeagle + USB Wi-Fi + 4 fuse blocks',fontsize=11.5,ha='center',va='center',weight='bold',color='#1f3f8f')
ex.plot([0,0],[101.9,108.5],color='k',lw=1)
# ground box + AC
ex.add_patch(Rectangle((-166,10),9,9,fc='#ffd9d9',ec=C['ac'],lw=2)); ex.text(-161.5,21,'GFCI\noutlet\n(assumed)',ha='center',va='bottom',fontsize=10,color=C['ac'],weight='bold')
ex.add_patch(Rectangle((-142,12),30,24,fc='#fff4d6',ec='k',lw=2)); ex.text(-127,24,'GROUND\nBOX\n4 x PSU',ha='center',va='center',fontsize=10,weight='bold',color='#7a3e00')
ex.plot([-157,-142],[14.5,16],color=C['ac'],lw=3)
ex.text(-140,47,'AC stays here\n(6 ft cord)',fontsize=10,color=C['ac'],ha='center',weight='bold')
# trunk
ex.plot([-112,-103.5,-103.5],[30,30,75],color=C['trunk'],lw=6)
ex.plot([-103.5,-ROUT-2,-9],[75,92.5,97],color=C['trunk'],lw=6)
ex.text(-150,72,'12 V trunk:\n4 x 6 AWG pairs\n(~15 ft) up post 1,\nalong rafter 1',color=C['trunk'],fontsize=10.5,weight='bold',ha='center',va='center')
# post jumpers (data + GND only)
ex.plot([-93,-93],[3,71],color=C['P1'],lw=2.4,ls=(0,(3,1.5))); ex.text(-91,60,'P1 jumper\nbase>72"',color=C['P1'],fontsize=10,weight='bold')
ex.plot([-90.5,-90.5],[37,71],color=C['P4'],lw=2.4,ls=(0,(3,1.5))); ex.text(-88,45,'P4 jumper\n36">72"',color=C['P4'],fontsize=10,weight='bold')
ex.plot([R-9,R-9],[3,35],color=C['P4'],lw=2.4,ls=(0,(3,1.5))); ex.text(R-11,12,'P4 jumper base>36"',color=C['P4'],fontsize=10,weight='bold',ha='right')
ex.plot([R-11.5,R-11.5],[37,71],color=C['P3'],lw=2.4,ls=(0,(3,1.5))); ex.text(R-13,40,'P3 jumper 36">72"',color=C['P3'],fontsize=10,weight='bold',ha='right')
# unit feeds at ring ends
for xs in(-ROUT,ROUT):
    ex.plot([np.sign(xs)*9,xs],[95,88],color=C['dc'],lw=2)
    ex.plot(xs,87,marker='*',ms=17,mfc=C['inj'],mec='k',zorder=9)
ex.annotate('every unit fed here only\n(ring end = string start)',xy=(ROUT+1,87),xytext=(38,104),fontsize=10.5,color='#b35900',weight='bold',arrowprops=dict(arrowstyle='->',color='#b35900'))
# rail drop down rafter 10 / post 10
ex.plot([9,ROUT+2,R-4,R-4,R-4],[98,93,76,72,36],color=C['dc'],lw=4.5)
for z in(72,36): ex.plot(R-4,z,marker='*',ms=20,mfc=C['inj'],mec='k',zorder=9)
ex.text(R-18,60,'one 10 AWG drop cable:\nring box > rafter 10 > T at 72"\n> continues down post 10\nto the 36" feed T',fontsize=10.5,color='#b35900',weight='bold',ha='right')
ex.annotate('',xy=(R+9,0),xytext=(R+9,71),arrowprops=dict(arrowstyle='<->',lw=1.2)); ex.text(R+11,35,'post 71"',fontsize=11,rotation=90,va='center')
ex.text(-55,101,'rafter ~84"',fontsize=11,ha='center')
ex.annotate('',xy=(-45,30),xytext=(-45,60),arrowprops=dict(arrowstyle='-|>',color='#b35900',lw=2))
ex.text(-42,20,'power flows\nring > rafter > post',fontsize=10.5,color='#b35900',ha='center',weight='bold')
ex.text(25,25,'U1 (left) on P1, U10 (right) on P4:\nboth run data DOWN; at the base a\npost jumper takes data up to the rails',fontsize=10.5,color='#333',ha='center',weight='bold')
ex.text(-10,-11,'ground / deck',fontsize=10.5,color='#6b4f2a',ha='center')

# ---------------- TABLES ----------------
tx=fig.add_axes([0.52,0.015,0.475,0.44]); tx.axis('off'); tx.set_xlim(0,100); tx.set_ylim(0,100)
tx.text(0,99,'3. Ports, trunk circuits, worst-case drop (0.06 A/px, 18 AWG string, 2" lead)',fontsize=15,weight='bold',va='top')
def table(y,xs,hdr,rows,col0=True,fs=11.5,dy=4.2):
    for x,h in zip(xs,hdr): tx.text(x,y,h,fontsize=fs,weight='bold')
    for r in rows:
        y-=dy
        for k,(x,v) in enumerate(zip(xs,r)): tx.text(x,y,v,fontsize=fs,color=(C.get(r[0],'k') if (k==0 and col0) else 'k'),weight='bold' if k==0 else 'normal')
    return y
y=table(91,[0,6,59,65,77],['Port','Chain (data order; all leads ~2 ft from the K4-PB)','px','nodes','post jumpers'],
  [('P1','ring > U11 dn > U12 up > U1 dn > 72" f1-f3 > 36" f3-f2','400','1-400','post 1 (6 ft), post 4'),
   ('P2','U2 dn > U3 up > U4 dn > 36" f4-f6 > 72" f6-f4','375','401-775','post 4, post 7'),
   ('P3','U5 dn > U6 up > U7 dn > 36" f7-f9 > 72" f9-f7','375','776-1150','post 7, post 10'),
   ('P4','U8 dn > U9 up > U10 dn > 36" f10-f12 > 72" f12-f10','375','1151-1525','post 10, post 1')])
y=table(y-5,[0,7,62,72,84],['PSU','Trunk circuit (6 AWG pair, 30 A fuse at ground)','worst A','load','trunk V'],
  [('G1','U1-U5','22.5','77%','0.34'),('G2','U6-U10','22.5','77%','0.34'),('G3','U11 + post-10 rail drop (18 A)','22.5','77%','0.34'),
   ('G4','U12 + ring + post-4 rail drop (16.5 A)','24.0','82%','0.36')],col0=False)
y=table(y-5,[0,40,58,73,86],['Section (incl. trunk, fuses, connectors)','drop','% of 12','far px @12.0','@12.4 V'],
  [('Unit 75 px, fed at ring end only','0.86 V','7.2%','11.14 ok','11.54 ok'),('Ring 50 px, one feed','0.61 V','5.1%','11.39 ok','11.79 ok'),
   ('72" rail, 75 px/dir from post 4/10 feed','1.18 V','9.8%','10.82 LOW','11.22 ok'),('36" rail, 75 px/dir from post 4/10 feed','1.23 V','10.3%','10.77 LOW','11.17 ok'),
   ('Rail loop with ONE feed (150 px each way)','2.58 V','21%','9.4 FAIL','9.8 FAIL')],col0=False)
tx.add_patch(FancyBboxPatch((0,0.5),99,y-4,boxstyle='round,pad=0.6',fc='#fff7e0',ec='#b35900',lw=2))
tx.text(1.5,y-5.5,'K4-PB ports carry DATA + GND ONLY: port V+ pins unconnected; all pixel power from the fuse blocks.\n'
 'Per-port eFuse current limit: NOT PUBLISHED - unknown; not relied on (no pixel current through the ports).\n'
 'Units + ring: no injection (fed at ring end only, worst 0.86 V). Rails: 2 feeds per loop (posts 4, 10)\n'
 'via one 10 AWG drop per side; supplies at 12.4 V (rails worst 1.23 V). 4 floor hops, none on the entrance.',
 fontsize=11.3,va='top',color='#5a2d00',linespacing=1.25)
fig.savefig(out,dpi=100)
print('wrote',out)
