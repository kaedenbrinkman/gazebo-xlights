import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import g5
RANK={'posts':0,'rails36':1,'rails72':2,'rafters':3,'ring':4}
def _key(k):
    m,i=g5.LAB[k]   # wiring order: unit k = post k then rafter k (ports 1-3), 36" rails + ring (port 4), 72" rails (port 5)
    return {'posts':(0,i,0,k),'rafters':(0,i,1,k),'rails36':(1,i,0,k),'ring':(1,99,0,k),'rails72':(2,i,0,k)}[m]
order=sorted(range(len(g5.pix)),key=_key)
XYZ=g5.pix[order].astype(float)           # inches, origin = gazebo centre on ground
MEM=[g5.LAB[k][0] for k in order]; MIDX=np.array([g5.LAB[k][1] for k in order])
MEMARR=np.array(MEM)
N=len(XYZ)
# local index within each (member,idx) and its fraction u
LOC=np.zeros(N,int);U=np.zeros(N)
keys={}
for n,(m,i) in enumerate(zip(MEM,MIDX)): keys.setdefault((m,i),[]).append(n)
for k,l in keys.items():
    for j,n in enumerate(l): LOC[n]=j;U[n]=j/max(len(l)-1,1)
ANG=np.arctan2(XYZ[:,1],XYZ[:,0]);RAD=np.hypot(XYZ[:,0],XYZ[:,1]);Z=XYZ[:,2]
def hsv(h,s,v):
    sh=np.broadcast(np.asarray(h),np.asarray(s),np.asarray(v)).shape
    h=np.broadcast_to(np.asarray(h,float)%1.0,sh);s=np.broadcast_to(s,sh);v=np.broadcast_to(v,sh)
    i=(h*6).astype(int)%6;f=h*6-np.floor(h*6)
    p=v*(1-s);q=v*(1-f*s);t=v*(1-(1-f)*s)
    r=np.choose(i,[v,q,p,p,t,v]);g=np.choose(i,[t,v,v,q,p,p]);b=np.choose(i,[p,p,t,v,v,q])
    return np.stack([r,g,b],-1)
