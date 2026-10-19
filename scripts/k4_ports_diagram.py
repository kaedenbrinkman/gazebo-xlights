import numpy as np, matplotlib, os
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, FancyBboxPatch, Circle
C={1:'#1f5fbf',2:'#0f9b8e',3:'#c2185b',4:'#7b3fb3'}
unit_port={1:1,2:2,3:2,4:2,5:3,6:3,7:3,8:4,9:4,10:4,11:1,12:1}
down={1,2,4,5,7,8,10,11}
rails={1:{'72':[(1,2),(2,3),(3,4)],'36':[(4,3),(3,2)]},
       2:{'36':[(4,5),(5,6),(6,7)],'72':[(7,6),(6,5),(5,4)]},
       3:{'36':[(7,8),(8,9),(9,10)],'72':[(10,9),(9,8),(8,7)]},
       4:{'36':[(10,11),(11,12),(12,1)],'72':[(1,12),(12,11),(11,10)]}}
jump={1:[(1,'base>72"'),(4,'72">36"')],2:[(4,'base>36"'),(7,'36">72"')],3:[(7,'base>36"'),(10,'36">72"')],4:[(10,'base>36"'),(1,'36">72"')]}
floor={1:(11,12),2:(2,3),3:(5,6),4:(8,9)}
ringhop={1:(12,1),2:(3,4),3:(6,7),4:(9,10)}
start_u={1:11,2:2,3:5,4:8}
ends={1:(2,'36'),2:(4,'72'),3:(7,'72'),4:(10,'72')}
px={1:400,2:375,3:375,4:375}
fig=plt.figure(figsize=(24,16),dpi=100,facecolor='white')
fig.text(0.5,0.972,'Kulp K4-PB: 4 ports, 1,525 px (400 / 375 / 375 / 375)',ha='center',fontsize=30,fontweight='bold')
def arr(ax,a,b,c,lw=4,ms=24,ls='-',z=7):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=ms,color=c,lw=lw,linestyle=ls,zorder=z,shrinkA=0,shrinkB=0))
# ================= plan =================
ax=fig.add_axes([0.012,0.315,0.405,0.62],facecolor='#fcfcfa');ax.set_aspect('equal');ax.set_xlim(-158,158);ax.set_ylim(-178,150);ax.set_xticks([]);ax.set_yticks([])
ax.set_title('1. Plan view (from above), posts 1-12 CCW from the entrance',fontsize=20,fontweight='bold',loc='left',pad=8)
for s in ax.spines.values():s.set_color('#bbb')
R=100;rin=24
ang=np.radians(-105+30*np.arange(12));P=np.c_[R*np.cos(ang),R*np.sin(ang)];U=np.c_[np.cos(ang),np.sin(ang)]
ax.add_patch(Polygon(P,fill=False,ec='#aaa',lw=3,zorder=1))
ax.plot([P[0][0],P[1][0]],[P[0][1],P[1][1]],color='red',lw=9,solid_capstyle='butt',zorder=2)
ax.text(0,-168,'ENTRANCE (face 1)',ha='center',va='center',fontsize=19,color='red',fontweight='bold')
RR=np.c_[rin*np.cos(ang),rin*np.sin(ang)]
ax.add_patch(Polygon(RR,fill=True,fc='white',ec='#8b4513',lw=3,zorder=3))
# units
for k in range(1,13):
    p=unit_port[k];a=RR[k-1];b=P[k-1]
    if k not in down:a,b=b,a
    arr(ax,a*0.999,b*0.999,C[p],5,26)
    m=(P[k-1]+RR[k-1])/2*1.0
    ax.text(*(U[k-1]*(rin+0.5*(R-rin))+0),f"U{k}\n{'dn' if k in down else 'up'}",fontsize=14,ha='center',va='center',color=C[p],fontweight='bold',zorder=9,bbox=dict(fc='white',ec='none',alpha=.9,pad=1))
    ax.add_patch(Rectangle(P[k-1]-5,10,10,fc='#deb887',ec='k',lw=1.5,zorder=8))
    ax.text(*(U[k-1]*(R*1.30)),str(k),fontsize=26,fontweight='bold',ha='center',va='center')
# rails
for p,d in rails.items():
    for kind,segs in d.items():
        sc=0.88 if kind=='72' else 0.76
        for a,b in segs:
            A=P[a-1]*sc;B=P[b-1]*sc
            ax.plot([A[0],B[0]],[A[1],B[1]],color=C[p],lw=6,ls='-' if kind=='72' else (0,(3,1.6)),zorder=5,solid_capstyle='butt')
            m=(A+B)/2;dv=(B-A)/np.linalg.norm(B-A)
            arr(ax,m-dv*5,m+dv*5,C[p],0.1,26,z=6)
