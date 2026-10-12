import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { buildMembers, hexaGeometry, toScene, IN, POSTS, ANG, Rc, pixelNormal } from './gazebo.js';
import { woodTexture, grassTexture, concreteTexture, glowSprite, moonTexture } from './textures.js';
import { parseFseq, buildChannelMap, channelExtent, FseqError } from './fseq.js';

const $ = (s) => document.querySelector(s);
const params = new URLSearchParams(location.search);
const PAVER_TOP = 1.0 * IN;         // posts stand on 16"x16"x2" pavers set 1" proud of the grass
const GAMMA = 1.6;                  // LED PWM is linear, but eyes adapt at night: a mild curve keeps dim bases visible without washing out colours

// ---------------------------------------------------------------- loader UI
const loader = {
  set(p, msg) { $('#load-bar').style.width = `${Math.round(p * 100)}%`; if (msg) $('#load-msg').textContent = msg; },
  fail(msg) { $('#loader').classList.add('error'); $('#load-msg').textContent = msg; },
  done() { $('#loader').classList.add('done'); setTimeout(() => $('#loader').remove(), 900); },
};
let toastTimer;
function toast(msg, err = false, ms = 4200) {
  const t = $('#toast'); t.textContent = msg; t.classList.toggle('err', err); t.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), ms);
}

async function fetchBytes(url, onProgress) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  const total = +res.headers.get('content-length') || 0;
  if (!res.body || !total || !onProgress) return res.arrayBuffer();
  const reader = res.body.getReader(), parts = []; let got = 0;
  for (;;) {
    const { done, value } = await reader.read(); if (done) break;
    parts.push(value); got += value.length; onProgress(Math.min(1, got / total));
  }
  const out = new Uint8Array(got); let o = 0; for (const p of parts) { out.set(p, o); o += p.length; }
  return out.buffer;
}

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/); const head = lines[0].split(',');
  const col = (n) => head.indexOf(n);
  const ix = { index: col('index'), ch: col('channel_start'), m: col('member'), x: col('x_in'), y: col('y_in'), z: col('z_in'), no: col('member_no') };
  if (Object.values(ix).some((v) => v < 0)) throw new Error('pixel CSV is missing a column');
  return lines.slice(1).map((l) => { const c = l.split(','); return { index: +c[ix.index], ch: +c[ix.ch], member: c[ix.m], no: +c[ix.no], x: +c[ix.x], y: +c[ix.y], z: +c[ix.z] }; })
    .sort((a, b) => a.index - b.index);
}

