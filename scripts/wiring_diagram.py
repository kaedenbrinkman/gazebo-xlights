import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle, FancyArrowPatch
PC={1:'#1f77b4',2:'#2ca02c',3:'#ff7f0e',4:'#d62728',5:'#9467bd',6:'#17becf'}
BG='#fbfbf8'
fig=plt.figure(figsize=(24,16),dpi=100,facecolor=BG)
def panel(rect,title):
    ax=fig.add_axes(rect,facecolor='white');ax.set_title(title,fontsize=15,fontweight='bold',loc='left')
    for s in ax.spines.values():s.set_color('#999')
    return ax
def arrow(ax,a,b,c='k',lw=2,ms=18):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=ms,color=c,lw=lw,zorder=6))
def bolt(ax,x,y,s=1.0,c='#e6b800'):
    ax.add_patch(Polygon([[x+.2*s,y+1.2*s],[x-.5*s,y-.1*s],[x-.05*s,y-.1*s],[x-.3*s,y-1.2*s],[x+.5*s,y+.2*s],[x+.05*s,y+.2*s]],fc=c,ec='k',lw=1,zorder=8))
fig.suptitle('Gazebo pixel wiring: Kulp K16A-B, 12-sided gazebo (1,525 px, 48 strings, pixels face inward)',fontsize=24,fontweight='bold',y=0.985)

# ---------- plan ----------
ax=panel([0.015,0.505,0.30,0.445],'1. Top-down plan (posts #1-#12 CCW from entrance)')
ax.set_aspect('equal');ax.set_xlim(-135,135);ax.set_ylim(-150,150);ax.axis('off')
R=97.75;ang=np.radians(-105+30*np.arange(12));P=np.c_[R*np.cos(ang),R*np.sin(ang)]
ax.add_patch(Polygon(P,fill=False,ec='#555',lw=3))
ax.add_patch(Polygon(np.c_[15.27*np.cos(ang),15.27*np.sin(ang)],fc='#ddd',ec='k',lw=1.5,zorder=3))
ax.text(0,0,'ring\n1x50',ha='center',va='center',fontsize=11,color=PC[4],fontweight='bold',zorder=5)
for k in range(12):
    port=1+k//4
    ax.plot([P[k][0],15.27*np.cos(ang[k])],[P[k][1],15.27*np.sin(ang[k])],color=PC[port],lw=4,alpha=.85,zorder=2)
    ax.add_patch(Rectangle((P[k][0]-4,P[k][1]-4),8,8,fc=PC[port],ec='k',zorder=5))
    r=np.array([np.cos(ang[k]),np.sin(ang[k])])
    ax.text(*(r*113),f'#{k+1}',ha='center',va='center',fontsize=16,fontweight='bold',color=PC[port])
    ax.text(*(r*60),f'P{port}',ha='center',va='center',fontsize=10,color=PC[port],rotation=np.degrees(ang[k])%180-(90 if False else 0))
# entrance
ax.plot([P[0][0],P[1][0]],[P[0][1],P[1][1]],color='red',lw=7,solid_capstyle='butt',zorder=4)
ax.text(0,-112,'ENTRANCE FACE (between #1 and #2)\nno 36" rail, no lower braces',ha='center',va='top',fontsize=12,color='red',fontweight='bold')
ax.annotate('',xy=(P[1][0]+14,P[1][1]+16),xytext=(P[0][0]-14,P[0][1]+18),arrowprops=dict(arrowstyle='->',color='gray',lw=2,connectionstyle='arc3,rad=-0.0'))
ax.text(0,-70,'numbering CCW',ha='center',fontsize=11,color='gray')
ax.text(-132,148,'Ports: P1 = posts 1-4 (blue)\nP2 = posts 5-8 (green)\nP3 = posts 9-12 (orange)\nEach post+rafter pair = 75 px',fontsize=11.5,va='top',bbox=dict(fc='white',ec='#aaa'))
ax.text(132,148,'192" inside post-to-post\nside 50.6", R = 97.75"',fontsize=11,ha='right',va='top',color='#444')