# floor hops (outside the wall)
for p,(a,b) in floor.items():
    A=P[a-1]*1.09;B=P[b-1]*1.09
    ax.add_patch(FancyArrowPatch(A,B,arrowstyle='-|>',mutation_scale=24,color=C[p],lw=4,linestyle=(0,(1.5,1.2)),zorder=7,connectionstyle='arc3,rad=-0.12'))
# ring hops (just outside ring)
for p,(a,b) in ringhop.items():
    A=RR[a-1]*1.45;B=RR[b-1]*1.45
    ax.add_patch(FancyArrowPatch(A,B,arrowstyle='-|>',mutation_scale=18,color=C[p],lw=3.5,linestyle=(0,(1.5,1.2)),zorder=10,connectionstyle='arc3,rad=-0.25'))
# P1 ring path (once round CCW)
a0=ang[10];t=np.linspace(a0,a0+2*np.pi*0.985,200);ax.plot((rin+4)*np.cos(t),(rin+4)*np.sin(t),color=C[1],lw=5,zorder=4)
arr(ax,((rin+4)*np.cos(t[-2]),(rin+4)*np.sin(t[-2])),((rin+4)*np.cos(t[-1]),(rin+4)*np.sin(t[-1])),C[1],5,24)
# jumpers
for p,js in jump.items():
    seen={}
    for post,lab in js:
        n=seen.get(post,0);seen[post]=n+1
    for post,lab in js:
        pass
cnt={}
for p,js in jump.items():
    for post,lab in js:
        i=cnt.get(post,0);cnt[post]=i+1
        t=np.array([-U[post-1][1],U[post-1][0]])
        q=P[post-1]*0.945+t*(-8+16*i)
        ax.add_patch(Polygon([q+[0,8],q+[8,0],q+[0,-8],q+[-8,0]],fc=C[p],ec='k',lw=1.5,zorder=11))
# controller
ax.add_patch(Rectangle((-10,-10),20,20,fc='#222',ec='k',zorder=12));ax.text(0,0,'K4',color='white',ha='center',va='center',fontsize=15,fontweight='bold',zorder=13)
for p,u in start_u.items():
    q=RR[u-1]
    ax.plot([0,q[0]],[0,q[1]],color=C[p],lw=3.5,ls=(0,(2,1.2)),zorder=11)
    ax.add_patch(Circle(q,6.5,fc=C[p],ec='k',lw=1.5,zorder=14));ax.text(q[0],q[1],f'S{p}',color='white',ha='center',va='center',fontsize=10.5,fontweight='bold',zorder=15)
for p,(post,kind) in ends.items():
    q=P[post-1]*(0.88 if kind=='72' else 0.76)
    ax.add_patch(Rectangle(q-7,14,14,fc=C[p],ec='k',lw=2,zorder=14));ax.text(q[0],q[1],f'E{p}',color='white',ha='center',va='center',fontsize=10.5,fontweight='bold',zorder=15)
ax.annotate('Kulp K4-PB\nin the ring box',xy=(8,8),xytext=(95,128),fontsize=17,fontweight='bold',ha='center',arrowprops=dict(arrowstyle='-|>',lw=2.5,color='k'),zorder=20,bbox=dict(fc='white',ec='#888'))
ax.text(-154,146,'ring drawn 1.6x larger\nthan true scale',fontsize=14,color='#555',va='top')
# ================= elevation =================
ax=fig.add_axes([0.435,0.315,0.553,0.62],facecolor='#fcfcfa')
ax.set_title('2. Unrolled elevation: 12 faces left to right (entrance face 1 at left)',fontsize=20,fontweight='bold',loc='left',pad=8)
ax.set_xlim(-0.85,13.7);ax.set_ylim(-19,128);ax.set_xticks([]);ax.set_yticks([])
for s in ax.spines.values():s.set_color('#bbb')
X=lambda k:k-1  # x of post k (post 1 also at x=12)
# members
for k in range(1,14):
    x=k-1;ax.plot([x,x],[0,72.5],color='#d9b88f',lw=11,solid_capstyle='butt',zorder=1)
    ax.plot([x,x],[72.5,89],color='#caa57a',lw=4,zorder=1)
    ax.text(x,-5.5,f'post {k if k<13 else 1}',ha='center',va='center',fontsize=15,fontweight='bold')