// ---------------------------------------------------------------- renderer / scene
const canvas = $('#view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: params.has('capture') });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
const NIGHT_FOG = new THREE.Color(0x070b17), WOOD_FOG = new THREE.Color(0x101828);
scene.fog = new THREE.FogExp2(NIGHT_FOG.getHex(), 0.03);
scene.background = NIGHT_FOG.clone();

const camera = new THREE.PerspectiveCamera(50, 1, 0.05, 1200);
camera.position.set(5.8, 2.3, 6.4);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.target.set(0, 1.15, 0);
controls.minDistance = 0.3; controls.maxDistance = 40;
controls.maxPolarAngle = Math.PI * 0.97;   // allow looking up from inside; camera height is clamped above the grass in tick()
controls.autoRotateSpeed = 0.6;

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(512, 512), 0.75, 0.5, 0.62);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------------------------------------------------------------- sky, stars, moon
function buildSky() {
  const g = new THREE.SphereGeometry(600, 48, 24);
  const m = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uTop: { value: new THREE.Color(0x01020a) }, uHorizon: { value: new THREE.Color(0x0d1630) }, uGlow: { value: new THREE.Color(0x1b2747) }, uMoonDir: { value: new THREE.Vector3() }, uLift: { value: 0 } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); gl_Position.z = gl_Position.w; }`,
    fragmentShader: `uniform vec3 uTop, uHorizon, uGlow, uMoonDir; uniform float uLift; varying vec3 vDir;
      void main(){ float h = clamp(vDir.y, 0., 1.);
        vec3 c = mix(uHorizon, uTop, pow(h, .45));
        float m = max(dot(normalize(vDir), uMoonDir), 0.); c += uGlow * (pow(m, 24.) * .9 + pow(m, 4.) * .18);
        c += vec3(.02,.03,.05) * uLift;
        if (vDir.y < 0.) c = uHorizon * .6;
        c += (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - .5) / 255.;   // dither banding
        gl_FragColor = vec4(c, 1.); }`,
  });
  return new THREE.Mesh(g, m);
}
const sky = buildSky(); scene.add(sky);
const MOON_DIR = new THREE.Vector3(-0.55, 0.42, -0.72).normalize();
sky.material.uniforms.uMoonDir.value.copy(MOON_DIR);

function buildStars(n = 4200) {
  const pos = new Float32Array(n * 3), sz = new Float32Array(n), ph = new Float32Array(n), col = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const u = Math.random(), v = Math.random() * 0.97 + 0.03;
    const th = u * Math.PI * 2, y = Math.pow(v, 0.8), r = Math.sqrt(1 - y * y);
    pos.set([Math.cos(th) * r * 560, y * 560, Math.sin(th) * r * 560], i * 3);
    sz[i] = Math.pow(Math.random(), 6) * 3.2 + 0.7; ph[i] = Math.random() * 100;
    const t = Math.random(); col.set(t < 0.15 ? [1, 0.85, 0.7] : t < 0.35 ? [0.75, 0.85, 1] : [1, 1, 1], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('size', new THREE.BufferAttribute(sz, 1));
  g.setAttribute('phase', new THREE.BufferAttribute(ph, 1)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
    uniforms: { uTime: { value: 0 }, uPR: { value: renderer.getPixelRatio() }, uFade: { value: 1 } },
    vertexShader: `attribute float size, phase; attribute vec3 color; uniform float uTime, uPR; varying float vA; varying vec3 vC;
      void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.); gl_Position = projectionMatrix * mv; gl_Position.z = gl_Position.w * .99999;
        float tw = .75 + .25 * sin(uTime * (1.3 + fract(phase) * 2.) + phase);
        vA = tw * smoothstep(0., .25, normalize(position).y) * min(size, 1.6) / 1.6; vC = color; gl_PointSize = size * uPR * 1.6; }`,
    fragmentShader: `varying float vA; varying vec3 vC; uniform float uFade; void main(){ float d = length(gl_PointCoord - .5) * 2.; float a = exp(-d * d * 5.) * vA * uFade; gl_FragColor = vec4(vC * a * .9, a); }`,
  });
  return new THREE.Points(g, m);
}
const stars = buildStars(); scene.add(stars);

const moonGroup = new THREE.Group();
{
  const moon = new THREE.Sprite(new THREE.SpriteMaterial({ map: moonTexture(), fog: false, depthWrite: false, color: 0xdfe6ff }));
  moon.scale.setScalar(22); moonGroup.add(moon);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowSprite(), fog: false, depthWrite: false, blending: THREE.AdditiveBlending, color: 0x5a6f9c, opacity: 0.55, transparent: true }));
  halo.scale.setScalar(120); moonGroup.add(halo);
  moonGroup.position.copy(MOON_DIR).multiplyScalar(520);
  moonGroup.renderOrder = -1;
  scene.add(moonGroup);
}

// ---------------------------------------------------------------- lights
const hemi = new THREE.HemisphereLight(0x30406a, 0x0b1208, 0.5); scene.add(hemi);
const moonLight = new THREE.DirectionalLight(0x9fb4e6, 0.9);
moonLight.position.copy(MOON_DIR).multiplyScalar(20); moonLight.castShadow = true;
moonLight.shadow.mapSize.set(2048, 2048);
Object.assign(moonLight.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 50 });
moonLight.shadow.bias = -0.0004; moonLight.shadow.normalBias = 0.02; moonLight.shadow.radius = 4;
scene.add(moonLight);
// "wood lit": warm garden floodlights so the framing reads clearly
const flood = new THREE.Group(); flood.visible = false; scene.add(flood);
{
  const a = new THREE.SpotLight(0xffd2a1, 60, 30, Math.PI / 5, 0.6, 1.6); a.position.set(6, 5, 7); a.castShadow = true; a.shadow.mapSize.set(2048, 2048); a.shadow.bias = -0.0003;
  const b = new THREE.SpotLight(0xffe6c8, 35, 30, Math.PI / 5, 0.7, 1.6); b.position.set(-7, 4, -5);
  const c = new THREE.SpotLight(0xc8d6ff, 25, 30, Math.PI / 5, 0.7, 1.6); c.position.set(-5, 6, 7);
  for (const s of [a, b, c]) { s.target.position.set(0, 1.0, 0); flood.add(s, s.target); }
  flood.add(new THREE.HemisphereLight(0x8090b0, 0x2a3a1a, 0.8));
}

// ---------------------------------------------------------------- ground, grass, pavers
const grassTex = grassTexture();
const ground = new THREE.Mesh(new THREE.CircleGeometry(300, 96), new THREE.MeshStandardMaterial({ map: grassTex, roughness: 1, metalness: 0, color: 0x9aa88a }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

function buildGrass(count) {
  const blade = new THREE.BufferGeometry();
  // tapered 2-segment blade, 1 unit tall, bent later in the vertex shader
  const w = 0.5, v = [-w, 0, 0, w, 0, 0, -w * 0.6, 0.5, 0.02, w * 0.6, 0.5, 0.02, 0, 1, 0.08];
  blade.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
  blade.setAttribute('color', new THREE.Float32BufferAttribute([0.25, 0.4, 0.2, 0.25, 0.4, 0.2, 0.55, 0.75, 0.4, 0.55, 0.75, 0.4, 0.85, 1, 0.6], 3));
  blade.setIndex([0, 1, 2, 1, 3, 2, 2, 3, 4]); blade.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, side: THREE.DoubleSide });
  const uTime = { value: 0 };
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      vec3 ip = vec3(instanceMatrix[3][0], 0., instanceMatrix[3][2]);
      float sway = sin(uTime * 1.3 + ip.x * 1.7 + ip.z * 1.1) * .5 + sin(uTime * 2.7 + ip.x * 4.1) * .25;
      transformed.z += sway * .18 * position.y * position.y;`);
    // keep normals pointing up so blades catch sky light like a lawn rather than flickering
    sh.vertexShader = sh.vertexShader.replace('#include <defaultnormal_vertex>', '#include <defaultnormal_vertex>\n transformedNormal = normalize(mix(transformedNormal, normalMatrix * vec3(0.,1.,0.), .6));');
  };
  const mesh = new THREE.InstancedMesh(blade, mat, count);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3(), c = new THREE.Color(), e = new THREE.Euler();
  const pavers = POSTS.map(([x, y]) => toScene(x, y, 0));
  let k = 0;
  while (k < count) {
    const r = Math.pow(Math.random(), 0.62) * 9.5, th = Math.random() * Math.PI * 2;
    p.set(Math.cos(th) * r, 0, Math.sin(th) * r);
    if (pavers.some((v) => Math.abs(v.x - p.x) < 0.26 && Math.abs(v.z - p.z) < 0.26)) continue;
    const h = 0.05 + Math.random() * 0.07 + Math.random() * Math.random() * 0.05;
    e.set((Math.random() - 0.5) * 0.5, Math.random() * Math.PI * 2, (Math.random() - 0.5) * 0.5); q.setFromEuler(e);
    s.set(0.011 + Math.random() * 0.008, h, 1);
    m.compose(p, q, s); mesh.setMatrixAt(k, m);
    c.setHSL(0.23 + Math.random() * 0.07, 0.4 + Math.random() * 0.2, 0.2 + Math.random() * 0.14); mesh.setColorAt(k, c);
    k++;
  }
  mesh.receiveShadow = true; mesh.frustumCulled = false;
  return { mesh, uTime };
}
const isMobile = matchMedia('(max-width: 760px)').matches || /Mobi/.test(navigator.userAgent);
const grass = buildGrass(isMobile ? 40000 : 110000); scene.add(grass.mesh);

