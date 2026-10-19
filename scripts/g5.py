import os
for _d in('renders','model','build'):os.makedirs(_d,exist_ok=True)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
N=12; INSIDE=192.0; PD=3.5
Rc=(INSIDE+PD)/2                     # post-centre circumradius: inside faces at Rc-1.75 -> 2*(Rc-1.75)=192
S=2*Rc*np.sin(np.pi/N)               # side length (centre-to-centre)
R=Rc
PH=71.0; JT=1.5; WT=PH+JT; RING_Z=89.0; RING_T=3.5
apo_in,apo_out=22.5/2,29.5/2
rin,rout=apo_in/np.cos(np.pi/N),apo_out/np.cos(np.pi/N)
ang=np.radians(-75+30*np.arange(N))   # post 1 just right of the entrance; entrance = face 12 (post 12 -> post 1) at -y
P=np.c_[R*np.cos(ang),R*np.sin(ang)]
def box(p0,p1,w,t,nrm):
    p0=np.array(p0,float);p1=np.array(p1,float);d=p1-p0;d/=np.linalg.norm(d)
    nrm=np.array(nrm,float);nrm/=np.linalg.norm(nrm)
    u=np.cross(d,nrm);u/=np.linalg.norm(u)
    c=[p0+sa*u*w/2+sb*nrm*t/2 for sa,sb in[(-1,-1),(1,-1),(1,1),(-1,1)]]
    c1=[x+(p1-p0) for x in c]
    return [c,c1]+[[c[k],c[(k+1)%4],c1[(k+1)%4],c1[k]] for k in range(4)]
def z3(p,z): return np.array([p[0],p[1],z],float)
def fnorm(a,b):
    m=(a+b)/2; n=np.array([m[0],m[1],0.]); return n/np.linalg.norm(n)
G={k:[] for k in['post','joist','r36','r72','brace_upper','brace_lower','rafter','ring']}

for i in range(N):
    j=(i+1)%N; a,b=P[i],P[j]
    rad=np.array([np.cos(ang[i]),np.sin(ang[i]),0]); 
    G['post']+=box(z3(a,0),z3(a,PH),1.5,PD,rad)
    G['joist']+=box(z3(a,PH+JT/2),z3(b,PH+JT/2),3.5,JT,[0,0,1])
    fn=fnorm(a,b); out=0*fn
    G['r72']+=box(z3(a,72)+out,z3(b,72)+out,3.5,0.75,fn)
    if i!=N-1: G['r36']+=box(z3(a,36)+out,z3(b,36)+out,3.5,0.75,fn)
    # braces at post i, toward face i (next post) and face i-1 (previous post)
    for face,other in[(i,P[j]),((i-1)%N,P[i-1])]:
        t=(other-a)/np.linalg.norm(other-a); fnn=fnorm(a,other)
        for kind,zv,zr in[('brace_upper',56.0,70.25),('brace_lower',20.0,34.25)]:
            if kind=='brace_lower' and face==N-1: continue
            # V opening upward: vertex on post centreline at zv, far end touches underside of rail at zr
            c=3.5*np.sqrt(2)/2; ds=zr-zv; ps=0.75   # ps = post half-width (cut flush to post face)
            poly2=[(ps,zv+ps-c),(ds+c,zr),(ds-c,zr),(ps,zv+ps+c)]  # parallelogram in rail plane
            for sg in(-1,1): pass
            lo=[z3(a+t*u,z)-fnn*0.75 for u,z in poly2]; hi=[z3(a+t*u,z)+fnn*0.75 for u,z in poly2]
            G[kind]+=[lo,hi]+[[lo[q],lo[(q+1)%4],hi[(q+1)%4],hi[q]] for q in range(4)]
    top=z3(a,WT); pk=z3(rout*np.array([np.cos(ang[i]),np.sin(ang[i])]),RING_Z)
    G['rafter']+=box(top,pk,3.5,1.5,np.cross([-np.sin(ang[i]),np.cos(ang[i]),0],pk-top))
# ring (12-gon annulus), corners aligned with posts
def rp(r,z): return [z3(r*np.array([np.cos(x),np.sin(x)]),z) for x in ang]
oi,ob=rp(rout,RING_Z+RING_T),rp(rout,RING_Z); ii,ib=rp(rin,RING_Z+RING_T),rp(rin,RING_Z)
for i in range(N):
    j=(i+1)%N
    for q in([ob[i],ob[j],oi[j],oi[i]],[ib[i],ib[j],ii[j],ii[i]],[oi[i],oi[j],ii[j],ii[i]],[ob[i],ob[j],ib[j],ib[i]]):
        G['ring'].append(q)