# ---------- elevation of one post + rafter ----------
ax=panel([0.335,0.505,0.325,0.445],'2. Side view: one post + rafter')
ax.set_xlim(-8,112);ax.set_ylim(-28,112);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
ax.plot([-6,108],[0,0],color='#6b4f2a',lw=6)
ax.add_patch(Rectangle((97.75-1.75,0),3.5,71,fc='#deb887',ec='k'))
ax.add_patch(Rectangle((97.75-1.75,71),3.5,1.5,fc='#c9a26b',ec='k'))
ax.plot([97.75,15.27],[72.5,89],color='#a0522d',lw=7,solid_capstyle='butt',zorder=1)
ax.add_patch(Rectangle((11.65,89),3.62,3.5,fc='#8b4513',ec='k'))
ax.plot([0,0],[0,100],'--',color='gray',lw=1);ax.text(0,104,'gazebo centre line',ha='center',fontsize=11,color='gray')
# pixels (inward side)
xp=97.75-1.9
c1='#1f77b4';c2='#5fb3f0'
zs=1+2*np.arange(35)
ax.scatter([xp]*35,zs,s=40,c=c1,zorder=7,edgecolors='k',linewidths=.4)
t=np.array([97.75,72.5])-np.array([97.75,72.5]);d=np.array([15.27-97.75,16.5]);L=np.linalg.norm(d);d/=L;nrm=np.array([-d[1],d[0]])  # normal pointing... down/in
nrm=-nrm if nrm[1]>0 else nrm
pts=[np.array([97.75,72.5])+d*(4+2*i)+nrm*3.2 for i in range(40)]
pts=np.array(pts)
ax.scatter(pts[:15,0],pts[:15,1],s=40,c=c1,zorder=7,edgecolors='k',linewidths=.4)
ax.scatter(pts[15:,0],pts[15:,1],s=40,c=c2,zorder=7,edgecolors='k',linewidths=.4)
# data arrows
arrow(ax,(xp-8,-8),(xp-8,30),c1,3);arrow(ax,tuple(pts[2]+[0,-9]),tuple(pts[12]+[-6,-8]),c1,3)
ax.text(xp-11,12,'data +\npower in',ha='right',va='center',fontsize=11,color=c1,fontweight='bold',rotation=0)
ax.text(104,35,'POST 71"\n35 px\n(1" to 69")',fontsize=12,va='center',ha='left',color=c1,fontweight='bold')
ax.text(60,98,'RAFTER ~84" (2x4), ~40 px\n(first 15 px on the 50-px string,\nthen the 25-px string to the ring)',fontsize=11.5,ha='center',va='bottom',color='#444')
ax.text(18,95,'ring base 89"',fontsize=10.5,ha='left',color='#8b4513')
ax.text(104,72.5,'wall top 72.5"',fontsize=10.5,ha='left',va='bottom')
# injection
bolt(ax,xp-8,-14,2.3);ax.text(xp-14,-14,'inject @ port start',fontsize=11,ha='right',va='center')
j=pts[14]+[0,0];bolt(ax,j[0]+4,j[1]-14,2.3);ax.annotate('',xy=j+[0,-3],xytext=(j[0]+4,j[1]-12),arrowprops=dict(arrowstyle='-',color='gray'))
ax.text(j[0]+4,j[1]-22,'mid-chain injection at\n50 -> 25 string joint',fontsize=11,ha='center',va='top')
# string brackets
ax.text(100,19,'',fontsize=1)
ax.text(5,-12,'STRING A: 50 px = 35 on post + 15 on rafter  (dark blue)\nSTRING B: 25 px on rafter (light blue)\n= 75 px per post/rafter pair',fontsize=12,ha='left',va='center',bbox=dict(fc='#f2f7fc',ec=c1))
ax.text(5,-23,'note: 75 per unit = 35 post + 40 rafter (older model had 76)',fontsize=10.5,ha='left',va='center',color='#a00')
ax.set_ylim(-28,112)

# ---------- mounting strip ----------
ax=panel([0.675,0.505,0.31,0.445],'3. 2" mounting strip (inward side)')
ax.set_xlim(0,100);ax.set_ylim(-16,100);ax.axis('off')
# front view
ax.text(3,95,'Front view (from inside)',fontsize=12.5,fontweight='bold')
ax.add_patch(Rectangle((8,12),14,76,fc='#deb887',ec='k',lw=1.5));ax.text(15,8,'post\n(1.5x3.5")',ha='center',va='top',fontsize=10.5)
ax.add_patch(Rectangle((12,14),6,72,fc='#9aa7b2',ec='k',lw=1.2));ax.text(15,90,'strip',ha='center',fontsize=10.5)
for i in range(11):
    y=18+i*6.4;ax.add_patch(Circle((15,y),1.6,fc='white',ec='k',lw=1));ax.add_patch(Circle((15,y),0.9,fc=PC[1],ec='none'))
