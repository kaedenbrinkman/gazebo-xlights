from xl_common import *
from xl_anim import write_fseq
FPS=20;NF=400;T=20.0
rng=np.random.default_rng(11)
W2=2*np.pi/T
IS=lambda m:(MEMARR==m)
K=lambda lo,hi:rng.integers(lo,hi+1,N)
PH=lambda:rng.uniform(0,2*np.pi,N)
def rgb(r,g,b):return np.array([r,g,b])/255.0
# 1 candlelight
c_k=[K(7,25) for _ in range(3)];c_p=[PH() for _ in range(3)]
def candle(t):
    f=sum(np.sin(W2*k*t+p) for k,p in zip(c_k,c_p))/3
    v=0.5+0.5*f; base=np.where(IS('posts'),0.40,np.where(IS('ring'),0.22,0.24))
    v=base*(0.55+0.45*v)
    return v[:,None]*rgb(255,147,41)
# 2 starry night
s_k=rng.choice([2,3,4,5],N);s_p=PH();s_c=rng.random(N)
SHOOT=[(3.0,2),(9.5,7),(15.0,10)]  # start time, rafter index
def starry(t):
    tw=(0.5+0.5*np.sin(W2*s_k*t+s_p))**14*0.85
    base=np.broadcast_to(np.array([0.0,0.02,0.12]),(N,3)).copy()
    col=np.where(s_c[:,None]<0.5,rgb(255,255,255),rgb(170,200,255))
    c=base+tw[:,None]*col
    for t0,ri in SHOOT:
        head=(t-t0)/1.6
        if 0<=head<=1.5:
            m=IS('rafters')&(MIDX==ri);d=head-U
            v=np.where((d>=0)&(d<0.45),np.exp(-d*9),0.0)*np.clip(1.5-head,0,1)
            c[m]+=(v[m,None])*rgb(255,255,255)
            mm=IS('ring');c[mm]+=0.5*np.exp(-((head-1.0)**2)/0.02)*rgb(220,235,255)
    return np.clip(c,0,1)
# 3 slow ember glow
def ember(t):
    h=np.clip(Z/91,0,1)
    v=0.5+0.5*np.sin(2*np.pi*t/10-2*np.pi*0.6*h)
    v=0.08+0.55*v**1.3
    col=rgb(255,185,110)*(1-0.0*h[:,None])
    return v[:,None]*col
# 4 aurora
def aurora(t):
    w1=np.sin(2*ANG+W2*t+Z/28);w2=np.sin(3*ANG-W2*2*t+Z/18);w3=np.sin(ANG+W2*t*1)
    v=np.clip(0.5+0.5*(0.6*w1+0.4*w2),0,1)**1.6
    hu=0.36+0.42*(0.5+0.5*np.sin(2*ANG-W2*t+Z/40))
    return hsv(hu,0.85,0.08+0.85*v)
# 5 golden hour
KEYS=[rgb(255,140,30),rgb(255,80,115),rgb(150,95,215)]
def golden(t):
    p=((t/T)+0.12*np.clip(Z/91,0,1))%1.0*3
    i=np.floor(p).astype(int)%3;f=p-np.floor(p);f=f*f*(3-2*f)
    A=np.array(KEYS)[i];B=np.array(KEYS)[(i+1)%3]
    return (A*(1-f[:,None])+B*f[:,None])*0.55
# 6 eye of sauron
e_k=[K(6,22) for _ in range(3)];e_p=[PH() for _ in range(3)]
RANG=np.radians(-105+30*np.arange(12))
SCANS=[2.0,12.0];SCAN_D=3.0
def eye(t):
    fl=sum(np.sin(W2*k*t+p) for k,p in zip(e_k,e_p))/3;fl=0.5+0.5*fl
    c=np.zeros((N,3))
    # walls: dim red embers pulsing slowly
    wall=~(IS('rafters')|IS('ring'))
    pulse=0.5+0.5*np.sin(2*np.pi*t/10-MIDX*0.4)
    c[wall]=(rgb(255,25,0)*(0.05+0.12*pulse)[:,None])[wall]
    # scan state
    beam=None;scan_a=0.0
    for s0 in SCANS:
        if s0<=t<=s0+SCAN_D:
            ph=(t-s0)/SCAN_D;beam=np.radians(-90)+2*np.pi*ph;scan_a=np.sin(np.pi*ph)
    # rafters: iris flames, bright near ring (u=1), fading outward
    m=IS('rafters')
    v=(0.10+0.90*U**1.4)*(0.55+0.45*fl)
    hue=0.00+0.09*U
    c[m]=hsv(hue,1.0,np.clip(v,0,1))[m]
    # ring: slit pupil
    r=IS('ring')
    slit=np.abs(np.cos(ANG))<0.38
    pup=(0.8+0.2*np.sin(2*np.pi*t/5))
    c[r&slit]=(rgb(255,245,170)*pup)
    c[r&~slit]=(rgb(255,70,0)*(0.6+0.4*fl[r&~slit])[:,None]) if False else rgb(255,70,0)*0.8
    if beam is not None:
        d=np.angle(np.exp(1j*(ANG-beam)))
        b=np.exp(-(d/np.radians(22))**2)*scan_a
        fm=(IS('rafters')|IS('ring')|IS('rails72'))
        add=(b[:,None]*rgb(255,230,150))*fm[:,None]
        c=c+add
        c[r]=np.clip(c[r]+0.2*scan_a,0,1)
    return np.clip(c,0,1)
# 7 lantern fireflies
NFF=16;ff=dict(th=rng.uniform(0,2*np.pi,NFF),k=rng.choice([-2,-1,1,2],NFF),R=rng.uniform(55,100,NFF),
    z0=rng.uniform(40,60,NFF),za=rng.uniform(15,30,NFF),zm=rng.choice([1,2,3],NFF),zp=rng.uniform(0,6.28,NFF),
    bn=rng.choice([3,4,5,6],NFF),bp=rng.uniform(0,6.28,NFF))
def fireflies(t):
    th=ff['th']+W2*ff['k']*t;R=ff['R']+8*np.sin(W2*2*t+ff['zp'])
    pos=np.c_[R*np.cos(th),R*np.sin(th),ff['z0']+ff['za']*np.sin(W2*ff['zm']*t+ff['zp'])]
    b=(0.5+0.5*np.sin(W2*ff['bn']*t+ff['bp']))**3
    d2=((XYZ[:,None,:]-pos[None])**2).sum(-1)
    v=(b[None]*np.exp(-d2/(2*14.0**2))).sum(1)
    v=np.clip(v,0,1)
    return np.clip(0.03*rgb(255,170,60)+v[:,None]*rgb(255,225,70),0,1)
ANIMS={'candlelight_dinner':candle,'starry_night':starry,'slow_ember_glow':ember,'aurora':aurora,'golden_hour':golden,'eye_of_sauron':eye,'lantern_fireflies':fireflies}
if __name__=='__main__':
    allf=[]
    for n,fn in ANIMS.items():
        fr=np.stack([fn(f/FPS) for f in range(NF)]);np.save(f'build/anim_{n}.npy',fr.astype(np.float32))
        write_fseq(f'sequences/{n}.fseq',fr);allf.append(fr);print(n,fr.shape,fr.mean())
    write_fseq('sequences/gazebo_calm.fseq',np.concatenate(allf))