for f in range(1,13):
    ax.text(f-0.5,-13,f'face {f}'+('\n(entrance)' if f==1 else ''),ha='center',va='center',fontsize=13,color='#444')
    ax.plot([f-1,f],[72,72],color='#cfc7bb',lw=4,zorder=1)
    if f!=1:ax.plot([f-1,f],[36,36],color='#cfc7bb',lw=4,zorder=1)
ax.text(0.55,27,'no 36" rail',ha='center',va='center',fontsize=12,color='red',bbox=dict(fc='white',ec='none',alpha=.9,pad=1),zorder=9)
ax.plot([0,1],[36,36],color='red',lw=2,ls=':',zorder=1)
ax.add_patch(Rectangle((-0.1,89),12.2,4,fc='#e9d8c4',ec='#8b4513',lw=2,zorder=1))
ax.text(12.25,91,'ring\n50 px',ha='left',va='center',fontsize=13,color='#8b4513',fontweight='bold')
ax.text(13.6,72,'72"',ha='right',va='bottom',fontsize=13,color='#555');ax.text(13.6,36,'36"',ha='right',va='bottom',fontsize=13,color='#555')
# units
OFF=0.09
for k in range(1,13):
    p=unit_port[k];x=X(k)+OFF
    if k in down: arr(ax,(x,89),(x,0.6),C[p],5,26);yl=60
    else: arr(ax,(x,0.6),(x,89),C[p],5,26);yl=60
    ax.text(x+0.1,80,f"U{k} {'dn' if k in down else 'up'}",fontsize=14,color=C[p],fontweight='bold',ha='left',va='center',zorder=9,bbox=dict(fc='white',ec='none',alpha=.9,pad=1))
# floor hops
for p,(a,b) in floor.items():
    arr(ax,(X(a)+OFF,3.5),(X(b)+OFF,3.5),C[p],4,24,ls=(0,(1.5,1.2)))
    ax.text((X(a)+X(b))/2+OFF,9,f'floor hop f{a}',ha='center',fontsize=12,color=C[p],fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.9,pad=1))
# ring hops
for p,(a,b) in ringhop.items():
    xa=X(a)+OFF;xb=X(b)+OFF
    if b==1:
        arr(ax,(xa,97),(12.45,97),C[p],4,22,ls=(0,(1.5,1.2)));ax.text(12.5,99,'wraps to post 1 (left)',fontsize=12,color=C[p],ha='right',va='bottom',bbox=dict(fc='white',ec='none',alpha=.9,pad=1),zorder=9)
        arr(ax,(-0.7,97),(xb,97),C[p],4,22,ls=(0,(1.5,1.2)))
    else:
        arr(ax,(xa,97),(xb,97),C[p],4,22,ls=(0,(1.5,1.2)))
        ax.text((xa+xb)/2,99,'ring hop',fontsize=12,color=C[p],ha='center',va='bottom',fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.9,pad=1),zorder=9)
# P1 ring path
ax.plot([10,12.2],[91,91],color=C[1],lw=5,zorder=4);ax.plot([-0.1,10],[91,91],color=C[1],lw=5,zorder=4)
arr(ax,(11.7,91),(12.2,91),C[1],5,22);arr(ax,(9.2,91),(9.9,91),C[1],5,22)
# rails and jumpers
for p,d in rails.items():
    for kind,segs in d.items():
        z=72 if kind=='72' else 36
        for a,b in segs:
            xa=X(a) if not(a==1 and b==12) else 12;xb=X(b) if not(b==1 and a==12) else 12
            # face crossing the wrap: post 1 drawn at x=12 for P4 (and at x=0 for P1)
            if p==4 and kind=='36':
                xa={10:9,11:10,12:11}.get(a,xa);xb={11:10,12:11,1:12}.get(b,xb)
            if p==4 and kind=='72':
                xa={1:12,12:11,11:10}.get(a,xa);xb={12:11,11:10,10:9}.get(b,xb)
            ax.plot([xa,xb],[z,z],color=C[p],lw=7,zorder=5,solid_capstyle='butt')
            m=(xa+xb)/2;dd=0.12*(1 if xb>xa else -1)
            arr(ax,(m-dd,z),(m+dd,z),C[p],0.1,28,z=8)
for p,js in jump.items():
    for post,lab in js:
        x=X(post)-OFF if not(p==4 and post==1) else 12-OFF
        z0,z1={'base>72"':(0,72),'72">36"':(72,36),'base>36"':(0,36),'36">72"':(36,72)}[lab]
        arr(ax,(x,z0+4),(x,z1),C[p],4,24,ls=(0,(1.5,1.2)))
        ax.text(x-0.1,{'base>72"':40,'72">36"':54,'base>36"':22,'36">72"':54}[lab],'jumper\n'+lab,fontsize=11.5,color=C[p],fontweight='bold',ha='right',va='center',bbox=dict(fc='white',ec='none',alpha=.9,pad=1),zorder=9)
