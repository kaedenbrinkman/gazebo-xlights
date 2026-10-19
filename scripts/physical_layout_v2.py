# Physical layout diagram, Layout F: AC + 12 V supplies in a ground box at post 1, 12 V trunk up post 1 /
# rafter 1, controller + fused distribution in a sealed box on the center ring, every unit fed at its ring end,
# rails fed by two drop cables (rafters/posts 4 and 10). Writes a 2400x1600 PNG.
# Run from the repo root: python scripts/physical_layout_v2.py docs/physical_layout_v2.png
import numpy as np, matplotlib, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle
out = sys.argv[1] if len(sys.argv) > 1 else 'physical_layout_v2.png'
N=12; R=97.75; ROUT=14.75/np.cos(np.pi/12); RIN=11.25/np.cos(np.pi/12)
ang=np.radians(-105+30*np.arange(N)); P=np.c_[R*np.cos(ang),R*np.sin(ang)]
RC=np.c_[ROUT*np.cos(ang),ROUT*np.sin(ang)]
def u(i): return np.array([np.cos(ang[i]),np.sin(ang[i])])
def nrm(i,s=1): return np.array([-u(i)[1],u(i)[0]])*s
C={'P1':'#1f5fbf','P2':'#0f9b8e','P3':'#c2185b','P4':'#8e44ad','P5':'#2e8b2e','ac':'#d62728','trunk':'#7a3e00','dc':'#ff8c00','inj':'#ffd000'}
port={1:'P1',2:'P1',3:'P1',4:'P1',5:'P2',6:'P2',7:'P2',8:'P2',0:'P3',11:'P3',10:'P3',9:'P3'}   # index = unit-1
down={1,3,5,7,0,10}            # data ring -> base (U2,U4,U6,U8,U1,U11)
fig=plt.figure(figsize=(24,16),dpi=100)
fig.text(0.5,0.977,'Gazebo pixels - Layout F: supplies on the ground at post 1, 12 V trunk up post 1, K16A-B + fuses in a sealed box on the ring',ha='center',va='center',fontsize=23,weight='bold')
fig.text(0.5,0.951,'1,525 px | 12 V WS2811 | 5 of 16 ports | 4 x LRS-350-12 (set 12.4 V) on the ground | trunk 4 x 6 AWG pairs, 15 ft | every unit fed only at its ring end | rails: 2 drop cables (posts 4 & 10)',ha='center',fontsize=14.5,color='#333')

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
for f in range(N):        # 72" rails (outer, CCW f1..f12), 36" rails (inner, CW f12..f2)
    a,b=off(f,(f+1)%N,6); ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C['P4'],lw=2.2,mutation_scale=14))
    if f!=0:
        a,b=off((f+1)%N,f,-6); ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C['P5'],lw=2.2,mutation_scale=14))
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
for i,j,p in((1,2,'P1'),(3,4,'P1'),(5,6,'P2'),(7,8,'P2'),(0,-1,'P3'),(10,9,'P3')):   # base hops, floor level
    a1,a2=ang[i],ang[j] if j>=0 else ang[11]-2*np.pi
    t=np.linspace(a1,a2,30); ax.plot((R+9)*np.cos(t),(R+9)*np.sin(t),color=C[p],lw=3,ls=(0,(4,2)),zorder=3)
for i,j,p in((2,3,'P1'),(6,7,'P2'),(11,10,'P3')): arc(i,j,C[p],ROUT+5,n=10,z=7)       # ring hops
ax.add_patch(Circle((0,0),ROUT-1.5,fill=False,ec=C['P1'],lw=3,ls=':',zorder=7))          # ring pixels (P1 first)
# unit feeds: ring box -> ring end of every rafter
for i in range(N):
    ax.plot([0,RC[i][0]],[0,RC[i][1]],color=C['dc'],lw=1.6,zorder=7.5)
    ax.plot(*RC[i],marker='*',ms=15,mfc=C['inj'],mec='k',zorder=10)
