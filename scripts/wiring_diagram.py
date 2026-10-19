import numpy as np, matplotlib, os
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle, FancyArrowPatch
C={1:'#1f6fb4',2:'#2a9d3f',3:'#ef7d10',4:'#d3302f',5:'#7b4fb5'}
BG='#ffffff'; FS=17
fig=plt.figure(figsize=(24,16),dpi=100,facecolor=BG)
def panel(rect,title,frame=True):
    ax=fig.add_axes(rect,facecolor='#fcfcfa');ax.set_title(title,fontsize=22,fontweight='bold',loc='left',pad=10)
    ax.set_xticks([]);ax.set_yticks([])
    for s in ax.spines.values():s.set_color('#bbb');s.set_visible(frame)
    return ax
def arr(ax,a,b,c='k',lw=3.5,ms=28):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=ms,color=c,lw=lw,zorder=7,shrinkA=0,shrinkB=0))
def bolt(ax,x,y,s=1.0):
    ax.add_patch(Polygon([[x+.25*s,y+1.1*s],[x-.45*s,y-.05*s],[x-.05*s,y-.05*s],[x-.3*s,y-1.1*s],[x+.45*s,y+.15*s],[x+.05*s,y+.15*s]],fc='#f5c400',ec='k',lw=1.5,zorder=9))
fig.text(0.5,0.972,'Gazebo pixel wiring  |  1,525 px in 48 strings  |  12 V pixels  |  Kulp K16A-B',ha='center',fontsize=30,fontweight='bold')

# ===== 1. plan =====
ax=panel([0.02,0.505,0.33,0.43],'1. Plan view (from above)')
ax.set_aspect('equal');ax.set_xlim(-150,150);ax.set_ylim(-150,150)
R=97.75;ang=np.radians(-105+30*np.arange(12));P=np.c_[R*np.cos(ang),R*np.sin(ang)]
ax.add_patch(Polygon(P,fill=False,ec='#444',lw=4,zorder=2))
ax.plot([P[0][0],P[1][0]],[P[0][1],P[1][1]],color='red',lw=10,solid_capstyle='butt',zorder=3)
rin=15.3
for k in range(12):
    port=1+k//4;r=np.array([np.cos(ang[k]),np.sin(ang[k])])
    a=P[k]*0.93;b=r*(rin+12)
    arr(ax,a,b,C[port],4,22)
    ax.add_patch(Rectangle((P[k][0]-6,P[k][1]-6),12,12,fc=C[port],ec='k',lw=1.5,zorder=5))
    ax.text(*(r*(R+19)),f'{k+1}',ha='center',va='center',fontsize=26,fontweight='bold',color=C[port])
ax.add_patch(Polygon(np.c_[rin*np.cos(ang),rin*np.sin(ang)],fc='white',ec=C[4],lw=4,zorder=6))
ax.text(0,0,'ring\n50 px',ha='center',va='center',fontsize=15,fontweight='bold',color=C[4],zorder=8)
ax.text(0,-138,'ENTRANCE (face between 1 and 2)',ha='center',va='center',fontsize=19,color='red',fontweight='bold')
ax.text(-146,142,'Port 1: posts 1-4\nPort 2: posts 5-8\nPort 3: posts 9-12',fontsize=18,va='top',linespacing=1.4,
        bbox=dict(fc='white',ec='#bbb',boxstyle='round,pad=0.4'))
for p,(x,y) in zip((1,2,3),((-139,125),(-139,108),(-139,91))):pass
ax.text(146,142,'posts numbered CCW\nfrom the entrance\narrows: data direction\npost -> rafter -> ring',fontsize=15,va='top',ha='right',color='#555',linespacing=1.4)