# controller + leads
ax.add_patch(FancyBboxPatch((5.0,111),2.0,12,boxstyle='round,pad=0.02',fc='#222',ec='k',lw=2,zorder=10))
ax.text(6.0,117,'Kulp K4-PB\n(ring box)',color='white',ha='center',va='center',fontsize=14,fontweight='bold',zorder=11)
for p,u in start_u.items():
    x=X(u)+OFF
    ax.plot([6.0,x],[111,94],color=C[p],lw=3,ls=(0,(2,1.2)),zorder=2,alpha=.8)
    ax.add_patch(Circle((x,91),0.0,fc='none'))
    ax.scatter([x],[91],s=420,c=C[p],edgecolors='k',zorder=12);ax.text(x,91,f'S{p}',color='white',ha='center',va='center',fontsize=11,fontweight='bold',zorder=13)
for p,(post,kind) in ends.items():
    x=X(post);z=72 if kind=='72' else 36
    ax.scatter([x],[z],s=520,marker='s',c=C[p],edgecolors='k',zorder=12);ax.text(x,z,f'E{p}',color='white',ha='center',va='center',fontsize=11,fontweight='bold',zorder=13)
ax.text(0.0,124,'4 leads ~2 ft (data + GND only)',fontsize=13,color='#333',ha='left',va='center')
# ================= legend / table =================
ax=fig.add_axes([0.012,0.02,0.976,0.275],facecolor='white');ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off')
hd=[(1,'Port'),(9,'Pixels (nodes)'),(21,'Start'),(35,'Path (data order)'),(88,'End')]
for x,h in hd:ax.text(x,94,h,fontsize=17,fontweight='bold',va='center')
ax.plot([0,100],[88,88],color='k',lw=2)
rows=[(1,'400 (1-400)','ring, rafter 11 end','ring (once round) > U11 dn > floor hop f11 > U12 up > ring hop > U1 dn > post 1 jumper base>72" > 72" f1-f3 > post 4 jumper 72">36" > 36" f3-f2','36" at post 2'),
      (2,'375 (401-775)','rafter 2, ring end','U2 dn > floor hop f2 > U3 up > ring hop > U4 dn > post 4 jumper base>36" > 36" f4-f6 > post 7 jumper 36">72" > 72" f6-f4','72" at post 4'),
      (3,'375 (776-1150)','rafter 5, ring end','U5 dn > floor hop f5 > U6 up > ring hop > U7 dn > post 7 jumper base>36" > 36" f7-f9 > post 10 jumper 36">72" > 72" f9-f7','72" at post 7'),
      (4,'375 (1151-1525)','rafter 8, ring end','U8 dn > floor hop f8 > U9 up > ring hop > U10 dn > post 10 jumper base>36" > 36" f10-f12 > post 1 jumper 36">72" > 72" f12-f10','72" at post 10')]
import textwrap
for i,(p,n,s,path,e) in enumerate(rows):
    y=77-i*16.5
    ax.add_patch(Rectangle((0.8,y-6),4.5,12,fc=C[p],ec='none'));ax.text(3.05,y,f'P{p}',color='white',ha='center',va='center',fontsize=18,fontweight='bold')
    ax.text(9,y,n,fontsize=16,va='center');ax.text(21,y,textwrap.fill(s,18),fontsize=14.5,va='center')
    ax.text(35,y,textwrap.fill(path,92),fontsize=13.5,va='center',linespacing=1.15);ax.text(88,y,e,fontsize=15,va='center')
ax.plot([0,100],[11,11],color='#aaa',lw=1.5)
ax.text(0.8,5,'Key:  S = start (K4-PB lead at the ring)   E = end of chain   solid arrows = pixel strings (post, rafter, rails)   dotted arrows = floor hops, ring hops and post jumpers (data + GND only)   72" = solid line, 36" = dashed (plan)   U# dn/up = unit data direction',fontsize=13,va='center',color='#333')
os.makedirs('docs',exist_ok=True) if os.path.basename(os.getcwd())=='gazebo-xlights-repo' else None
out='docs/k4_ports_diagram.png' if os.path.basename(os.getcwd())=='gazebo-xlights-repo' else 'k4_ports_diagram.png'
plt.savefig(out,dpi=100,facecolor='white');print(out)
