// Procedural canvas textures (no image downloads): wood grain, grass, concrete paver.
import * as THREE from 'three';

function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }

function finish(c, repeat, srgb = true, aniso = 8) {
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = aniso;
  return t;
}

// value noise for organic variation
function noise2(seed) {
  const r = rng(seed), P = 64, g = Array.from({ length: P * P }, r);
  const at = (x, y) => g[((y % P + P) % P) * P + ((x % P + P) % P)];
  const sm = (t) => t * t * (3 - 2 * t);
  return (x, y) => {
    const xi = Math.floor(x), yi = Math.floor(y), xf = sm(x - xi), yf = sm(y - yi);
    const a = at(xi, yi), b = at(xi + 1, yi), c = at(xi, yi + 1), d = at(xi + 1, yi + 1);
    return a + (b - a) * xf + (c - a) * yf + (a - b - c + d) * xf * yf;
  };
}

/** Pressure-treated / cedar-ish wood. Grain runs along U. */
export function woodTexture(base = [176, 128, 82], seed = 1) {
  const W = 512, H = 128, [c, x] = canvas(W, H), r = rng(seed), n = noise2(seed + 7);
  const img = x.createImageData(W, H);
  for (let j = 0; j < H; j++)
    for (let i = 0; i < W; i++) {
      const warp = n(i / 90, j / 18) * 6;
      const ring = Math.sin((j + warp * 3) * 0.55 + n(i / 200, j / 40) * 8);
      const fine = n(i / 3, j * 1.5) * 0.5;
      let v = 0.82 + 0.1 * ring + 0.12 * (fine - 0.25) + 0.08 * (n(i / 40, j / 6) - 0.5);
      const k = (j * W + i) * 4;
      img.data[k] = base[0] * v; img.data[k + 1] = base[1] * v; img.data[k + 2] = base[2] * v; img.data[k + 3] = 255;
    }
  x.putImageData(img, 0, 0);
  // a few knots
  for (let k = 0; k < 3; k++) {
    const cx = r() * W, cy = r() * H, rr = 3 + r() * 5;
    const g = x.createRadialGradient(cx, cy, 0, cx, cy, rr * 2.2);
    g.addColorStop(0, 'rgba(60,35,18,0.85)'); g.addColorStop(0.5, 'rgba(90,55,30,0.4)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.beginPath(); x.ellipse(cx, cy, rr * 2.6, rr * 1.2, 0, 0, Math.PI * 2); x.fill();
  }
  return finish(c, [1, 1]);
}

export function grassTexture(seed = 3) {
  const S = 512, [c, x] = canvas(S, S), r = rng(seed), n = noise2(seed);
  const img = x.createImageData(S, S);
  for (let j = 0; j < S; j++)
    for (let i = 0; i < S; i++) {
      const v = 0.55 + 0.35 * n(i / 40, j / 40) + 0.25 * n(i / 6, j / 6) - 0.15;
      const k = (j * S + i) * 4;
      img.data[k] = 34 * v; img.data[k + 1] = 72 * v; img.data[k + 2] = 26 * v; img.data[k + 3] = 255;
    }
  x.putImageData(img, 0, 0);
  // little blade strokes
  for (let k = 0; k < 9000; k++) {
    const px = r() * S, py = r() * S, l = 3 + r() * 7, a = -Math.PI / 2 + (r() - 0.5) * 1.2;
    const g = 70 + r() * 70;
    x.strokeStyle = `rgba(${g * 0.45 | 0},${g | 0},${g * 0.3 | 0},${0.35 + r() * 0.4})`;
    x.lineWidth = 0.8 + r();
    x.beginPath(); x.moveTo(px, py); x.lineTo(px + Math.cos(a) * l, py + Math.sin(a) * l); x.stroke();
  }
  return finish(c, [60, 60]);
}

export function concreteTexture(seed = 5) {
  const S = 256, [c, x] = canvas(S, S), r = rng(seed), n = noise2(seed);
  const img = x.createImageData(S, S);
  for (let j = 0; j < S; j++)
    for (let i = 0; i < S; i++) {
      let v = 0.72 + 0.12 * n(i / 30, j / 30) + 0.1 * (r() - 0.5);
      if (r() < 0.004) v *= 0.55;                                   // aggregate pits
      const edge = Math.min(i, j, S - 1 - i, S - 1 - j);
      if (edge < 4) v *= 0.85 + edge * 0.035;                        // chamfered edge
      const k = (j * S + i) * 4;
      img.data[k] = 168 * v; img.data[k + 1] = 164 * v; img.data[k + 2] = 156 * v; img.data[k + 3] = 255;
    }
  x.putImageData(img, 0, 0);
  return finish(c, [1, 1]);
}

/** Soft round sprite used for stars / moon glow. */
export function glowSprite(size = 128) {
  const [c, x] = canvas(size, size), h = size / 2;
  const g = x.createRadialGradient(h, h, 0, h, h, h);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.2, 'rgba(255,255,255,0.6)');
  g.addColorStop(0.5, 'rgba(255,255,255,0.12)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, size, size);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function moonTexture(size = 256) {
  const [c, x] = canvas(size, size), h = size / 2, n = noise2(11), r = rng(12);
  x.fillStyle = '#e9ecf2'; x.beginPath(); x.arc(h, h, h - 2, 0, Math.PI * 2); x.fill();
  const img = x.getImageData(0, 0, size, size);
  for (let j = 0; j < size; j++)
    for (let i = 0; i < size; i++) {
      const k = (j * size + i) * 4; if (!img.data[k + 3]) continue;
      const v = 0.78 + 0.22 * n(i / 22, j / 22) - 0.18 * Math.max(0, n(i / 50 + 3, j / 50) - 0.55) * 3;
      img.data[k] *= v; img.data[k + 1] *= v; img.data[k + 2] *= v * 1.02;
    }
  x.putImageData(img, 0, 0);
  for (let k = 0; k < 14; k++) {
    const a = r() * 6.28, d = r() * h * 0.8, cx = h + Math.cos(a) * d, cy = h + Math.sin(a) * d, rr = 3 + r() * 12;
    x.fillStyle = 'rgba(120,125,140,0.25)'; x.beginPath(); x.arc(cx, cy, rr, 0, 6.28); x.fill();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