# rail drop cables along rafters 4 and 10, feed points at posts 4 and 10
for i in(3,9):
    n=nrm(i,-5); ax.plot([RC[i][0]+n[0],P[i][0]+n[0]],[RC[i][1]+n[1],P[i][1]+n[1]],color=C['dc'],lw=5,zorder=6)
    ax.plot(*(P[i]+u(i)*-9),marker='*',ms=22,mfc=C['inj'],mec='k',zorder=10)
    t=P[i]+u(i)*-26+nrm(i,-14)
    ax.text(*t,f'10 AWG drop\nfeeds 72" + 36"\nat post {i+1}',fontsize=10.5,ha='center',va='center',color='#b35900',weight='bold')
for i in(6,0): ax.plot(*P[i],marker='X',ms=15,mfc='white',mec='k',mew=2,zorder=11)        # V+ breaks on rails
# ring box
ax.add_patch(FancyBboxPatch((-10,-7),20,14,boxstyle='round,pad=0.5',fc='#dfe9ff',ec='k',lw=2,zorder=8))
ax.text(0,0,'RING\nBOX',ha='center',va='center',fontsize=10,weight='bold',zorder=9,color='#1f3f8f')
# ground box + outlet near post 1, trunk up post 1 along rafter 1
gb=np.array([-62.,-108.]); ax.add_patch(Rectangle(gb-np.array([11,7]),22,14,fc='#fff4d6',ec='k',lw=2,zorder=8))
ax.text(-104,-122,'GROUND BOX on post 1\n(4 x LRS-350-12,\nAC terminals, 30 A fuses)',fontsize=11.5,ha='center',va='center',weight='bold',color='#7a3e00')
outl=np.array([-62,-150]); ax.add_patch(Rectangle(outl-np.array([5,4]),10,8,fc='#ffd9d9',ec=C['ac'],lw=2,zorder=8))
ax.plot([outl[0],gb[0]],[outl[1]+4,gb[1]-7],color=C['ac'],lw=3,zorder=7)
ax.text(-44,-172,'GFCI outlet - ASSUMED within ~6 ft of post 1. AC (red) stays on the ground:\nonly a 6 ft cord from outlet to ground box. Nothing at height carries mains.',fontsize=11,color=C['ac'],ha='center',weight='bold')
n=nrm(0,-6); pa=[gb+[11,4],P[0]+n+u(0)*2,RC[0]+n*0.6]
ax.plot([p[0] for p in pa],[p[1] for p in pa],color=C['trunk'],lw=7,zorder=6,solid_capstyle='round')
ax.text(-58,-58,'12 V TRUNK\n4 x 6 AWG pairs\n15 ft: up post 1,\nalong rafter 1',fontsize=11,color=C['trunk'],weight='bold',ha='center',rotation=0,zorder=12,
        bbox=dict(fc='white',ec='none',alpha=.8,pad=1))
# rail data leads down rafter 1 (other side of the rafter)
n2=nrm(0,8); ax.plot([RC[0][0]+n2[0],P[0][0]+n2[0]],[RC[0][1]+n2[1],P[0][1]+n2[1]],color=C['P4'],lw=2.2,ls=(0,(2,1.5)),zorder=6)
ax.text(P[0][0]+30,P[0][1]+22,'P4/P5\ndata leads\n(rafter 1)',fontsize=10,color=C['P4'],weight='bold',ha='center')
# legend
L=[('P1: ring > U2 > U3 > U4 > U5 (350 px)',C['P1'],'-'),('P2: U6 > U7 > U8 > U9 (300 px)',C['P2'],'-'),('P3: U1 > U12 > U11 > U10 (300 px)',C['P3'],'-'),
   ('P4: 72" rails f1 > f12 (300 px, outer)',C['P4'],'-'),('P5: 36" rails f12 > f2 (275 px, inner)',C['P5'],'-'),
   ('dashed arc = base hop (floor); solid arc = ring hop',"#555",'--'),('12 V trunk (ground box > ring box)',C['trunk'],'-'),
   ('12 V feed from ring box (unit lead / rail drop)',C['dc'],'-'),('AC mains (ground level only)',C['ac'],'-')]
