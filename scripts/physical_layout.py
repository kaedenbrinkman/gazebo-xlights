# Physical layout diagram for the gazebo pixel installation (recommended layout B).
# Writes physical_layout.png (2400x1600). Run with any python that has numpy+matplotlib.
import numpy as np, matplotlib, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, FancyArrowPatch, Circle
out = sys.argv[1] if len(sys.argv) > 1 else 'physical_layout.png'
N=12; R=97.75; ROUT=14.75/np.cos(np.pi/12); RIN=11.25/np.cos(np.pi/12)
ang=np.radians(-105+30*np.arange(N)); P=np.c_[R*np.cos(ang),R*np.sin(ang)]
RC=np.c_[ROUT*np.cos(ang),ROUT*np.sin(ang)]
def u(i): return np.array([np.cos(ang[i]),np.sin(ang[i])])
C={'P1':'#1f5fbf','P2':'#0f9b8e','P3':'#8e44ad','P4':'#2e8b2e','ac':'#d62728','dc':'#ff8c00','inj':'#ffd000',
   'G1':'#e6194b','G2':'#3cb44b','G3':'#4363d8','G4':'#f58231'}
fig=plt.figure(figsize=(24,16),dpi=100)
fig.text(0.5,0.975,'Gazebo pixel installation - physical layout (recommended Layout B: PSU hub on the ring, controller at post 1)',ha='center',va='center',fontsize=24,weight='bold')
fig.text(0.5,0.948,'1,525 px  |  12 V WS2811  |  Kulp K16A-B  |  4 ports used  |  4 x 12 V 29 A supplies at the ring  |  3 injection locations (17 fused taps)  |  worst-case drop 0.83 V @ 0.06 A/px',ha='center',fontsize=15,color='#333')

# ---------------- PLAN ----------------
ax=fig.add_axes([0.005,0.02,0.50,0.91]); ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-152,152); ax.set_ylim(-190,140)
ax.set_title('1. Plan view (from above)   posts numbered CCW from the entrance',fontsize=17,weight='bold',loc='left')
for i in range(N):
    j=(i+1)%N
    ax.plot(*zip(P[i],P[j]),color='#888',lw=2,zorder=1)
    ax.plot(*zip(P[i],RC[i]),color='#a0522d',lw=3,zorder=1,alpha=.55)          # rafter
ax.add_patch(Polygon(RC,closed=True,fill=False,ec='#8b4513',lw=3))
ax.add_patch(Polygon(np.c_[RIN*np.cos(ang),RIN*np.sin(ang)],closed=True,fill=False,ec='#8b4513',lw=1.5))
# rails: 72" outer offset, 36" inner offset
def off(i,j,d):
    a,b=P[i],P[j]; m=(a+b)/2; n=m/np.linalg.norm(m); t=(b-a)/np.linalg.norm(b-a)
    return a+n*d+t*5,b+n*d-t*5
for f in range(N):
    a,b=off(f,(f+1)%N,6); ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C['P3'],lw=2.2,mutation_scale=14))
    if f!=0:
        a,b=off((f+1)%N,f,-6); ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color=C['P4'],lw=2.2,mutation_scale=14))