const paverMat = new THREE.MeshStandardMaterial({ map: concreteTexture(), roughness: 0.95, color: 0xc8c4bc });
const paverGeo = new THREE.BoxGeometry(16 * IN, 2 * IN, 16 * IN);
POSTS.forEach(([x, y], i) => {
  const p = new THREE.Mesh(paverGeo, paverMat); const c = toScene(x, y, 0);
  p.position.set(c.x, PAVER_TOP - IN, c.z); p.rotation.y = ANG[i];
  p.castShadow = p.receiveShadow = true; scene.add(p);
});

// distant tree line silhouettes for depth
{
  const g = new THREE.ConeGeometry(1, 1, 7); const mat = new THREE.MeshStandardMaterial({ color: 0x060a08, roughness: 1 });
  const n = 180, mesh = new THREE.InstancedMesh(g, mat, n), m = new THREE.Matrix4();
  for (let i = 0; i < n; i++) {
    const th = (i / n) * Math.PI * 2 + Math.random() * 0.05, r = 60 + Math.random() * 30, h = 5 + Math.random() * 7, w = 2.2 + Math.random() * 2.5;
    m.compose(new THREE.Vector3(Math.cos(th) * r, h / 2 - 0.3, Math.sin(th) * r), new THREE.Quaternion(), new THREE.Vector3(w, h, w)); mesh.setMatrixAt(i, m);
  }
  scene.add(mesh);
}

// ---------------------------------------------------------------- gazebo framing
const gazebo = new THREE.Group(); gazebo.position.y = PAVER_TOP; scene.add(gazebo);
{
  const M = buildMembers();
  const tex = (rgb, seed) => woodTexture(rgb, seed);
  const mats = {
    post: new THREE.MeshStandardMaterial({ map: tex([186, 140, 92], 1), roughness: 0.82 }),
    rail: new THREE.MeshStandardMaterial({ map: tex([196, 156, 108], 2), roughness: 0.8 }),
    brace: new THREE.MeshStandardMaterial({ map: tex([170, 122, 78], 3), roughness: 0.85 }),
    rafter: new THREE.MeshStandardMaterial({ map: tex([160, 112, 70], 4), roughness: 0.85 }),
    ring: new THREE.MeshStandardMaterial({ map: tex([140, 96, 60], 5), roughness: 0.85 }),
  };
  for (const m of Object.values(mats)) m.side = THREE.DoubleSide;
  const add = (list, mat) => { const mesh = new THREE.Mesh(hexaGeometry(list), mat); mesh.castShadow = mesh.receiveShadow = true; gazebo.add(mesh); };
  add(M.post, mats.post); add([...M.r36, ...M.r72, ...M.joist], mats.rail);
  add([...M.brace_upper, ...M.brace_lower], mats.brace); add(M.rafter, mats.rafter); add(M.ring, mats.ring);
}