# ===== 2. one unit =====
ax=panel([0.37,0.505,0.61,0.43],'2. One post + rafter unit (75 px = string A 50 + string B 25)')
ax.set_xlim(0,100);ax.set_ylim(-14,56)
ax.plot([0,100],[0,0],color='#6b4f2a',lw=8)
ax.add_patch(Rectangle((11,0),2.2,30,fc='#deb887',ec='k',lw=1.5,zorder=1))
ax.plot([12.1,86],[31,45],color='#a0522d',lw=14,solid_capstyle='butt',zorder=1)
ax.add_patch(Rectangle((84,44),8,5,fc='#8b4513',ec='k',zorder=1));ax.text(88,51,'ring',ha='center',fontsize=18,fontweight='bold',color='#8b4513')
cA='#0b3d91';cB='#59b7f2'
zs=np.linspace(0.8,29.2,35);ax.scatter(np.full(35,15.2),zs,s=95,c=cA,edgecolors='k',linewidths=.8,zorder=6)
t=np.linspace(0,1,40);rx=17+t*(82-17);ry=31.3+t*(45.5-31.3)-1.5
ax.scatter(rx[:15],ry[:15],s=95,c=cA,edgecolors='k',linewidths=.8,zorder=6)
ax.scatter(rx[15:],ry[15:],s=95,c=cB,edgecolors='k',linewidths=.8,zorder=6)
# joint
jx,jy=(rx[14]+rx[15])/2,(ry[14]+ry[15])/2
ax.add_patch(Rectangle((jx-.9,jy-1.9),1.8,3.8,fc='k',zorder=8,angle=0))
ax.annotate('connector between\nstring A and string B',xy=(jx,jy-2),xytext=(jx+3,jy-15),fontsize=18,ha='center',va='top',arrowprops=dict(arrowstyle='-|>',lw=2.5,color='k'))
# data in
arr(ax,(6,-9),(6,15),cA,5,34);bolt(ax,6,-11.5,1.6)
ax.text(8,-11,'data + 12 V in\n(port start)',fontsize=18,va='center',color='k',fontweight='bold')
arr(ax,(rx[20]+1,ry[20]-6),(rx[33],ry[33]-6),cB,5,30)
ax.text(19,8,'POST  71"\n35 px, bottom to top',fontsize=20,color=cA,fontweight='bold',va='center')
ax.text(40,48.5,'RAFTER  ~84"  (40 px, wall to ring)',fontsize=20,color='#333',fontweight='bold',va='center',ha='center')
# brackets
ax.text(70,-3,'STRING A  =  50 px   (35 post + first 15 on rafter)',fontsize=19,color=cA,ha='right',va='center',fontweight='bold')
ax.text(70,-8,'STRING B  =  25 px   (rest of rafter)',fontsize=19,color='#2a86c9',ha='right',va='center',fontweight='bold')
ax.text(96,-6,'end of unit: data\nrun on to next post',fontsize=16,ha='right',va='center',color='#555')

# ===== 3. controller / chains / power =====
ax=panel([0.02,0.035,0.62,0.43],'3. Controller, data chains and 12 V power')
ax.set_xlim(0,100);ax.set_ylim(0,54)
ax.add_patch(FancyBboxPatch((1,6),13,40,boxstyle='round,pad=0.3',fc='#e8ecf8',ec='k',lw=3))
ax.text(7.5,26,'Kulp\nK16A-B\n(FPP)',ha='center',va='center',fontsize=22,fontweight='bold')
rows=[(1,['Unit 1','Unit 2',None,'Unit 3','Unit 4'],'300 px'),(2,['Unit 5','Unit 6',None,'Unit 7','Unit 8'],'300 px'),(3,['Unit 9','Unit 10',None,'Unit 11','Unit 12'],'300 px'),
      (4,['36" rails  11 x 25','Ring  50'],'325 px'),(5,['72" rails  12 x 25'],'300 px')]
