import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import g5
# ---------------------------------------------------------------------------
# Node order = wiring order for Layout F v3 (Kulp K4-PB, 4 ports, controller in the ring box).
# Units/faces are numbered as in the docs: unit k = rafter k + post k; face k = post k -> post k+1.
#   ('ring',)          center ring, 50 px, entered at rafter 11's corner, running CCW once round
#   ('U',k,'up'|'dn')  up = post base->top then rafter wall->ring; dn = rafter ring->wall then post top->base
#   ('R72'|'R36',f,'f'|'r')  rail face f, forward = post f -> post f+1, reverse = post f+1 -> post f
PORTS=[
 ('P1',[('ring',),('U',11,'dn'),('U',12,'up'),('U',1,'dn'),('R72',1,'f'),('R72',2,'f'),('R72',3,'f'),('R36',3,'r'),('R36',2,'r')]),
 ('P2',[('U',2,'dn'),('U',3,'up'),('U',4,'dn'),('R36',4,'f'),('R36',5,'f'),('R36',6,'f'),('R72',6,'r'),('R72',5,'r'),('R72',4,'r')]),
 ('P3',[('U',5,'dn'),('U',6,'up'),('U',7,'dn'),('R36',7,'f'),('R36',8,'f'),('R36',9,'f'),('R72',9,'r'),('R72',8,'r'),('R72',7,'r')]),
 ('P4',[('U',8,'dn'),('U',9,'up'),('U',10,'dn'),('R36',10,'f'),('R36',11,'f'),('R36',12,'f'),('R72',12,'r'),('R72',11,'r'),('R72',10,'r')]),
]
RING_START=int(np.ceil(10/12*50))      # first ring pixel past corner 10 (rafter 11), CCW
_idx={}
for _k,(_m,_i) in enumerate(g5.LAB): _idx.setdefault((_m,_i),[]).append(_k)   # geometric order within each member
def _seg(s):
    if s[0]=='ring': r=_idx[('ring',0)]; return r[RING_START:]+r[:RING_START]
    if s[0]=='U':
        p,r=_idx[('posts',s[1]-1)],_idx[('rafters',s[1]-1)]
        return p+r if s[2]=='up' else r[::-1]+p[::-1]
    l=_idx[({'R72':'rails72','R36':'rails36'}[s[0]],s[1]-1)]
    return l if s[2]=='f' else l[::-1]
order=[];PORT_RANGES=[]
for _name,_segs in PORTS:
    a=len(order)
    for s in _segs: order+=_seg(s)
    PORT_RANGES.append((_name,a+1,len(order)))
assert sorted(order)==list(range(len(g5.pix))),'node order must cover every pixel exactly once'
order=np.array(order)
XYZ=g5.pix[order].astype(float)           # inches, origin = gazebo centre on ground
MEM=[g5.LAB[k][0] for k in order]; MIDX=np.array([g5.LAB[k][1] for k in order])
MEMARR=np.array(MEM)
N=len(XYZ)
# LOC/U = geometric position within each member (posts bottom->top, rafters wall->ring, rails post i->i+1, ring CCW
# from post 1), independent of wiring direction, so animations look the same whichever way a unit is wired.
_geo={}
for _l in _idx.values():
    for j,k in enumerate(_l): _geo[k]=(j,j/max(len(_l)-1,1))
LOC=np.array([_geo[k][0] for k in order]);U=np.array([_geo[k][1] for k in order])
ANG=np.arctan2(XYZ[:,1],XYZ[:,0]);RAD=np.hypot(XYZ[:,0],XYZ[:,1]);Z=XYZ[:,2]
def hsv(h,s,v):
    sh=np.broadcast(np.asarray(h),np.asarray(s),np.asarray(v)).shape
    h=np.broadcast_to(np.asarray(h,float)%1.0,sh);s=np.broadcast_to(s,sh);v=np.broadcast_to(v,sh)
    i=(h*6).astype(int)%6;f=h*6-np.floor(h*6)
    p=v*(1-s);q=v*(1-f*s);t=v*(1-(1-f)*s)
    r=np.choose(i,[v,q,p,p,t,v]);g=np.choose(i,[t,v,v,q,p,p]);b=np.choose(i,[p,p,t,v,v,q])
    return np.stack([r,g,b],-1)