// ---------------------------------------------------------------- pixels
let PIX = null;          // { points, colors(Uint8), csv, starts, lights }
function buildPixels(csv) {
  const n = csv.length, pos = new Float32Array(n * 3), dir = new Float32Array(n * 3), col = new Uint8Array(n * 3);
  csv.forEach((p, i) => {
    const v = toScene(p.x, p.y, p.z); pos.set([v.x, v.y, v.z], i * 3);
    const d = pixelNormal(p.member, p.x, p.y); dir.set([d.x, d.y, d.z], i * 3);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('dir', new THREE.BufferAttribute(dir, 3));
  const ca = new THREE.BufferAttribute(col, 3, true); ca.setUsage(THREE.DynamicDrawUsage); g.setAttribute('color', ca);
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uSize: { value: 0.07 }, uScale: { value: 600 }, uBright: { value: 1 }, uGamma: { value: GAMMA }, uOff: { value: 0.035 } },
    vertexShader: `attribute vec3 dir; attribute vec3 color; uniform float uSize, uScale, uBright, uGamma, uOff;
      varying vec3 vCol; varying float vCore;
      void main(){
        vec3 wp = (modelMatrix * vec4(position, 1.)).xyz;
        vec3 toCam = normalize(cameraPosition - wp);
        float f = dot(normalize(dir), toCam);
        float face = mix(0.14, 1.0, smoothstep(-0.35, 0.45, f));         // bullet pixels face inward
        vec3 lin = pow(color, vec3(uGamma));
        vCol = lin * uBright * face;
        vCore = smoothstep(-0.2, 0.6, f);
        vec4 mv = viewMatrix * vec4(wp, 1.);
        gl_PointSize = clamp(uSize * uScale / -mv.z, 1.5, 96.);
        gl_Position = projectionMatrix * mv;
        if (max(max(color.r, color.g), color.b) < 0.002) gl_Position = vec4(2., 2., 2., 1.);  // cull dark pixels
      }`,
    fragmentShader: `varying vec3 vCol; varying float vCore;
      void main(){
        float d = length(gl_PointCoord - .5) * 2.; if (d > 1.) discard;
        float core = smoothstep(.32, .05, d);
        float halo = exp(-d * d * 8.) * .4;
        vec3 c = vCol * (core * (1.6 + 2.4 * vCore) + halo);
        c += vec3(1.) * core * vCore * dot(vCol, vec3(.3,.5,.2)) * .35;      // whitish hot centre
        gl_FragColor = vec4(c, 1.);
      }`,
  });
  const points = new THREE.Points(g, mat); points.frustumCulled = false; points.renderOrder = 2; gazebo.add(points);

  // a few coloured point lights driven by the average pixel colour of each sector, so the show lights the wood and grass
  const groups = [], lights = [];
  for (let s = 0; s < 13; s++) groups.push([]);
  csv.forEach((p, i) => {
    if (/Ring|Rafter/i.test(p.member) && p.z > 80) { groups[12].push(i); return; }
    let a = Math.atan2(p.y, p.x) - ANG[0]; a = ((a % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
    groups[Math.floor(a / (Math.PI / 6)) % 12].push(i);
  });
  for (let s = 0; s < 13; s++) {
    let pos;
    if (s === 12) pos = new THREE.Vector3(0, 2.05, 0);
    else { const a = ANG[s] + Math.PI / 12, r = Rc * 0.86; pos = toScene(r * Math.cos(a), r * Math.sin(a), 44); }
    const L = new THREE.PointLight(0xffffff, 0, s === 12 ? 9 : 7, 1.6); L.position.copy(pos); gazebo.add(L); lights.push(L);
  }
  const lut = new Float32Array(256); for (let i = 0; i < 256; i++) lut[i] = Math.pow(i / 255, GAMMA);
  return { points, colors: col, attr: ca, csv, starts: Int32Array.from(csv, (p) => p.ch), lights, groups, lut };
}

function updateLights(bright) {
  const { colors, lights, groups, lut } = PIX;
  for (let s = 0; s < lights.length; s++) {
    const idx = groups[s]; let r = 0, g = 0, b = 0;
    for (const i of idx) { r += lut[colors[3 * i]]; g += lut[colors[3 * i + 1]]; b += lut[colors[3 * i + 2]]; }
    const sum = r + g + b, L = lights[s];
    if (sum <= 1e-4) { L.intensity = 0; continue; }
    L.color.setRGB(r / sum * 3, g / sum * 3, b / sum * 3).multiplyScalar(1 / 3);
    L.intensity = (sum / idx.length) * idx.length * 0.012 * bright * state.lightGain;
  }
}

// ---------------------------------------------------------------- playback state
const state = {
  manifest: null, shows: [], cur: null, playing: !params.has('paused'), t: 0, speed: 1, bright: 1, glow: 1,
  wood: false, lightGain: 1, lastFrame: -1,
};
const SPEEDS = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4];

function fmt(s) { const m = Math.floor(s / 60); return `${m}:${(s - m * 60).toFixed(1).padStart(4, '0')}`; }
function setRangeFill(el) { const p = ((el.value - el.min) / (el.max - el.min)) * 100; el.style.setProperty('--p', `${p}%`); }

