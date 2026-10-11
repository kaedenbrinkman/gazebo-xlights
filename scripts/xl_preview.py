from xl_common import *
from PIL import Image, ImageDraw
import sys
W,H,SS=800,500,2
G=g5.G
wood={'post':(34,25,17),'joist':(30,22,15),'r36':(30,22,15),'r72':(30,22,15),'brace_upper':(26,19,13),'brace_lower':(26,19,13),'rafter':(30,22,15),'ring':(28,20,14)}
polys=[]
for k,v in G.items():
    for q in v:
        q=np.array(q);n=np.cross(q[1]-q[0],q[2]-q[0]);ln=np.linalg.norm(n)
        polys.append((q,np.array(wood[k])*(0.6+0.4*abs((n/ln if ln>0 else n)@np.array([.3,.5,.8])))))
gr=np.array([[x,y,0] for x,y in[(-30000,-30000),(30000,-30000),(30000,30000),(-30000,30000)]])
def clip(pc,zn=1.0):
    out=[]
    for i in range(len(pc)):
        a,b=pc[i],pc[(i+1)%len(pc)];ia,ib=a[2]>=zn,b[2]>=zn
        if ia:out.append(a)
        if ia!=ib:t=(zn-a[2])/(b[2]-a[2]);out.append(a+t*(b-a))
    return out
class Cam:
    def __init__(s,cam,tgt,fov):
        cam=np.array(cam,float);fw=np.array(tgt,float)-cam;fw/=np.linalg.norm(fw)
        r=np.cross(fw,(0,0,1));r/=np.linalg.norm(r);u=np.cross(r,fw);f=(W/2)/np.tan(np.radians(fov)/2)
        tr=lambda P:np.c_[(np.atleast_2d(P)-cam)@r,(np.atleast_2d(P)-cam)@u,(np.atleast_2d(P)-cam)@fw]
        pr=lambda pc,k=1:[((W/2+f*p[0]/p[2])*k,(H/2-f*p[1]/p[2])*k) for p in pc]
        img=Image.new('RGB',(W*SS,H*SS),(2,3,10));dr=ImageDraw.Draw(img)
        pc=clip(list(tr(gr)));dr.polygon(pr(pc,SS),fill=(7,8,12))
        it=[]
        for q,c in polys:
            p=tr(q)
            if p[:,2].max()>=1:it.append((p[:,2].mean(),p,c))
        it.sort(key=lambda x:-x[0])
        for d,p,c in it:
            p=clip(list(p))
            if len(p)>=3:dr.polygon(pr(p,SS),fill=tuple(int(x) for x in c),outline=(60,46,32))
        s.base=np.asarray(img.resize((W,H),Image.LANCZOS)).astype(float)/255
        pc=tr(XYZ);s.sp=[]
        for n,p in enumerate(pc):
            if p[2]<4:continue
            x=W/2+f*p[0]/p[2];y=H/2-f*p[1]/p[2];sc=f/p[2];tot=None
            for sg,amp in[(0.45,1.6),(1.6,0.45)]:
                sd=max(sg*sc,0.7);R=int(min(4*sd,60))
                xs=np.arange(max(int(x)-R,0),min(int(x)+R+1,W));ys=np.arange(max(int(y)-R,0),min(int(y)+R+1,H))
                if len(xs)==0 or len(ys)==0:break
                g=amp*np.exp(-(((xs[None,:]-x)**2+(ys[:,None]-y)**2)/(2*sd*sd)))
                if sg>1:g=g*min(1,8/max(sd,8))
                if tot is None:tot=[ys[0],ys[-1]+1,xs[0],xs[-1]+1,g]
                else:
                    # halo window >= core window: add core into halo
                    a0=tot[0]-ys[0];pass
                    tot=[ys[0],ys[-1]+1,xs[0],xs[-1]+1,g+np.pad(tot[4],((tot[0]-ys[0],ys[-1]+1-tot[1]),(tot[2]-xs[0],xs[-1]+1-tot[3])))] if (tot[0]-ys[0]>=0 and tot[2]-xs[0]>=0 and ys[-1]+1-tot[1]>=0 and xs[-1]+1-tot[3]>=0) else tot
            if tot:s.sp.append((n,tot))
    def render(s,col):
        gl=np.zeros((H,W,3))
        for n,(y0,y1,x0,x1,g) in s.sp: gl[y0:y1,x0:x1]+=g[:,:,None]*col[n][None,None,:]
        lit=1-np.exp(-gl*1.3)
        return (np.clip(s.base+lit*(1-s.base*.5),0,1)*255).astype(np.uint8)