yy=[43,34.5,26,17.5,9]
for (p,blocks,tot),y in zip(rows,yy):
    ax.add_patch(Rectangle((15.5,y-2.2),4.2,4.4,fc=C[p],ec='k',lw=2,zorder=4));ax.text(17.6,y,str(p),color='white',ha='center',va='center',fontsize=21,fontweight='bold',zorder=5)
    arr(ax,(14.4,y),(15.4,y),'k',2.5,14)
    x=21.5
    if p<=3:
        wid=[10.5,10.5,0,10.5,10.5];gaps=[1.6,3.2,0,1.6,0]
    elif p==4:
        wid=[27,12];gaps=[1.6,0]
    else:
        wid=[27];gaps=[0]
    xs=[]
    for b,w in zip(blocks,wid):
        if b is None: x+=6.0;continue
        ax.add_patch(FancyBboxPatch((x,y-2.4),w,4.8,boxstyle='round,pad=0.1',fc=C[p],ec='k',lw=1.8,alpha=.85))
        ax.text(x+w/2,y,b if p>3 else b+'\n75',ha='center',va='center',fontsize=16 if p<=3 else 17,color='white',fontweight='bold',linespacing=1.0)
        xs.append((x,w));x+=w+1.6
    # arrows between blocks
    for (x0,w0),(x1,_) in zip(xs[:-1],xs[1:]):
        arr(ax,(x0+w0+0.1,y),(x1-0.1,y),'k',3,16)
    ax.text(79,y,tot,fontsize=19,va='center',fontweight='bold',color=C[p])
    # power
    sx=21.5
    ax.plot([sx+0.8,86.5],[y+3.1,y+3.1],color='#c00',lw=3,zorder=3)
    bolt(ax,sx+0.8,y+3.1,0.9)
    if p<=3:
        mx=xs[1][0]+xs[1][1]+3.0;bolt(ax,mx,y+3.1,0.9)
        ax.text(mx+1.3,y+4.9,'mid-chain 12 V (between units 2 and 3)',fontsize=13,va='center')
        ax.text(sx+1.5,y+4.9,'12 V at port start',fontsize=13,va='center')
    else:
        ax.text(sx+1.5,y+4.9,'12 V at port start',fontsize=13,va='center')
ax.text(23,52.3,'12 V injection (bolt) feeds V+ / GND into the pixel line; each port also gets data from the controller',fontsize=14,color='#444',va='center')
ax.text(21.5,2.2,'Units chained base -> ring -> next post base (data jumper). Unit = post + rafter, 75 px.',fontsize=14,color='#444',va='center')
# PSU column
for (p,y),lab in zip(zip((1,2,3,4,5),yy),('12 V 15 A\n+ fuse','12 V 15 A\n+ fuse','12 V 15 A\n+ fuse','12 V 20 A\n+ fuse','12 V 15 A\n+ fuse')):
    ax.add_patch(Rectangle((88,y-2.6),11,5.2,fc='#fff4c2',ec='k',lw=2))
    ax.text(93.5,y,lab,ha='center',va='center',fontsize=14,fontweight='bold',linespacing=1.0)
    ax.plot([88,86.5],[y,y],color='#c00',lw=3);
ax.text(93.5,52.3,'power supplies',fontsize=14,ha='center',color='#444',va='center')

# ===== 4. table =====
ax=panel([0.66,0.035,0.32,0.43],'4. Pixels and current (estimate)')
ax.set_xlim(0,100);ax.set_ylim(0,100)
cols=[(2,'Port'),(14,'Content'),(60,'Pixels'),(78,'Amps')]
for x,h in cols:ax.text(x,93,h,fontsize=19,fontweight='bold',va='center')
ax.plot([1,99],[88,88],color='k',lw=2)
data=[(1,'Units 1-4',300),(2,'Units 5-8',300),(3,'Units 9-12',300),(4,'36" rails + ring',325),(5,'72" rails',300)]
for i,(p,c,n) in enumerate(data):
    y=80-i*12.5
    ax.add_patch(Rectangle((1,y-4.5),9,9,fc=C[p],ec='none'));ax.text(5.5,y,str(p),color='white',ha='center',va='center',fontsize=20,fontweight='bold')
    ax.text(14,y,c,fontsize=18,va='center');ax.text(60,y,str(n),fontsize=18,va='center')
    ax.text(78,y,f'{n*0.04:.0f} A',fontsize=18,va='center')
ax.plot([1,99],[19,19],color='k',lw=2)
tot=sum(d[2] for d in data)
ax.text(14,12,'TOTAL',fontsize=20,fontweight='bold',va='center');ax.text(60,12,f'{tot:,}',fontsize=20,fontweight='bold',va='center');ax.text(78,12,f'{tot*0.04:.0f} A',fontsize=20,fontweight='bold',va='center')
ax.text(2,3,'Estimate: 0.04 A per pixel at full white, 12 V.\nPending the pixel datasheet; typical shows draw far less.',fontsize=14.5,va='center',color='#a00',linespacing=1.3)
os.makedirs('docs',exist_ok=True) if os.path.basename(os.getcwd())=='gazebo-xlights-repo' else None
out='docs/wiring_diagram.png' if os.path.basename(os.getcwd())=='gazebo-xlights-repo' else 'wiring_diagram.png'
plt.savefig(out,dpi=100,facecolor=BG);print(out,tot,tot*0.04)