ax.annotate('',xy=(27,18+6.4),xytext=(27,18));ax.annotate('',xy=(27,18),xytext=(27,18+6.4),arrowprops=dict(arrowstyle='<->',lw=1.5))
ax.text(29,18+3.2,'2" pitch',fontsize=11,va='center')
# cross-section
ax.text(48,95,'Plan cross-section',fontsize=12.5,fontweight='bold')
ax.add_patch(Rectangle((52,40),10,22,fc='#deb887',ec='k',lw=1.5));ax.text(57,36,'wood\npost',ha='center',va='top',fontsize=10.5)
ax.add_patch(Rectangle((62,42),3,18,fc='#9aa7b2',ec='k',lw=1.2));ax.text(63.5,64,'strip',ha='center',fontsize=10.5)
for y in (46,51,56):
    ax.add_patch(Circle((70,y),2.3,fc=PC[1],ec='k',lw=1,zorder=5));ax.plot([65,68],[y,y],color='k',lw=1)
    ax.plot([57,52],[y,y-12],color='#555',lw=1,ls=':')
ax.text(75,51,'bullet pixels plug into\nthe strip holes, bulbs\nface the gazebo interior',fontsize=11,va='center')
ax.annotate('',xy=(95,25),xytext=(70,25),arrowprops=dict(arrowstyle='->',lw=2,color='k'));ax.text(70,21,'inside of gazebo ->',fontsize=11)
ax.text(52,72,'wires run behind the strip,\nin the gap to the wood',fontsize=10.5,va='bottom',color='#555')
ax.text(3,-15,'Strip stock (assumed): flat bar / PVC / wood, holes drilled to fit your pixels, 2" centres.\nPixel strings stay as regular daisy-chains; the strip only holds the pitch.\nSame strip on rails, joists and rafters (centreline, inner side).',fontsize=11,va='bottom')

# ---------- unrolled ----------
ax=panel([0.015,0.255,0.97,0.225],'4. Unrolled wall (12 faces, CCW; strings run left to right): 36" and 72" rails')
ax.set_xlim(-1.9,13.2);ax.set_ylim(-0.9,4.3);ax.axis('off')
y72,y36=2.7,1.3
for k in range(13):
    ax.plot([k,k],[0,3.55],color='#deb887',lw=7,solid_capstyle='butt');ax.text(k,-0.15,f'#{k%12+1}',ha='center',va='top',fontsize=13,fontweight='bold')
ax.text(12.15,1.7,'(= #1\nagain)',fontsize=10,va='center',color='gray')
for f in range(12):
    x0,x1=f+0.04,f+0.96
    def dots(y,col,n=25):
        xs=np.linspace(x0+.06,x1-.06,n);ax.scatter(xs,[y]*n,s=11,c=col,zorder=5)
        ax.plot([x0,x1],[y,y],color=col,lw=2.4,alpha=.4)
    dots(y72,PC[5])
    if f==0:
        ax.plot([x0,x1],[y36,y36],color='red',lw=2,ls='--');ax.text(.5,y36-0.28,'no 36" rail',ha='center',fontsize=10,color='red')
        ax.text(.5,2.05,'ENTRANCE',ha='center',fontsize=11,color='red',fontweight='bold')
    else:dots(y36,PC[4])
    ax.text(f+.5,y72+.27,'25',ha='center',fontsize=9)
    if f:ax.text(f+.5,y36+.27,'25',ha='center',fontsize=9)
ax.text(-1.85,y72,'72" rails\nport 5 (12x25 = 300)',fontsize=11,color=PC[5],va='center',ha='left',fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.8))
ax.text(-1.85,y36-0.5,'36" rails\nport 4 (11x25 = 275,\nthen ring 50)',fontsize=11,color=PC[4],va='top',ha='left',fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.8))
for y,c in((y72+.55,PC[5]),(y36+.55,PC[4])):arrow(ax,(4.0,y),(6.5,y),c,2.5)
ax.text(8.2,y72+.85,'<- data direction (chain continues face to face)',ha='left',va='center',fontsize=9.5,color='#444')
ax.text(2.3,-.62,'One 25-px string per face: 25 px at 2" pitch = 48" span between posts. Port 4 jumpers from face 12 on to the ring (50 px).',fontsize=10.5,ha='left',va='center')
bolt(ax,0.0,4.0,0.3)
ax.text(0.4,4.0,'inject at start of ports 4 and 5 (first face of each chain) and again mid-chain (face 6/7)',fontsize=10.5,va='center')