col={'post':'#deb887','joist':'#c9a26b','r36':'#f0d9a8','r72':'#f0d9a8','brace_upper':'#d2691e','brace_lower':'#2e8b57','rafter':'#a0522d','ring':'#8b4513'}
def draw(ax,el,az):
    for k,v in G.items(): ax.add_collection3d(Poly3DCollection(v,fc=col[k],ec='k',lw=.25))
    ax.set_xlim(-115,115);ax.set_ylim(-115,115);ax.set_zlim(0,230);ax.set_box_aspect((1,1,1));ax.view_init(el,az)
    for i in range(N):
        r=np.array([np.cos(ang[i]),np.sin(ang[i])])*(R+14)
        ax.text(r[0],r[1],(PH+6) if el<80 else 0,f'#{i+1}',color='blue',fontsize=11,fontweight='bold',ha='center')
    ax.text(0,-R-35,0,'ENTRANCE (no 36" rail / lower braces)',color='red',fontsize=9,ha='center')
fig=plt.figure(figsize=(18,9))
ax=fig.add_subplot(121,projection='3d');draw(ax,20,-75);ax.set_title('Isometric (inches)')
ax=fig.add_subplot(122,projection='3d');draw(ax,90,-90);ax.set_title('Top-down (posts CCW from entrance; entrance = face #12-#1 at bottom)')
fig.suptitle(f'Gazebo v5: 12-gon side {S:.1f}", inside post-to-post 192", posts 71", ring base 89", ring hole 22.5/29.5" flat-to-flat. Orange=upper braces, green=lower braces')
plt.savefig('renders/gazebo_model_v5.png',dpi=100)
n=0
with open('model/gazebo_v5.obj','w') as o:
    for k,vv in G.items():
        o.write(f'o {k}\n')
        for poly in vv:
            for q in poly:o.write("v %.3f %.3f %.3f\n"%tuple(q))
            o.write("f "+" ".join(str(n+m+1) for m in range(len(poly)))+"\n");n+=len(poly)
print(Rc,S,rin,rout)
top=np.array([R,0,WT]);pk=np.array([rout,0,RING_Z]);print('rafter len',np.linalg.norm(top-pk))
# close-ups of face 5 (posts 6-7)
f=5;a,b=P[f],P[(f+1)%N];m=(a+b)/2;fa=np.degrees(np.arctan2(m[1],m[0]))
fig=plt.figure(figsize=(18,7))
for k,(el,az) in enumerate([(5,fa),(15,fa-40),(15,fa+40)]):
    ax=fig.add_subplot(1,3,k+1,projection='3d')
    for kk,v in G.items(): ax.add_collection3d(Poly3DCollection(v,fc=col[kk],ec='k',lw=.3))
    h=42;ax.set_xlim(m[0]-h,m[0]+h);ax.set_ylim(m[1]-h,m[1]+h);ax.set_zlim(40-h,40+h);ax.set_box_aspect((1,1,1));ax.view_init(el,az)
    ax.set_title(f'Face between posts #{f+1}-#{f+2}: elev {el}, azim {az:.0f}')
fig.suptitle('Close-up v5: upper braces (orange) and lower braces (green) are V-shapes, vertex on post, ends touching rail undersides, coplanar with rails')
plt.savefig('renders/gazebo_closeup_v5.png',dpi=100)

# ---------------- night render ----------------
pix=[];pcol=[];LAB=[]  # (x,y,z), colour
import colorsys
def inward(p): 
    r=np.array([p[0],p[1]]);n=np.linalg.norm(r);return -r/n
def addp(pt,hue):
    pix.append(pt);pcol.append(colorsys.hsv_to_rgb(hue%1,0.85,1))
WARM=(1.0,0.78,0.45)
cnt={}
def add_member(name,pts,cols):
    cnt[name]=cnt.get(name,0)+len(pts)
    LAB.extend([(name,0 if name=='ring' else globals()['i'])]*len(pts))
    for p,c in zip(pts,cols): pix.append(p);pcol.append(c)