# entrance
m=(P[0]+P[1])/2; ax.plot(*zip(P[0],P[1]),color='red',lw=6,zorder=2)
ax.text(m[0]+38,m[1]-13,'ENTRANCE (no 36" rail)',color='red',ha='center',fontsize=13,weight='bold')
# units: arrows along rafters (direction of data)
up={0:'P1',2:'P1',4:'P1',11:'P2',9:'P2',7:'P2'}; down={1:'P1',3:'P1',5:'P1',10:'P2',8:'P2',6:'P2'}
grp={0:'G1',1:'G1',2:'G1',3:'G1',4:'G1',5:'G2',6:'G2',7:'G2',8:'G2',9:'G3',10:'G4',11:'G4'}
for i in range(N):
    a=P[i]+(RC[i]-P[i])*0.12; b=P[i]+(RC[i]-P[i])*0.80
    nrm=np.array([-u(i)[1],u(i)[0]])*4.5
    if i in up: s,e,port=a+nrm,b+nrm,up[i]
    else: s,e,port=b+nrm,a+nrm,down[i]
    ax.annotate('',xy=e,xytext=s,arrowprops=dict(arrowstyle='-|>',color=C[port],lw=3.2,mutation_scale=20),zorder=4)
    # post marker + label
    ax.add_patch(Rectangle(P[i]-3.5,7,7,fc='#deb887',ec='k',zorder=5))
    lp=u(i)*(R+21)
    ax.text(*lp,f'{i+1}',fontsize=20,weight='bold',ha='center',va='center',color='#222',zorder=6)
    lp2=u(i)*(R+34)
    ax.text(*lp2,f"U{i+1} {'up' if i in up else 'down'}\n{grp[i]}",fontsize=10.5,ha='center',va='center',color=C[up.get(i,down.get(i))],weight='bold')
# base hops (outside perimeter, at floor)
def arc_out(i,j,col,r=R+9):
    t=np.linspace(ang[i],ang[j],30)
    ax.plot(r*np.cos(t),r*np.sin(t),color=col,lw=3,ls=(0,(4,2)),zorder=3)
for i,j,p in((1,2,'P1'),(3,4,'P1'),(10,9,'P2'),(8,7,'P2')): arc_out(i,j,C[p])
# ring hops
def arc_in(i,j,col,r=ROUT+5):
    t=np.linspace(ang[i],ang[j],10); ax.plot(r*np.cos(t),r*np.sin(t),color=col,lw=3,zorder=7)
for i,j,p in((2,3,'P1'),(4,5,'P1'),(11,10,'P2'),(9,8,'P2'),(7,6,'P2')): arc_in(i,j,C[p])
# ring itself on P1 between U1 and U2
ax.add_patch(Circle((0,0),ROUT-1.5,fill=False,ec=C['P1'],lw=3,ls=':',zorder=7))
# hub box
ax.add_patch(FancyBboxPatch((-9,-7),18,14,boxstyle='round,pad=0.5',fc='#fff4d6',ec='k',lw=2,zorder=8))
ax.text(0,0,'PSU\nHUB',ha='center',va='center',fontsize=10,weight='bold',zorder=9)
# unit taps (hub -> ring end of every rafter)
for i in range(N):
    ax.plot([0,RC[i][0]],[0,RC[i][1]],color=C['dc'],lw=1.6,zorder=7.5)
    ax.plot(*RC[i],marker='*',ms=16,mfc=C['inj'],mec='k',zorder=10)
# rail feeders along rafters 4 and 10
for i in(3,9):
    nrm=np.array([-u(i)[1],u(i)[0]])*-5
    ax.plot([RC[i][0]+nrm[0],P[i][0]+nrm[0]],[RC[i][1]+nrm[1],P[i][1]+nrm[1]],color=C['dc'],lw=5,zorder=6)
    ax.plot(*(P[i]+u(i)*-9),marker='*',ms=22,mfc=C['inj'],mec='k',zorder=10)
    t=P[i]+u(i)*-24+np.array([-u(i)[1],u(i)[0]])*-15
    ax.text(*t,'feeders\n72"+36" taps',fontsize=10.5,ha='center',va='center',color='#b35900',weight='bold')
# V+ breaks on rails at post 7 and post 1
for i in(6,0):
    q=P[i]*1.0; ax.plot(*q,marker='X',ms=15,mfc='white',mec='k',mew=2,zorder=11)