lx,ly=52,-128
ax.add_patch(FancyBboxPatch((lx-3,ly-66),103,72,boxstyle='round,pad=1',fc='white',ec='#999',zorder=12))
for k,(t,c,ls) in enumerate(L):
    yy=ly-k*6.4; ax.plot([lx,lx+9],[yy,yy],color=c,lw=3 if c!=C['trunk'] else 6,ls=ls,zorder=13); ax.text(lx+11,yy,t,fontsize=10,va='center',zorder=13)
ax.plot(lx+4.5,ly-9*6.4,marker='*',ms=15,mfc=C['inj'],mec='k',zorder=13); ax.text(lx+11,ly-9*6.4,'feed point (fused, at a string start)   X = V+ break',fontsize=10,va='center',zorder=13)
ax.text(-150,158,'Arrow on each rafter = data direction (down = ring to post base).\nPower: every unit is fed ONLY at its ring end (star),\nno feed anywhere along a unit. Base and ring hops carry\ndata + GND only (V+ cut).',fontsize=11,va='top',color='#333')

# ---------------- ELEVATION ----------------
ex=fig.add_axes([0.548,0.475,0.447,0.44]); ex.set_xlim(-172,125); ex.set_ylim(-16,124)
ex.set_title('2. Elevation (developed section post 1 - ring - post 10; inches, vertical x1.5)',fontsize=16,weight='bold',loc='left')
ex.set_xticks([]); ex.set_yticks([0,36,72,89]); ex.tick_params(labelsize=12); ex.grid(axis='y',ls=':',alpha=.5)
for s in('top','right','bottom'): ex.spines[s].set_visible(False)
ex.axhline(0,color='#6b4f2a',lw=4)
for xs,col in((-R,C['P3']),(R,C['P3'])):
    ex.add_patch(Rectangle((xs-1.75,0),3.5,71,fc='#deb887',ec='k'))
    sg=np.sign(xs)
    ex.plot([xs,sg*ROUT],[72.5,89],color='#a0522d',lw=7,solid_capstyle='butt')
    for z in(36,72): ex.add_patch(Rectangle((xs-sg*1.75-(14 if sg>0 else 0),z-1.75),14,3.5,fc='#f0d9a8',ec='k',lw=.8))
    zz=np.arange(1,70,2); ex.plot([xs-sg*3]*len(zz),zz,'o',ms=2.6,color=col)
    t=np.linspace(0.03,0.97,40); ex.plot(xs+(sg*ROUT-xs)*t,72.5+(89-72.5)*t-2.5,'o',ms=2.6,color=col)
ex.add_patch(Rectangle((-ROUT,89),2*ROUT,3.5,fc='#8b4513',ec='k'))
ex.add_patch(FancyBboxPatch((-9,93.5),18,8,boxstyle='round,pad=0.4',fc='#dfe9ff',ec='k',lw=2))
ex.text(0,115,'RING BOX (sealed, ~14x12x6") on top of ring\nK16A-B + 4 fuse blocks (one per trunk circuit)',fontsize=11.5,ha='center',va='center',weight='bold',color='#1f3f8f')
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
# rail data leads down rafter 1 / post 1
ex.plot([-9,-ROUT-2,-93,-93],[99,96.5,74,72],color=C['P4'],lw=2.2,ls=(0,(3,1.5)))
ex.plot([-93,-92,-92],[74,74,36],color=C['P5'],lw=2.2,ls=(0,(3,1.5)))
ex.text(-89,63,'P4',color=C['P4'],fontsize=11,weight='bold'); ex.text(-89,41,'P5',color=C['P5'],fontsize=11,weight='bold')
# unit feeds at ring ends
for xs in(-ROUT,ROUT):
    ex.plot([np.sign(xs)*9,xs],[95,88],color=C['dc'],lw=2)
    ex.plot(xs,87,marker='*',ms=17,mfc=C['inj'],mec='k',zorder=9)