/** Validate a parsed sequence against the gazebo channel layout. Returns {ok, level, msg, map}. */
function checkLayout(header, startChannel) {
  const need = PIX.starts.length * 3, ext = channelExtent(header);
  const last = Math.max(...PIX.starts) + 2;   // last model channel (1-based, relative)
  if (ext < last) return { ok: false, level: 'err', msg: `Channel count mismatch: this file has ${ext.toLocaleString()} channels, the gazebo model needs ${need.toLocaleString()} (1,525 RGB pixels, channels 1-${last.toLocaleString()}). Export the sequence with the gazebo model on its own controller/universe, or check the model in xLights matches model/gazebo.xmodel.` };
  const map = buildChannelMap(header, PIX.starts, startChannel);
  if (map.missing) return { ok: false, level: 'err', msg: `With start channel ${startChannel}, ${map.missing.toLocaleString()} of the gazebo's ${need.toLocaleString()} channels are not in this file (it covers ${ext.toLocaleString()} channels${header.sparse.length ? ' in sparse ranges' : ''}).` };
  if (ext !== last || startChannel !== 1)
    return { ok: true, level: 'warn', map, msg: `This file has ${ext.toLocaleString()} channels; playing channels ${startChannel.toLocaleString()}-${(startChannel + last - 1).toLocaleString()} as the gazebo. Change the start channel if the gazebo sits elsewhere in your show.` };
  return { ok: true, level: 'ok', map, msg: 'Channel layout matches the gazebo model (4,575 channels, RGB).' };
}

function showInfo(show) {
  const el = $('#file-info'); const h = show.header;
  if (!show.user) { el.hidden = true; return; }
  el.hidden = false; el.className = 'file-info ' + (show.check.level === 'ok' ? '' : show.check.level);
  const ext = channelExtent(h);
  el.innerHTML = `<b>${escapeHtml(show.title)}</b><div>${escapeHtml(show.check.msg)}</div>
    <dl><dt>Format</dt><dd>FSEQ v${h.version}, ${h.compression}${h.blocks.length ? ` (${h.blocks.filter((b) => b.length).length} blocks)` : ''}${h.sparse.length ? `, ${h.sparse.length} sparse ranges` : ''}</dd>
    <dt>Channels</dt><dd>${h.channels.toLocaleString()}${ext !== h.channels ? ` stored, up to ch ${ext.toLocaleString()}` : ''}</dd>
    <dt>Frames</dt><dd>${h.frames.toLocaleString()} @ ${h.stepMs} ms (${+h.fps.toFixed(2)} fps), ${fmt(h.seconds)}</dd>
    ${h.vars.mf ? `<dt>Media</dt><dd>${escapeHtml(h.vars.mf)}</dd>` : ''}${h.vars.sp ? `<dt>Producer</dt><dd>${escapeHtml(h.vars.sp)}</dd>` : ''}
    ${ext > 4575 || show.startChannel !== 1 ? `<dt>Start ch</dt><dd><input id="start-ch" type="number" min="1" max="${ext}" value="${show.startChannel}"></dd>` : ''}</dl>
    ${h.warning ? `<div>${escapeHtml(h.warning)}</div>` : ''}`;
  const sc = $('#start-ch');
  if (sc) sc.onchange = () => {
    const v = Math.max(1, Math.floor(+sc.value || 1)); const chk = checkLayout(h, v);
    if (!chk.ok) { toast(chk.msg, true, 7000); sc.value = show.startChannel; return; }
    show.startChannel = v; show.check = chk; state.lastFrame = -1; showInfo(show);
  };
}
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

async function ensureLoaded(show, onProgress) {
  if (show.data) return show;
  if (!show.loading) show.loading = (async () => {
    const buf = await fetchBytes(show.file, onProgress);
    const { header, data } = await parseFseq(buf);
    const check = checkLayout(header, 1);
    if (!check.ok) throw new FseqError(check.msg);
    Object.assign(show, { header, data, check, startChannel: 1 });
    return show;
  })();
  try { return await show.loading; } catch (e) { show.loading = null; throw e; }
}

async function selectShow(show, { keepTime = false } = {}) {
  const li = show.li; li?.classList.add('loading');
  try { await ensureLoaded(show); } catch (e) { li?.classList.remove('loading'); toast(`${show.title}: ${e.message}`, true, 8000); return; }
  li?.classList.remove('loading');
  state.cur = show; if (!keepTime) state.t = 0; state.lastFrame = -1;
  document.querySelectorAll('.show-list li').forEach((x) => x.classList.toggle('active', x === li));
  $('#now-title').textContent = show.title;
  $('#hud-show').textContent = show.title;
  const h = show.header;
  $('#now-meta').textContent = `${fmt(h.seconds)} · ${+h.fps.toFixed(2)} fps · ${h.frames} frames${show.user ? ' · your file' : ''}`;
  showInfo(show);
  if (!show.user) {
    history.replaceState(null, '', updateQuery({ show: show.id }));
    // prefetch the next built-in show so "next" is instant (1-2 MB each; the rest load on demand)
    const nx = state.shows[(state.shows.indexOf(show) + 1) % state.shows.length];
    if (nx && !nx.data) setTimeout(() => ensureLoaded(nx).catch((e) => console.warn(e)), 1500);
  }
}
function updateQuery(kv) { const p = new URLSearchParams(location.search); for (const [k, v] of Object.entries(kv)) v == null ? p.delete(k) : p.set(k, v); const s = p.toString(); return location.pathname + (s ? '?' + s : ''); }