# controller + outlet near post 1 (outside)
cb=np.array([-62.,-104.]); ax.add_patch(Rectangle(cb-np.array([9,6]),18,12,fc='#dfe9ff',ec='k',lw=2,zorder=8))
ax.text(-108,-114,'CONTROLLER BOX\n(K16A-B), outside\npost 1 near base',fontsize=11.5,ha='center',va='center',weight='bold',color='#1f3f8f')
outl=np.array([-62,-146]); ax.add_patch(Rectangle(outl-np.array([5,4]),10,8,fc='#ffd9d9',ec=C['ac'],lw=2,zorder=8))
ax.text(-50,-168,'AC outlet (GFCI) - ASSUMED location, within ~6 ft of post 1\nred solid = AC cord up post 1 + along rafter 1 to the hub',fontsize=11,color=C['ac'],ha='center',weight='bold')
# AC routes
ax.plot([outl[0]-2,cb[0]-2],[outl[1]+4,cb[1]-6],color=C['ac'],lw=2,ls='--',zorder=7)
nrm=np.array([-u(0)[1],u(0)[0]])*-5
pa=[outl+[5,4],P[0]+nrm+u(0)*3,RC[0]+nrm]
ax.plot([p[0] for p in pa],[p[1] for p in pa],color=C['ac'],lw=3.5,zorder=6)
# data leads from controller
ax.plot([cb[0]+9,P[0][0]],[cb[1]+3,P[0][1]],color=C['P1'],lw=3,zorder=7)
p12=P[11]+u(11)*9
ax.plot([cb[0]-4,p12[0]],[cb[1]+6,p12[1]],color=C['P2'],lw=3,ls=(0,(4,2)),zorder=7)
ax.text(*(p12+np.array([-22,-8])),'P2 lead\nat floor',fontsize=10.5,color=C['P2'],weight='bold',ha='center')
# legend
L=[('Data P1: U1 > ring > U2 > U3 > U4 > U5 > U6 (500 px)',C['P1'],'-'),('Data P2: U12 > U11 > U10 > U9 > U8 > U7 (450 px)',C['P2'],'-'),
   ('Data P3: 72" rails f1 > f12 (300 px, outer)',C['P3'],'-'),('Data P4: 36" rails f12 > f2 (275 px, inner)',C['P4'],'-'),
   ('dashed arc = base hop (floor), solid arc = ring hop',"#555",'--'),('12 V feed (hub tap / rail feeder)',C['dc'],'-'),('AC mains (assumed outlet)',C['ac'],'-')]
for k,(t,c,ls) in enumerate(L):
    y=-118-k*0  # placeholder
lx,ly=50,-132
ax.add_patch(FancyBboxPatch((lx-3,ly-54),104,60,boxstyle='round,pad=1',fc='white',ec='#999',zorder=12))
for k,(t,c,ls) in enumerate(L):
    yy=ly-k*6.6
    ax.plot([lx,lx+9],[yy,yy],color=c,lw=3,ls=ls,zorder=13); ax.text(lx+11,yy,t,fontsize=10,va='center',zorder=13)
ax.plot(lx+4.5,ly-7*6.6,marker='*',ms=15,mfc=C['inj'],mec='k',zorder=13); ax.text(lx+11,ly-7*6.6,'injection (fused tap)   X = V+ break on rails',fontsize=10,va='center',zorder=13)
ax.text(-148,128,'Gx = which 12 V supply feeds that unit\n(G1..G4 = PSU 1..4 in the hub)\nArrow = data direction on each rafter;\nevery unit is powered only from its ring end.',fontsize=11,va='top',color='#333')

# ---------------- ELEVATION ----------------
ex=fig.add_axes([0.548,0.47,0.447,0.44]); ex.set_xlim(-170,125); ex.set_ylim(-16,122)
ex.set_title('2. Elevation (developed section post 1 - ring hub - post 10; inches, vertical x1.5)',fontsize=17,weight='bold',loc='left')
ex.set_xticks([]); ex.set_yticks([0,36,72,89]); ex.tick_params(labelsize=12); ex.grid(axis='y',ls=':',alpha=.5)
for s in('top','right','bottom'): ex.spines[s].set_visible(False)
ex.axhline(0,color='#6b4f2a',lw=4)
for xs in(-R,R):
    ex.add_patch(Rectangle((xs-1.75,0),3.5,71,fc='#deb887',ec='k'))
    sg=np.sign(xs)
    ex.plot([xs,sg*ROUT],[72.5,89],color='#a0522d',lw=7,solid_capstyle='butt')
    for z in(36,72): ex.add_patch(Rectangle((xs-sg*1.75-(14 if sg>0 else 0),z-1.75),14,3.5,fc='#f0d9a8',ec='k',lw=.8))
    zz=np.arange(1,70,2); ex.plot([xs-sg*3]*len(zz),zz,'o',ms=2.6,color=C['P1' if sg<0 else 'P2'])
    t=np.linspace(0.03,0.97,40); ex.plot(xs+(sg*ROUT-xs)*t,72.5+(89-72.5)*t-2.5,'o',ms=2.6,color=C['P1' if sg<0 else 'P2'])