ex.annotate('every unit fed here only\n(ring end = string start)',xy=(ROUT+1,87),xytext=(38,104),fontsize=10.5,color='#b35900',weight='bold',arrowprops=dict(arrowstyle='->',color='#b35900'))
# rail drop down rafter 10 / post 10
ex.plot([9,ROUT+2,R-4,R-4,R-4],[98,93,76,72,36],color=C['dc'],lw=4.5)
for z in(72,36): ex.plot(R-4,z,marker='*',ms=20,mfc=C['inj'],mec='k',zorder=9)
ex.text(R-8,52,'one 10 AWG drop cable:\nring box > rafter 10 > T at 72"\n> continues down post 10\nto the 36" feed T',fontsize=10.5,color='#b35900',weight='bold',ha='right')
ex.annotate('',xy=(R+9,0),xytext=(R+9,71),arrowprops=dict(arrowstyle='<->',lw=1.2)); ex.text(R+11,35,'post 71"',fontsize=11,rotation=90,va='center')
ex.text(-55,101,'rafter ~84"',fontsize=11,ha='center')
ex.annotate('',xy=(-60,30),xytext=(-60,60),arrowprops=dict(arrowstyle='-|>',color='#b35900',lw=2))
ex.text(-60,20,'power flows\nring > rafter > post',fontsize=10.5,color='#b35900',ha='center',weight='bold')
ex.text(30,30,'U1 (left), U10 (right)\nboth on P3',fontsize=10.5,color=C['P3'],ha='center',weight='bold')
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
y=table(91,[0,7,57,64],['Port','Chain (data order)','px','Data lead from ring box'],
  [('P1','ring > U2 dn > U3 up > U4 dn > U5 up','350','~2 ft'),('P2','U6 dn > U7 up > U8 dn > U9 up','300','~2 ft'),
   ('P3','U1 dn > U12 up > U11 dn > U10 up','300','~2 ft'),('P4','72" rails f1 > f12 (from post 1)','300','~9 ft down rafter 1'),
   ('P5','36" rails f12 > f2 (from post 1)','275','~12 ft down rafter 1 + post 1')])
y=table(y-5,[0,7,62,72,84],['PSU','Trunk circuit (6 AWG pair, 30 A fuse at ground)','worst A','load','trunk V'],
  [('G1','U1-U5','22.5','77%','0.34'),('G2','U6-U10','22.5','77%','0.34'),('G3','U11 + post-10 rail drop (18 A)','22.5','77%','0.34'),
   ('G4','U12 + ring + post-4 rail drop (16.5 A)','24.0','82%','0.36')],col0=False)
y=table(y-5,[0,40,58,73,86],['Section (incl. trunk, fuses, connectors)','drop','% of 12','far px @12.0','@12.4 V'],
  [('Unit 75 px, fed at ring end only','0.86 V','7.2%','11.14 ok','11.54 ok'),('Ring 50 px, one feed','0.61 V','5.1%','11.39 ok','11.79 ok'),
   ('72" rail, 75 px/dir from post 4/10 feed','1.18 V','9.8%','10.82 LOW','11.22 ok'),('36" rail, 75 px/dir from post 4/10 feed','1.23 V','10.3%','10.77 LOW','11.17 ok'),
   ('Rail loop with ONE feed (150 px each way)','2.58 V','21%','9.4 FAIL','9.8 FAIL')],col0=False)
tx.add_patch(FancyBboxPatch((0,0.5),99,y-4,boxstyle='round,pad=0.6',fc='#fff7e0',ec='#b35900',lw=2))
tx.text(1.5,y-5.5,'"No injection" verdict (worst case):\n'
 '- Units and center ring: YES. Each is fed only at its ring end; worst 0.86 V even with supplies at 12.0 V.\n'
 '- Rail loops: NOT from a single feed. 300 px from one end = 7.4 V; one feed mid-loop = 2.6 V.\n'
 '  Minimum = 2 feed points per loop at face joints (posts 4 and 10), via ONE 10 AWG drop cable per side.\n'
 '  Even then, set the 4 supplies to 12.4 V (or use 8 AWG drops + 12.4 V for more margin).',
 fontsize=11.3,va='top',color='#5a2d00',linespacing=1.25)
fig.savefig(out,dpi=100)
print('wrote',out)