function renderList() {
  const ul = $('#show-list'); ul.innerHTML = '';
  const hues = { rainbow_chase: 'linear-gradient(#f44,#fd4,#4f8,#48f,#c4f)', rafter_spiral: '#5a8cff', wipe_up: '#ffb000', twinkle: '#bfe3ff', breathing: '#c070ff', fire: '#ff5a1f', christmas: 'linear-gradient(#e33,#2c5)', candlelight_dinner: '#ffae4a', starry_night: '#3f5fd8', slow_ember_glow: '#ffd7a0', aurora: 'linear-gradient(#2fd59a,#8a4dff)', golden_hour: 'linear-gradient(#ffb347,#ff6f91,#9b6bff)', eye_of_sauron: '#ff3b00', lantern_fireflies: '#ffe066' };
  for (const s of state.shows) ul.appendChild(makeItem(s, hues[s.id] || '#888'));
  $('#show-count').textContent = state.shows.length;
}
function makeItem(s, swatch) {
  const li = document.createElement('li'); li.setAttribute('role', 'option'); li.tabIndex = 0;
  li.innerHTML = `<span class="swatch" style="background:${swatch}"></span><div class="t"><span class="name">${escapeHtml(s.title)}</span><span class="dur">${fmt(s.seconds)}</span></div>
    ${s.description ? `<div class="desc">${escapeHtml(s.description)}</div>` : ''}${s.mood ? `<span class="mood">${escapeHtml(s.mood)}</span>` : ''}`;
  li.onclick = () => selectShow(s);
  li.onkeydown = (e) => { if (e.key === 'Enter') selectShow(s); };
  s.li = li; return li;
}

// user files: button + drag and drop
/** Pick a start channel: 1 if it fits, else the first sparse range big enough to hold the gazebo. */
function autoStart(header) {
  let chk = checkLayout(header, 1);
  if (chk.ok) return { start: 1, check: chk };
  const last = Math.max(...PIX.starts) + 2;
  for (const r of header.sparse || []) {
    if (r.count < last) continue;
    const c = checkLayout(header, r.start + 1);
    if (c.ok) { c.level = 'warn'; c.msg = `Auto-detected the gazebo at start channel ${(r.start + 1).toLocaleString()} (sparse range of ${r.count.toLocaleString()} channels). ` + c.msg.replace(/^This file has [^;]*; playing/, 'Playing'); return { start: r.start + 1, check: c }; }
  }
  return { start: 1, check: chk };
}
function showLoadError(name, header, msg, retry) {
  const el = $('#file-info'); el.hidden = false; el.className = 'file-info err';
  const ext = header ? channelExtent(header) : 0;
  el.innerHTML = `<b>${escapeHtml(name)}</b><div>${escapeHtml(msg)}</div>` + (header ? `<dl><dt>Format</dt><dd>FSEQ v${header.version}, ${header.compression}${header.sparse.length ? `, ${header.sparse.length} sparse ranges` : ''}</dd>
    <dt>Channels</dt><dd>${ext.toLocaleString()}</dd><dt>Frames</dt><dd>${header.frames.toLocaleString()} @ ${header.stepMs} ms</dd>
    ${retry ? `<dt>Start ch</dt><dd><input id="start-ch" type="number" min="1" max="${ext}" value="1"> <span class="muted">try another</span></dd>` : ''}</dl>` : '');
  const sc = $('#start-ch'); if (sc && retry) sc.onchange = () => retry(Math.max(1, Math.floor(+sc.value || 1)));
}
async function addUserShow(file, header, data, start, check) {
  const show = { id: 'user:' + file.name, title: file.name.replace(/\.fseq$/i, ''), user: true, header, data, check, startChannel: start,
    seconds: header.seconds, description: `${(file.size / 1e6).toFixed(2)} MB · FSEQ v${header.version} · ${header.compression} · ${channelExtent(header).toLocaleString()} ch`, mood: 'Your file' };
  $('#user-shows-wrap').hidden = false;
  const ul = $('#user-list'); [...ul.children].forEach((li) => { if (li.dataset.id === show.id) li.remove(); });
  const li = makeItem(show, '#7aa2ff'); li.dataset.id = show.id; ul.prepend(li);
  await selectShow(show);
  toast(`Loaded ${file.name}` + (check.level === 'warn' ? ' (see channel note)' : ''));
}
async function loadUserFile(file) {
  if (!file) return;
  if (!/\.fseq$/i.test(file.name)) toast(`"${file.name}" does not end in .fseq; trying anyway…`);
  let header = null;
  try {
    const parsed = await parseFseq(await file.arrayBuffer()); header = parsed.header;
    const { start, check } = autoStart(header);
    if (check.ok) return await addUserShow(file, header, parsed.data, start, check);
    const ext = channelExtent(header), last = Math.max(...PIX.starts) + 2;
    const retry = ext >= last ? async (st) => {
      const c = checkLayout(header, st);
      if (c.ok) await addUserShow(file, header, parsed.data, st, c); else showLoadError(file.name, header, c.msg, retry);
    } : null;
    showLoadError(file.name, header, check.msg, retry);
    toast('Channel count mismatch: see details in the panel.', true, 6000);
  } catch (e) {
    showLoadError(file.name, header, e.message || String(e), null);
    toast(e instanceof FseqError ? e.message : `Could not read ${file.name}: ${e.message}`, true, 8000);
    console.warn(e);
  }
}
$('#file-input').onchange = (e) => { loadUserFile(e.target.files[0]); e.target.value = ''; };
let dragDepth = 0;
addEventListener('dragenter', (e) => { if ([...(e.dataTransfer?.types || [])].includes('Files')) { dragDepth++; document.body.classList.add('dragging'); e.preventDefault(); } });
addEventListener('dragleave', () => { if (--dragDepth <= 0) { dragDepth = 0; document.body.classList.remove('dragging'); } });
addEventListener('dragover', (e) => e.preventDefault());
addEventListener('drop', (e) => { e.preventDefault(); dragDepth = 0; document.body.classList.remove('dragging'); loadUserFile(e.dataTransfer?.files?.[0]); });

