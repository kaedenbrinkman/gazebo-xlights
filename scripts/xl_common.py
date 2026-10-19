import numpy as np, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import g5
# ---------------------------------------------------------------------------
# Node order = wiring order. Posts/rafters/faces are numbered as in the docs: posts 1-12 CCW from the entrance,
# face f = post f -> post f+1 (entrance = face 12, posts 12-1, no 36" rail), rafter k sits on post k.
# Segment vocabulary:
#   ('post',k,'up'|'dn')          post k, up = base -> top (35 px)
#   ('raft',k,'up'|'dn')          rafter k, up = wall end -> ring end (40 px)
#   ('U',k,'up'|'dn')             unit k = post k + rafter k (v3): up = base -> ring, dn = ring -> base
#   ('R72'|'R36',f,'f'|'r')       rail face f, forward = post f -> post f+1, reverse = post f+1 -> post f
#   ('ring',corner,'ccw'|'cw')    center ring (50 px), entered at rafter (corner+1)'s ring end
# LAYOUT selects the plan: 'v4' = 4-line plan (docs/physical_layout_v4.md, default), 'v3' = Layout F v3.
import os as _os
LAYOUT=_os.environ.get('GAZEBO_LAYOUT','v4')
PORTS_V3=[
 ('P1',[('ring',10,'ccw'),('U',11,'dn'),('U',12,'up'),('U',1,'dn'),('R72',1,'f'),('R72',2,'f'),('R72',3,'f'),('R36',3,'r'),('R36',2,'r')]),
 ('P2',[('U',2,'dn'),('U',3,'up'),('U',4,'dn'),('R36',4,'f'),('R36',5,'f'),('R36',6,'f'),('R72',6,'r'),('R72',5,'r'),('R72',4,'r')]),
 ('P3',[('U',5,'dn'),('U',6,'up'),('U',7,'dn'),('R36',7,'f'),('R36',8,'f'),('R36',9,'f'),('R72',9,'r'),('R72',8,'r'),('R72',7,'r')]),
 ('P4',[('U',8,'dn'),('U',9,'up'),('U',10,'dn'),('R36',10,'f'),('R36',11,'f'),('R36',12,'f'),('R72',12,'r'),('R72',11,'r'),('R72',10,'r')]),
]
def _w(k): return (k-1)%12+1
def _line_v4(b):
    """Lines 1-3 of the v4 plan, starting at post b: 2 jogs of 2 posts (200 px each)."""
    segs=[]
    for p in (b,b+2):
        segs+=[('post',_w(p),'up'),('R72',_w(p),'f'),('raft',_w(p+1),'up'),('raft',_w(p+2),'dn'),('R72',_w(p+1),'r'),('post',_w(p+1),'dn')]
    return segs
PORTS_V4=[('P1',_line_v4(1)),('P2',_line_v4(5)),('P3',_line_v4(9)),
 # line 4: from mid-height at post 1, CCW (post 1 -> 2 -> ... -> 12) over the 11 36" faces, inject at post 12, then up to the ring at rafter 12
 ('P4',[('R36',f,'f') for f in range(1,12)]+[('ring',11,'ccw')])]
PORTS={'v3':PORTS_V3,'v4':PORTS_V4}[LAYOUT]
_idx={}
for _k,(_m,_i) in enumerate(g5.LAB): _idx.setdefault((_m,_i),[]).append(_k)   # geometric order within each member
def _seg(s):
    if s[0]=='ring':
        r=_idx[('ring',0)]; st=int(np.ceil(s[1]/12*50))%50     # first ring pixel at/after that corner, CCW
        r=r[st:]+r[:st]
        return r if s[2]=='ccw' else [r[0]]+r[1:][::-1]
    if s[0]=='U':
        p,r=_idx[('posts',s[1]-1)],_idx[('rafters',s[1]-1)]
        return p+r if s[2]=='up' else r[::-1]+p[::-1]
    if s[0] in('post','raft'):
        l=_idx[({'post':'posts','raft':'rafters'}[s[0]],s[1]-1)]
        return l if s[2]=='up' else l[::-1]
    l=_idx[({'R72':'rails72','R36':'rails36'}[s[0]],s[1]-1)]
    return l if s[2]=='f' else l[::-1]