for i in range(N):
    a=P[i];j=(i+1)%N;b=P[j];ni=inward(a)
    # posts: along centreline every 2", shifted to inner face (1.75" radial inward)
    zs=np.arange(1,PH,2.0); pts=[z3(a+ni*1.9,z) for z in zs]
    add_member('posts',pts,[WARM]*len(pts))
    L=np.linalg.norm(b-a);t=(b-a)/L;nin=inward((a+b)/2)
    ss=1.3+2.0*np.arange(25)   # 25-px string per face, 2" pitch, centred (48" span)
    off=nin*(0.75/2+0.3)
    if i!=N-1:   # entrance face 12 has no 36" rail
        pts=[z3(a+t*u+off,36) for u in ss]; add_member('rails36',pts,[colorsys.hsv_to_rgb(0.55,0.8,1)]*len(pts))
    # 72" rail pixels sit on the inner face of the top-joist/rail stack: the 2x4 joist (71-72.5", 3.5" wide, centred on
    # the post line) encloses z=72 out to 1.75" inward, so a pixel at the rail's own face (0.675") would be buried in it.
    off72=nin*(3.5/2+0.3)
    pts=[z3(a+t*u+off72,72) for u in ss]; add_member('rails72',pts,[colorsys.hsv_to_rgb(0.85,0.8,1)]*len(pts))
    # (top joists carry NO pixels: they duplicate the 72" rails)
    top=z3(a,WT-0.8);pk=z3(rout*np.array([np.cos(ang[i]),np.sin(ang[i])]),RING_Z-0.8)
    Lr=np.linalg.norm(pk-top);d=(pk-top)/Lr;us=2.0+2.0*np.arange(40)   # 40 rafter px (35 post + 40 rafter = 75 per unit)
    pts=[top+d*u for u in us]; add_member('rafters',pts,[colorsys.hsv_to_rgb(0.3+0.02*k,0.8,1) for k in range(len(pts))])
# ring: centreline at mid apothem, perimeter every 2"
rm=(apo_in+apo_out)/2/np.cos(np.pi/N)
rc=rp(rm,RING_Z-0.3)   # on the ring's underside, facing down (the old centre line at RING_Z+RING_T/2 was inside the wood)
# 50 pixels equally spaced along the ring perimeter (pitch ~1.7")
_L=[np.linalg.norm(rc[(i+1)%N]-rc[i]) for i in range(N)];_cum=np.r_[0,np.cumsum(_L)];pts=[]
for _k in range(50):
    _s=_k*_cum[-1]/50;_i=min(int(np.searchsorted(_cum,_s,side='right')-1),N-1);_u=(_s-_cum[_i])/_L[_i]
    pts.append(rc[_i]+(rc[(_i+1)%N]-rc[_i])*_u)
add_member('ring',pts,[colorsys.hsv_to_rgb(0.0,0.0,1)]*len(pts))
pix=np.array(pix);pcol=np.array(pcol);TOTAL=len(pix)
print('PIXELS',TOTAL,cnt)
def night(ax,el,az,cut=False,lim=None):
    ax.set_facecolor('#02030a')
    cv=np.array([np.cos(np.radians(az)),np.sin(np.radians(az))])
    for k,v in G.items():
        vv=[q for q in v if not cut or np.mean([x[:2] for x in q],axis=0)@cv<5]
        ax.add_collection3d(Poly3DCollection(vv,fc='#14100c',ec='#2b2118',lw=.2))
    m=np.ones(len(pix),bool) if not cut else (pix[:,:2]@cv<5)
    p=pix[m];c=pcol[m]
    for sz,al in[(260,.04),(110,.09),(40,.2),(9,1.0)]:
        ax.scatter(p[:,0],p[:,1],p[:,2],s=sz,c=c,alpha=al,linewidths=0,depthshade=False)
    ax.scatter(p[:,0],p[:,1],p[:,2],s=2,c='white',alpha=.9,linewidths=0,depthshade=False)
    h=lim or 115
    ax.set_xlim(-h,h);ax.set_ylim(-h,h);ax.set_zlim(0,2*h*0.6);ax.set_box_aspect((1,1,0.6),zoom=1.7);ax.view_init(el,az);ax.set_axis_off()
fig=plt.figure(figsize=(18,9),facecolor='#02030a')
ax=fig.add_subplot(121,projection='3d');night(ax,20,-60);ax.set_title('Isometric',color='#99a')
ax=fig.add_subplot(122,projection='3d');night(ax,12,90,cut=True,lim=105);ax.set_title('Cutaway from inside: entrance wall (far side cut away near half)',color='#99a')
fig.suptitle(f'Gazebo at night - {TOTAL} pixels @ 2" spacing (no pixels on braces)',color='white')
plt.savefig('renders/gazebo_night.png',dpi=100,facecolor=fig.get_facecolor())