// ---------------------------------------------------------------- controls UI
function setPlaying(p) { state.playing = p; document.body.classList.toggle('paused', !p); }
$('#btn-play').onclick = () => setPlaying(!state.playing);
function step(d) {
  const i = state.shows.indexOf(state.cur); const n = state.shows.length;
  selectShow(state.shows[((i < 0 ? 0 : i) + d + n) % n]);
}
$('#btn-prev').onclick = () => step(-1); $('#btn-next').onclick = () => step(1);
const scrub = $('#scrub'); let scrubbing = false;
scrub.oninput = () => { if (!state.cur) return; scrubbing = true; state.t = (scrub.value / 1000) * state.cur.header.seconds; state.lastFrame = -1; setRangeFill(scrub); };
scrub.onchange = () => { scrubbing = false; };
const sb = $('#s-bright'), ss = $('#s-speed'), sg = $('#s-glow');
sb.oninput = () => { state.bright = sb.value / 100; $('#o-bright').textContent = `${sb.value}%`; setRangeFill(sb); state.lastFrame = -1; };
ss.oninput = () => { state.speed = SPEEDS[ss.value]; $('#o-speed').textContent = `${state.speed.toFixed(2)}×`; setRangeFill(ss); };
sg.oninput = () => { state.glow = sg.value / 100; $('#o-glow').textContent = `${sg.value}%`; setRangeFill(sg); applyMode(); };
[sb, ss, sg, scrub].forEach(setRangeFill);

// camera presets (scene: entrance faces +Z)
const CAMS = {
  outside: { pos: [4.6, 2.05, 5.6], target: [0, 1.15, 0], fov: 50 },
  inside: { pos: [0.55, 0.55, 0.75], target: [-0.05, 2.3, -0.1], fov: 80 },
  entrance: { pos: [0, 1.45, 5.4], target: [0, 1.25, 0], fov: 50 },
  top: { pos: [0, 7.4, 0.001], target: [0, 0.6, 0], fov: 50 },
};
let camTween = null;
function setCam(name, instant = false) {
  const c = CAMS[name]; if (!c) return;
  document.querySelectorAll('#cams .chip').forEach((b) => b.classList.toggle('active', b.dataset.cam === name));
  const from = { pos: camera.position.clone(), target: controls.target.clone(), fov: camera.fov };
  const tgt = new THREE.Vector3(...c.target), pos = new THREE.Vector3(...c.pos);
  // portrait / narrow screens: back the camera off so the whole gazebo fits horizontally
  if (name !== 'inside' && camera.aspect < 1.25) pos.sub(tgt).multiplyScalar(Math.min(1.8, 1.05 / camera.aspect)).add(tgt);
  const to = { pos, target: tgt, fov: c.fov };
  if (instant) { camera.position.copy(to.pos); controls.target.copy(to.target); camera.fov = to.fov; camera.updateProjectionMatrix(); controls.update(); return; }
  camTween = { from, to, t0: performance.now(), dur: 1100 };
}
document.querySelectorAll('#cams .chip').forEach((b) => (b.onclick = () => setCam(b.dataset.cam)));
controls.addEventListener('start', () => { camTween = null; document.querySelectorAll('#cams .chip').forEach((b) => b.classList.remove('active')); });
$('#t-orbit').onchange = (e) => { controls.autoRotate = e.target.checked; };
$('#t-wood').onchange = (e) => { state.wood = e.target.checked; applyMode(); };

function applyMode() {
  const w = state.wood;
  flood.visible = w;
  hemi.intensity = w ? 0.3 : 0.5;
  moonLight.intensity = w ? 0.35 : 0.9;
  scene.fog.color.copy(w ? WOOD_FOG : NIGHT_FOG); scene.fog.density = w ? 0.022 : 0.03;
  scene.background.copy(scene.fog.color);
  sky.material.uniforms.uLift.value = w ? 1 : 0;
  renderer.toneMappingExposure = w ? 1.05 : 1.0;
  bloom.strength = 0.75 * state.glow; bloom.threshold = w ? 0.75 : 0.62;
  state.lightGain = w ? 0.5 : 1;
}

$('#sheet-toggle').onclick = () => $('#panel').classList.toggle('collapsed');
addEventListener('keydown', (e) => {
  if (e.target.matches('input[type=number], input[type=text]')) return;
  if (e.code === 'Space') { e.preventDefault(); setPlaying(!state.playing); }
  else if (e.key === 'ArrowRight') step(1); else if (e.key === 'ArrowLeft') step(-1);
  else if ('1234'.includes(e.key) && e.key.length === 1) setCam(['outside', 'inside', 'entrance', 'top'][+e.key - 1]);
  else if (e.key === 'r' || e.key === 'R') { const t = $('#t-orbit'); t.checked = !t.checked; t.onchange({ target: t }); }
  else if (e.key === 'w' || e.key === 'W') { const t = $('#t-wood'); t.checked = !t.checked; t.onchange({ target: t }); }
});