ex.add_patch(Rectangle((-ROUT,89),2*ROUT,3.5,fc='#8b4513',ec='k'))
ex.add_patch(FancyBboxPatch((-9,93.5),18,8,boxstyle='round,pad=0.4',fc='#fff4d6',ec='k',lw=2))
ex.text(0,113,'PSU HUB box on top of ring (~16x14x7")\n4 x LRS-350-12 + 4 fuse blocks + GND bus',fontsize=11.5,ha='center',va='center',weight='bold')
ex.plot([0,0],[101.9,107.5],color='k',lw=1)
# AC: outlet -> post 1 -> rafter 1 -> hub
ex.add_patch(Rectangle((-162,14),9,9,fc='#ffd9d9',ec=C['ac'],lw=2)); ex.text(-157.5,11,'AC outlet\n(assumed)',ha='center',va='top',fontsize=10.5,color=C['ac'],weight='bold')
ex.plot([-153,-140,-140,-131],[17,17,12,12],color=C['ac'],lw=2,ls='--')
ex.plot([-157.5,-157.5,-101.5,-101.5],[23,34,34,76],color=C['ac'],lw=3.5)
ex.plot([-101.5,-ROUT-2,-9],[76,94,97],color=C['ac'],lw=3.5)
ex.text(-168,64,'AC cord (SJOOW 14/3,\n~22 ft): up outside of\npost 1, along top of\nrafter 1 to the hub',color=C['ac'],fontsize=10.5,weight='bold',ha='left',va='center')
# controller box
ex.add_patch(Rectangle((-131,6),22,20,fc='#dfe9ff',ec='k',lw=2)); ex.text(-120,16,'K16A-B\nbox',ha='center',va='center',fontsize=10,weight='bold',color='#1f3f8f')
ex.plot([-109,-99],[9,1],color=C['P1'],lw=2.5); ex.text(-112,-9,'P1',color=C['P1'],fontsize=11,weight='bold')
ex.plot([-109,-105,-105,-99],[22,22,72,72],color=C['P3'],lw=2.5); ex.text(-113,73,'P3',color=C['P3'],fontsize=11,weight='bold')
ex.plot([-109,-108,-108,-99],[18,18,36,36],color=C['P4'],lw=2.5); ex.text(-116,38,'P4',color=C['P4'],fontsize=11,weight='bold')
# hub taps at ring ends
for xs in(-ROUT,ROUT):
    ex.plot([np.sign(xs)*9,xs],[95,88],color=C['dc'],lw=2)
    ex.plot(xs,87,marker='*',ms=17,mfc=C['inj'],mec='k',zorder=9)
