// Gazebo framing geometry, ported from scripts/g5.py (inches, z up), converted to scene units.
// Scene: metres, Y up. Mapping: scene (X, Y, Z) = (x, z, -y) * 0.0254, so the entrance (-y) faces +Z.
import * as THREE from 'three';

export const IN = 0.0254;
export const toScene = (x, y, z) => new THREE.Vector3(x * IN, z * IN, -y * IN);

const N = 12, INSIDE = 192.0, PD = 3.5;
export const Rc = (INSIDE + PD) / 2;            // 97.75" post-centre circumradius
export const SIDE = 2 * Rc * Math.sin(Math.PI / N);
export const PH = 71.0, JT = 1.5, WT = PH + JT, RING_Z = 89.0, RING_T = 3.5;
const apoIn = 22.5 / 2, apoOut = 29.5 / 2;
const rin = apoIn / Math.cos(Math.PI / N), rout = apoOut / Math.cos(Math.PI / N);
export const ANG = Array.from({ length: N }, (_, i) => THREE.MathUtils.degToRad(-105 + 30 * i));
export const POSTS = ANG.map((a) => [Rc * Math.cos(a), Rc * Math.sin(a)]);

// --- small vector helpers on plain arrays (inches) ---
const sub = (a, b) => a.map((v, i) => v - b[i]);
const add = (a, b) => a.map((v, i) => v + b[i]);
const mul = (a, s) => a.map((v) => v * s);
const norm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); };
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const z3 = (p, z) => [p[0], p[1], z];
const fnorm = (a, b) => norm([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0]);

// box() from g5.py: returns [bottomQuad, topQuad] corner lists (hexahedron)
function box(p0, p1, w, t, nrm) {
  const d = norm(sub(p1, p0)); nrm = norm(nrm); const u = norm(cross(d, nrm));
  const c = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([sa, sb]) => add(add(p0, mul(u, sa * w / 2)), mul(nrm, sb * t / 2)));
  return [c, c.map((x) => add(x, sub(p1, p0)))];
}

/** Members as hexahedra: { post:[[lo4,hi4],...], r36, r72, joist, brace_upper, brace_lower, rafter, ring } */
export function buildMembers() {
  const G = { post: [], joist: [], r36: [], r72: [], brace_upper: [], brace_lower: [], rafter: [], ring: [] };
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N, a = POSTS[i], b = POSTS[j];
    const rad = [Math.cos(ANG[i]), Math.sin(ANG[i]), 0];
    G.post.push(box(z3(a, 0), z3(a, PH), 1.5, PD, rad));
    G.joist.push(box(z3(a, PH + JT / 2), z3(b, PH + JT / 2), 3.5, JT, [0, 0, 1]));
    const fn = fnorm(a, b);
    G.r72.push(box(z3(a, 72), z3(b, 72), 3.5, 0.75, fn));
    if (i !== 0) G.r36.push(box(z3(a, 36), z3(b, 36), 3.5, 0.75, fn));   // entrance face 1-2 has no 36" rail
    const im1 = (i - 1 + N) % N;
    for (const [face, other] of [[i, POSTS[j]], [im1, POSTS[im1]]]) {
      const t = norm(sub(other, a)), fnn = fnorm(a, other);
      for (const [kind, zv, zr] of [['brace_upper', 56.0, 70.25], ['brace_lower', 20.0, 34.25]]) {
        if (kind === 'brace_lower' && face === 0) continue;                 // none on the entrance face
        const c = 3.5 * Math.SQRT2 / 2, ds = zr - zv, ps = 0.75;
        const poly = [[ps, zv + ps - c], [ds + c, zr], [ds - c, zr], [ps, zv + ps + c]];
        const pt = (u, z, s) => add(z3(add(a, mul(t, u)), z), mul(fnn, s * 0.75));
        G[kind].push([poly.map(([u, z]) => pt(u, z, -1)), poly.map(([u, z]) => pt(u, z, 1))]);
      }
    }
    const top = z3(a, WT), pk = z3([rout * Math.cos(ANG[i]), rout * Math.sin(ANG[i])], RING_Z);
    G.rafter.push(box(top, pk, 3.5, 1.5, cross([-Math.sin(ANG[i]), Math.cos(ANG[i]), 0], sub(pk, top))));
  }
  const rp = (r, z) => ANG.map((x) => [r * Math.cos(x), r * Math.sin(x), z]);
  const ob = rp(rout, RING_Z), ib = rp(rin, RING_Z), ot = rp(rout, RING_Z + RING_T), it = rp(rin, RING_Z + RING_T);
  for (let i = 0; i < N; i++) {
    const j = (i + 1) % N;   // one ring segment = hexahedron between corners i and j
    G.ring.push([[ob[i], ob[j], ib[j], ib[i]], [ot[i], ot[j], it[j], it[i]]]);
  }
  return G;
}

/** Merge hexahedra into one BufferGeometry with flat normals and length-aligned UVs (grain along the long axis). */
export function hexaGeometry(list, uvScale = 1 / 30) {
  const pos = [], uv = [];
  const quad = (q) => {
    const P = q.map((p) => toScene(...p));
    const e1 = P[1].distanceTo(P[0]) / IN, e2 = P[3].distanceTo(P[0]) / IN;
    let U = [[0, 0], [e1, 0], [e1, e2], [0, e2]];
    if (e2 > e1) U = [[0, 0], [0, e1], [e2, e1], [e2, 0]];
    for (const k of [0, 1, 2, 0, 2, 3]) { pos.push(P[k].x, P[k].y, P[k].z); uv.push(U[k][0] * uvScale, U[k][1] * uvScale * 3); }
  };
  for (const [lo, hi] of list) {
    quad(lo); quad([...hi].reverse());
    for (let k = 0; k < 4; k++) { const m = (k + 1) % 4; quad([lo[k], lo[m], hi[m], hi[k]]); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.computeVertexNormals();
  return g;
}

/** Inward-facing emission direction per pixel (scene coords), from member name. */
export function pixelNormal(member, x, y) {
  const r = Math.hypot(x, y) || 1;
  const inward = new THREE.Vector3(-x / r, 0, y / r);       // (-x, -y) in scene coordinates
  if (/Rafter/i.test(member)) return inward.multiplyScalar(0.55).add(new THREE.Vector3(0, -0.85, 0)).normalize();
  if (/Ring/i.test(member)) return inward.multiplyScalar(0.35).add(new THREE.Vector3(0, -0.95, 0)).normalize();
  return inward;
}