def seg_label(s):
    if s[0]=='ring': return 'ring (50) '+s[2].upper()
    if s[0]=='U': return f'U{s[1]} {s[2]}'
    if s[0]=='post': return f'post {s[1]} {s[2]}'
    if s[0]=='raft': return f'rafter {s[1]} {s[2]}'
    a,b=s[1],_w(s[1]+1)
    return f'{s[0][1:]}" f{s[1]} ({a}>{b})' if s[2]=='f' else f'{s[0][1:]}" f{s[1]} ({b}>{a})'
order=[];PORT_RANGES=[]
for _name,_segs in PORTS:
    a=len(order)
    for s in _segs: order+=_seg(s)
    PORT_RANGES.append((_name,a+1,len(order)))
PORT_DESC={_n:', '.join(seg_label(x) for x in _s) for _n,_s in PORTS}
assert sorted(order)==list(range(len(g5.pix))),'node order must cover every pixel exactly once'
order=np.array(order)
XYZ=g5.pix[order].astype(float)           # inches, origin = gazebo centre on ground
MEM=[g5.LAB[k][0] for k in order]; MIDX=np.array([g5.LAB[k][1] for k in order])
MEMARR=np.array(MEM)
N=len(XYZ)
# LOC/U = geometric position within each member (posts bottom->top, rafters wall->ring, rails post i->i+1, ring CCW
# from post 1), independent of wiring direction, so animations look the same whichever way a unit is wired.
# Computed from the physical x/y/z (the same values written to model/gazebo_pixels.csv), never from node order:
#   posts, rafters: by height z; rails: by distance along the face from post f toward post f+1; ring: by angle CCW from post 1.
ANG=np.arctan2(XYZ[:,1],XYZ[:,0]);RAD=np.hypot(XYZ[:,0],XYZ[:,1]);Z=XYZ[:,2]
LOC=np.zeros(N,int);U=np.zeros(N)
for _m in set(MEM):
    for _i in set(MIDX[MEMARR==_m]):
        _sel=np.where((MEMARR==_m)&(MIDX==_i))[0]
        if _m in('posts','rafters'): _key=Z[_sel]
        elif _m in('rails36','rails72'):
            _a,_b=g5.P[_i],g5.P[(_i+1)%12]; _key=(XYZ[_sel,:2]-_a)@((_b-_a)/np.linalg.norm(_b-_a))
        else: _key=(ANG[_sel]-g5.ang[0])%(2*np.pi)
        _r=np.argsort(np.argsort(_key,kind='stable'),kind='stable')
        LOC[_sel]=_r;U[_sel]=_r/max(len(_sel)-1,1)
# sanity: the geometric order g5 generated each member in must agree with the physical ranking
for _l in _idx.values():
    _pos=[int(np.where(order==k)[0][0]) for k in _l]
    assert list(LOC[_pos])==list(range(len(_l))),'LOC must follow physical position'
def by_height(sel):
    """Node indices of a selection sorted bottom-to-top by physical z (wiring-direction independent)."""
    sel=np.asarray(sel);return sel[np.argsort(Z[sel],kind='stable')]
def hsv(h,s,v):
    sh=np.broadcast(np.asarray(h),np.asarray(s),np.asarray(v)).shape
    h=np.broadcast_to(np.asarray(h,float)%1.0,sh);s=np.broadcast_to(s,sh);v=np.broadcast_to(v,sh)
    i=(h*6).astype(int)%6;f=h*6-np.floor(h*6)
    p=v*(1-s);q=v*(1-f*s);t=v*(1-(1-f)*s)
    r=np.choose(i,[v,q,p,p,t,v]);g=np.choose(i,[t,v,v,q,p,p]);b=np.choose(i,[p,p,t,v,v,q])
    return np.stack([r,g,b],-1)