ex.annotate('unit taps at ring ends\n(12 units + ring)',xy=(ROUT+1,87),xytext=(44,100),fontsize=10.5,color='#b35900',weight='bold',arrowprops=dict(arrowstyle='->',color='#b35900'))
# rail feeder down rafter 10 / post 10
ex.plot([9,ROUT+2,R-4,R-4,R-4],[98,93,76,72,36],color=C['dc'],lw=4.5)
for z in(72,36): ex.plot(R-4,z,marker='*',ms=20,mfc=C['inj'],mec='k',zorder=9)
ex.text(R-8,48,'12/2 feeders along rafter 10,\ndown post 10 to the\n72" and 36" rail taps',fontsize=10.5,color='#b35900',weight='bold',ha='right')
# dimensions
ex.annotate('',xy=(R+9,0),xytext=(R+9,71),arrowprops=dict(arrowstyle='<->',lw=1.2)); ex.text(R+11,35,'post 71"',fontsize=11,rotation=90,va='center')
ex.text(-55,99,'rafter ~84"',fontsize=11,ha='center')
ex.text(-60,40,'U1: data up\n(post, then rafter)',fontsize=11,color=C['P1'],ha='center',weight='bold')
ex.text(62,40,'U10: data up',fontsize=11,color=C['P2'],ha='center',weight='bold')
ex.text(-10,-11,'ground / deck',fontsize=10.5,color='#6b4f2a',ha='center')

# ---------------- TABLES ----------------
tx=fig.add_axes([0.52,0.02,0.475,0.42]); tx.axis('off'); tx.set_xlim(0,100); tx.set_ylim(0,100)
tx.text(0,98,'3. Ports, 12 V supplies and taps',fontsize=17,weight='bold',va='top')
hdr=['Port','Chain (data order)','px','Start (data lead)']
rowsP=[('P1','U1 > ring > U2 > U3 > U4 > U5 > U6','500','post 1 base (~3 ft)'),
       ('P2','U12 > U11 > U10 > U9 > U8 > U7','450','post 12 base (~6 ft at floor)'),
       ('P3','72" rails f1 > f2 > ... > f12 (loop)','300','post 1 at 72" (~6 ft)'),
       ('P4','36" rails f12 > f11 > ... > f2','275','post 1 at 36" (~3 ft)')]
xs=[0,8,58,65]; y=89
for x,h in zip(xs,hdr): tx.text(x,y,h,fontsize=12.5,weight='bold')
for r in rowsP:
    y-=5.6
    for k,(x,v) in enumerate(zip(xs,r)): tx.text(x,y,v,fontsize=12.5,color=C[r[0]] if k==0 else 'k',weight='bold' if k==0 else 'normal')
y-=8.5
hdr2=['PSU','Fused taps (all at the hub except rail feeders)','worst A','load']
rowsG=[('G1','U1-U5 (5 x 7.5 A)','22.5','77%'),('G2','U6-U9 (4 x 7.5 A) + ring (5 A)','21.0','72%'),
       ('G3','U10 + post-10 feeders 72" & 36" (2 x 10 A)','22.5','77%'),('G4','U11, U12 + post-4 feeders 72" & 36" (2 x 10 A)','25.5','87%')]
xs2=[0,8,70,82]
for x,h in zip(xs2,hdr2): tx.text(x,y,h,fontsize=12.5,weight='bold')
for r in rowsG:
    y-=5.6
    for k,(x,v) in enumerate(zip(xs2,r)): tx.text(x,y,v,fontsize=12.5,color=C[r[0]] if k==0 else 'k',weight='bold' if k==0 else 'normal')
y-=5.6; tx.text(0,y,'Total 1,525 px x 0.06 A = 91.5 A (1,098 W) worst case; ~30 A typical. 4 x 29.2 A = 116.8 A available.',fontsize=12)
y-=8.5; tx.text(0,y,'Worst-case drop (0.06 A/px, 18 AWG string, 2" lead, 12 AWG rail feeders)',fontsize=12.5,weight='bold')
for t in('Unit, fed at ring end: 0.47 V (4.0%)     Ring: 0.20 V (1.6%)',
         '72" rail tap: 0.75 V (6.2%)     36" rail tap (11 ft feeder): 0.83 V (6.9%)',
         'Rule: V+ is cut on every jumper between separately fed segments (base hops, ring hops,',
         'controller leads, rails at post 7). GND and data always continue; all PSU V- tied at the hub.'):
    y-=5.2; tx.text(0,y,t,fontsize=12)
fig.savefig(out,dpi=100)
print('wrote',out)
