import os;os.makedirs('renders',exist_ok=True)
import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import g5
from PIL import Image, ImageDraw
W,H,SS=1600,1000,2
G=g5.G;pix=g5.pix;pcol=g5.pcol
wood={'post':(34,25,17),'joist':(30,22,15),'r36':(30,22,15),'r72':(30,22,15),'brace_upper':(26,19,13),'brace_lower':(26,19,13),'rafter':(30,22,15),'ring':(28,20,14)}
polys=[]
for k,v in G.items():
    for q in v:
        q=np.array(q);n=np.cross(q[1]-q[0],q[2]-q[0]);ln=np.linalg.norm(n)
        sh=0.6+0.4*abs((n/ln if ln>0 else n)@np.array([.3,.5,.8]))
        polys.append((q,np.array(wood[k])*sh))
gr=np.array([[x,y,0] for x,y in[(-30000,-30000),(30000,-30000),(30000,30000),(-30000,30000)]])
def clip(pc,zn=1.0):
    out=[]
    for i in range(len(pc)):
        a,b=pc[i],pc[(i+1)%len(pc)];ina,inb=a[2]>=zn,b[2]>=zn
        if ina:out.append(a)
        if ina!=inb:
            t=(zn-a[2])/(b[2]-a[2]);out.append(a+t*(b-a))
    return out
def render(name,cam,tgt,fov,up=(0,0,1)):
    cam=np.array(cam,float);fw=np.array(tgt,float)-cam;fw/=np.linalg.norm(fw)
    r=np.cross(fw,up);r/=np.linalg.norm(r);u=np.cross(r,fw)
    f=(W/2)/np.tan(np.radians(fov)/2)
    def tr(P):
        d=np.atleast_2d(P)-cam;return np.c_[d@r,d@u,d@fw]
    def proj(pc,s=1):
        return [((W/2+f*p[0]/p[2])*s,(H/2-f*p[1]/p[2])*s) for p in pc]
    img=Image.new('RGB',(W*SS,H*SS),(2,3,10));dr=ImageDraw.Draw(img)
    # ground
    pc=clip(list(tr(gr)))
    if len(pc)>2: dr.polygon(proj(pc,SS),fill=(7,8,12))
    items=[]
    for q,c in polys:
        pc=tr(q);
        if pc[:,2].max()<1:continue
        items.append((pc[:,2].mean(),pc,c))
    items.sort(key=lambda x:-x[0])
    for d,pc,c in items:
        pc=clip(list(pc))
        if len(pc)<3:continue
        pts=proj(pc,SS)
        dr.polygon(pts,fill=tuple(int(x) for x in c),outline=(60,46,32))
    base=np.asarray(img.resize((W,H),Image.LANCZOS)).astype(float)/255
    glow=np.zeros((H,W,3))
    pc=tr(pix);m=pc[:,2]>4
    for p,c in zip(pc[m],pcol[m]):
        x=W/2+f*p[0]/p[2];y=H/2-f*p[1]/p[2]
        sc=f/p[2]
        for sig_in,amp in[(0.45,1.6),(1.6,0.45)]:
            s=max(sig_in*sc,0.7);R=int(min(4*s,90))
            x0,x1=int(x)-R,int(x)+R+1;y0,y1=int(y)-R,int(y)+R+1
            if x1<0 or y1<0 or x0>=W or y0>=H:continue
            xs=np.arange(max(x0,0),min(x1,W));ys=np.arange(max(y0,0),min(y1,H))
            if len(xs)==0 or len(ys)==0:continue
            g=np.exp(-(((xs[None,:]-x)**2+(ys[:,None]-y)**2)/(2*s*s)))
            # keep halo brightness bounded for close-up dots
            a=amp*(min(1.0,(1.2*sc*0+ 1))) * (min(1,(8/ max(s,8))**1) if sig_in>1 else 1)
            glow[ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]+=g[:,:,None]*np.array(c)[None,None,:]*a
    lit=1-np.exp(-glow*1.3)
    out=np.clip(base+lit*(1-base*0.5),0,1)
    Image.fromarray((out*255).astype(np.uint8)).save(name)
    print(name)
cx=lambda a,r,z:(r*np.cos(np.radians(a)),r*np.sin(np.radians(a)),z)
render('renders/night_inside_wide.png',(0,70,60),(0,-94,48),105)
render('renders/night_looking_up.png',(0,-10,48),(0,10,95),100)
render('renders/night_entrance.png',(0,-230,66),(0,0,62),80)
render('renders/night_inside_wall.png',cx(30,-5,55),cx(30,94,50),100)
render('renders/night_corner_far.png',(330,-330,190),(0,0,55),45)
