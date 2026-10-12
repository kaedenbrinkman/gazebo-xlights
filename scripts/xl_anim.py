from xl_common import *
import struct,xml.etree.ElementTree as ET
ET.parse('model/gazebo.xmodel')
FPS=20;NF=200;rng=np.random.default_rng(7)
IS=lambda m:(MEMARR==m)
def anim_rainbow(t):
    h=ANG/(2*np.pi)-0.3*t+0.25*Z/90
    return hsv(h,1,1)
def anim_spiral(t):
    c=np.zeros((N,3))+hsv(np.full(N,0.62),1,0.06)
    m=IS('rafters');head=(0.55*t+MIDX/12)%1;d=(head-U)%1
    v=np.exp(-d*7);c[m]=hsv(MIDX/12+0.08*t,1,v)[m]
    m=IS('ring');head=((ANG/(2*np.pi))-0.55*t)%1;v=np.exp(-head*5);c[m]=hsv(0.9+0.1*t,0.4,v)[m]+0.05
    m=IS('rails72');c[m]=hsv(MIDX/12+0.08*t,1,0.25+0.2*np.sin(2*np.pi*t*0.55))[m]
    return c
def anim_wipe(t):
    per=2.5;k=int(t//per);ph=(t%per)/per;front=ph*100
    cur=hsv(np.full(N,(0.13*k)%1),1,1);prev=hsv(np.full(N,(0.13*(k-1))%1),1,1)
    a=np.clip((front-Z)/4+0.5,0,1)[:,None]
    return cur*a+prev*(1-a)
tw_p=rng.uniform(0.8,2.4,N);tw_f=rng.uniform(0,1,N);tw_c=rng.choice([0.0,0.58,0.1,0.62],N)
def anim_twinkle(t):
    v=np.clip(np.sin(2*np.pi*(t/tw_p+tw_f)),0,1)**10
    s=np.where(tw_c<0.05,0.0,0.5)
    return hsv(tw_c,s,v*1.0)+hsv(np.full(N,0.62),1,0.03)
def anim_breath(t):
    ph={'posts':0,'rails36':0.5,'rails72':1.0,'rafters':2.0,'ring':2.5}
    hb={'posts':0.08,'rails36':0.55,'rails72':0.85,'rafters':0.3,'ring':0.0}
    p=np.array([ph[m] for m in MEM]);hh=np.array([hb[m] for m in MEM])
    v=0.5+0.5*np.sin(2*np.pi*0.3*t-p)
    s=np.where(MEMARR=='ring',0.0,1.0)
    return hsv(hh+0.05*t,s,v**1.5)
# fire (Fire2012 per post column; other members as embers)
def make_fire():
    fr=np.zeros((NF,N,3));heat=np.zeros((12,35));r=np.random.default_rng(3)
    # heat[k][0] is the BASE of post k: order each post's nodes by physical height, not node order
    # ("dn" units are wired top->base, so node order is upside down on every other unit)
    posts=[by_height(np.where((MEMARR=='posts')&(MIDX==k))[0]) for k in range(12)]
    for f in range(NF):
        heat=np.clip(heat-r.uniform(0,0.12,heat.shape)*1.0,0,1)   # cooling
        new=heat.copy()
        new[:,2:]=(heat[:,1:-1]+heat[:,0:-2]+heat[:,0:-2])/3
        heat=new
        sp=r.random(12)<0.5;heat[sp,r.integers(0,4,sp.sum())]+=r.uniform(0.5,1.0,sp.sum());heat=np.clip(heat,0,1)
        for k in range(12):
            hv=heat[k];col=np.stack([np.clip(hv*3,0,1),np.clip(hv*3-1,0,1),np.clip(hv*3-2,0,1)],-1)
            fr[f,posts[k]]=col
        emb=0.15+0.1*np.sin(f/3.0+MIDX)+r.uniform(0,0.08,N)
        o=np.where(MEMARR!='posts')[0]
        fr[f,o]=np.stack([emb[o]*1.0,emb[o]*0.25,emb[o]*0.0],-1)
        rr=np.where(MEMARR=='ring')[0];fr[f,rr]=np.stack([np.full(len(rr),0.8),np.full(len(rr),0.4),np.full(len(rr),0.05)],-1)*(0.7+0.3*r.random(len(rr)))[:,None]
    return fr
FIRE=make_fire()
def anim_xmas(t):
    par=(LOC+int(t*2))%2
    c=np.where(par[:,None]==0,[1.0,0,0],[0,0.8,0]).astype(float)
    spark=(np.sin(2*np.pi*(t*1.7+tw_f*7))>0.985)[:,None]
    return np.where(spark,1.0,c)
ANIMS={'rainbow_chase':anim_rainbow,'rafter_spiral':anim_spiral,'wipe_up':anim_wipe,'twinkle':anim_twinkle,'breathing':anim_breath,'fire':None,'christmas':anim_xmas}
def frames(name):
    if name=='fire': return FIRE
    fn=ANIMS[name];return np.stack([fn(f/FPS) for f in range(NF)])
def write_fseq(path,fr):
    fr8=np.clip(np.round(fr*255),0,255).astype(np.uint8).reshape(len(fr),-1)
    ch=fr8.shape[1]
    hdr=struct.pack('<4sHBBHIIBBBBBB8s',b'PSEQ',32,0,2,32,ch,len(fr8),1000//FPS,0,0,0,0,0,b'gazebo01')
    assert len(hdr)==32,len(hdr)
    open(path,'wb').write(hdr+fr8.tobytes())
if __name__=='__main__':
    allf=[]
    for n in ANIMS:
        fr=frames(n);np.save(f'build/anim_{n}.npy',fr.astype(np.float32));write_fseq(f'sequences/{n}.fseq',fr);allf.append(fr);print(n,fr.shape)
    write_fseq('sequences/gazebo_all.fseq',np.concatenate(allf))