// ---------------------------------------------------------------- frame loop
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); composer.setSize(w, h); camera.aspect = w / h;
  // keep the gazebo centred in the area left of the side panel on wide screens
  const panel = $('#panel'), shift = w > 760 && panel ? (panel.offsetWidth + 12) / 2 : 0;
  const yshift = w <= 760 ? Math.min(h * 0.18, 120) : 0;   // bottom sheet on phones: lift the view a little
  if (shift || yshift) camera.setViewOffset(w, h, shift, yshift, w, h); else camera.clearViewOffset();
  camera.updateProjectionMatrix();
  if (PIX) PIX.points.material.uniforms.uScale.value = (h * renderer.getPixelRatio()) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2));
}
addEventListener('resize', resize);

function writeFrame(show, f) {
  const { data, header } = show, ch = header.channels, base = f * ch, out = PIX.colors, map = show.check.map;
  if (map.contiguous) out.set(data.subarray(base + map.offset, base + map.offset + out.length));
  else { const m = map.map; for (let k = 0; k < out.length; k++) out[k] = m[k] >= 0 ? data[base + m[k]] : 0; }
  PIX.attr.needsUpdate = true;
}

let hudT = 0, lastNow = performance.now(), elapsed = 0;
function tick() {
  const now = performance.now(), dt = Math.min((now - lastNow) / 1000, 0.1); lastNow = now; elapsed += dt;
  if (camTween) {
    const k = Math.min(1, (now - camTween.t0) / camTween.dur), e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    camera.position.lerpVectors(camTween.from.pos, camTween.to.pos, e); controls.target.lerpVectors(camTween.from.target, camTween.to.target, e);
    camera.fov = camTween.from.fov + (camTween.to.fov - camTween.from.fov) * e; camera.updateProjectionMatrix();
    if (PIX) resize();
    if (k >= 1) camTween = null;
  }
  controls.update(dt);
  if (camera.position.y < 0.12) camera.position.y = 0.12;
  const show = state.cur;
  if (show && PIX) {
    const h = show.header;
    if (state.playing && !scrubbing) state.t = (state.t + dt * state.speed) % h.seconds;
    const f = Math.min(h.frames - 1, Math.floor((state.t * 1000) / h.stepMs));
    if (f !== state.lastFrame) { writeFrame(show, f); state.lastFrame = f; updateLights(state.bright); }
    PIX.points.material.uniforms.uBright.value = state.bright * 2.2;
    if (now - hudT > 100) { hudT = now; $('#hud-time').textContent = `${fmt(state.t)} / ${fmt(h.seconds)} · frame ${f + 1}/${h.frames}`; if (!scrubbing) { scrub.value = Math.round((state.t / h.seconds) * 1000); setRangeFill(scrub); } }
  }
  grass.uTime.value = elapsed; stars.material.uniforms.uTime.value = elapsed;
  composer.render();
  requestAnimationFrame(tick);
}

// ---------------------------------------------------------------- boot
async function boot() {
  try {
    if (!renderer.capabilities.isWebGL2) throw new Error('WebGL 2 is required.');
    loader.set(0.05, 'Loading pixel model…');
    const [manifest, csvText] = await Promise.all([
      fetch('sequences/manifest.json').then((r) => { if (!r.ok) throw new Error('manifest.json: HTTP ' + r.status); return r.json(); }),
      fetch('model/gazebo_pixels.csv').then((r) => { if (!r.ok) throw new Error('gazebo_pixels.csv: HTTP ' + r.status); return r.text(); }),
    ]);
    const csv = parseCSV(csvText);
    PIX = buildPixels(csv);
    state.manifest = manifest;
    state.shows = manifest.shows.map((s) => ({ ...s }));
    renderList();
    const first = state.shows.find((s) => s.id === params.get('show')) || state.shows[0];
    loader.set(0.2, `Loading “${first.title}” (${(first.bytes / 1e6).toFixed(1)} MB)…`);
    await ensureLoaded(first, (p) => loader.set(0.2 + 0.7 * p));
    loader.set(0.95, 'Compiling shaders…');
    if (innerWidth <= 760) $('#panel').classList.add('collapsed');
    resize();
    if (params.get('mode') === 'wood') { $('#t-wood').checked = true; state.wood = true; }
    applyMode();
    setCam(params.get('cam') || 'outside', true);
    if (params.get('orbit') === '1') { $('#t-orbit').checked = true; controls.autoRotate = true; }
    await selectShow(first);
    if (params.has('t')) state.t = +params.get('t');
    setPlaying(state.playing);
    renderer.compile(scene, camera);
    tick();
    loader.set(1, 'Ready'); setTimeout(() => loader.done(), 250);
    window.__gazebo = { state, setCam, selectShow, loadUserFile, pix: PIX, ready: true, camera, controls };
  } catch (e) {
    console.error(e); loader.fail(`Could not start: ${e.message}`);
  }
}
boot();