# ---------- controller ----------
ax=panel([0.015,0.015,0.60,0.225],'5. Controller and port assignments (Kulp K16A-B, ports 1-5 used)')
ax.set_xlim(0,120);ax.set_ylim(-2,40);ax.axis('off')
ax.add_patch(FancyBboxPatch((1,19),18,16,boxstyle='round,pad=0.4',fc='#eef',ec='k',lw=2))
ax.text(10,27,'Kulp\nK16A-B\n(FPP)',ha='center',va='center',fontsize=15,fontweight='bold')
ax.text(10,17.5,'E1.31 / ethernet\nfrom xLights/FPP',ha='center',va='top',fontsize=10.5)
rows=[(1,'Units 1-4 (posts 1-4 + rafters): 4 x (50 + 25) = 300 px',300),(2,'Units 5-8 (posts 5-8 + rafters): 4 x (50 + 25) = 300 px',300),(3,'Units 9-12 (posts 9-12 + rafters): 4 x (50 + 25) = 300 px',300),
      (4,'36" rails 11 x 25 = 275 (faces 2-12), then ring 1 x 50 = 325 px',325),(5,'72" rails 12 x 25 = 300 px',300)]
for i,(p,txt,n) in enumerate(rows):
    y=35-i*5.6
    ax.add_patch(Rectangle((19,y-1.7),4,3.4,fc=PC[p],ec='k'));ax.text(21,y,f'{p}',color='white',ha='center',va='center',fontsize=11,fontweight='bold')
    arrow(ax,(23.5,y),(27.5,y),PC[p],2.5,16)
    bar=n/325*34
    ax.add_patch(Rectangle((31,y-1.5),bar,3,fc=PC[p],alpha=.35,ec=PC[p]))
    bolt(ax,28.9,y+0.1,0.6)
    ax.text(33,y,f'Port {p}',fontsize=11,va='center',fontweight='bold',color='k')
    ax.text(68,y,txt,fontsize=11.5,va='center')
ax.text(28,38.6,'power inject at port start',fontsize=10,va='bottom',color='#444')
ax.text(1,6.2,'Power (assumed 5 V, check your pixels): inject at the start of every port and at the 50->25 joint of each post/rafter pair.\n12 V pixels need far less injection. Share ground with the controller.',fontsize=10.5,va='center',color='#333')
ax.text(1,1.2,'Each port chain = strings in order, e.g. port 1: post1 A(50) -> post1 B(25) -> post2 A -> post2 B -> ... -> post4 B.',fontsize=10.5,va='center',color='#333')

# ---------- table ----------
ax=panel([0.63,0.015,0.355,0.225],'6. Pixel counts')
ax.axis('off');ax.set_xlim(0,100);ax.set_ylim(0,100)
hdr=['Port','Strings','Pixels']
data=[('1','4x50 + 4x25 (units 1-4)',300),('2','4x50 + 4x25 (units 5-8)',300),('3','4x50 + 4x25 (units 9-12)',300),('4','11x25 (36" rails) + 1x50 (ring)',325),('5','12x25 (72" rails)',300)]
for x,h in zip((4,18,88),hdr):ax.text(x,92,h,fontsize=13,fontweight='bold',va='center')
ax.plot([2,98],[86,86],color='k')
for i,(p,s,n) in enumerate(data):
    y=79-i*10.5
    ax.add_patch(Rectangle((2,y-3.2),12,6.4,fc=PC[int(p)],ec='none',alpha=.8));ax.text(8,y,p,ha='center',va='center',fontsize=12,color='white',fontweight='bold')
    ax.text(18,y,s,fontsize=12,va='center');ax.text(96,y,str(n),fontsize=12,va='center',ha='right')
ax.plot([2,98],[24,24],color='k')
tot=sum(d[2] for d in data)
ax.text(4,17,f'Total: {tot} px in 48 strings (24 + 11 + 12 + 1)',fontsize=12.5,fontweight='bold',va='center')
ax.text(4,8,'Top joists carry no pixels (they duplicate the 72" rails). 12x75 + 275 + 300 + 50 = 1,525.',fontsize=10.5,color='#333',va='center')
import os;os.makedirs('docs',exist_ok=True);plt.savefig('docs/wiring_diagram.png',dpi=100,facecolor=BG)
print(tot)
