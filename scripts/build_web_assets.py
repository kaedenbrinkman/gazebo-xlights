#!/usr/bin/env python3
"""Copy the show .fseq files (as-is) and the pixel table into web/, write web/sequences/manifest.json,
and verify that everything the browser player relies on is consistent.

Run from the repo root:  python3 scripts/build_web_assets.py [--regen]

Checks:
  * FSEQ v2 header of every file (magic, version, data offset, channel count, frames, step, compression)
  * channel count == 3 x pixel rows in model/gazebo_pixels.csv, and CSV channel_start == 3*(index-1)+1
  * CSV x/y/z == scripts/xl_common.XYZ (node order = wiring order)
  * frame data == build/anim_<name>.npy (generator output, quantised the same way) when present;
    --regen recomputes frames from scripts/xl_anim*.py instead (slower, no files written)
"""
import csv, json, os, re, shutil, struct, sys, hashlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
WEB = os.path.join(ROOT, 'web')
ORDER = ['rainbow_chase', 'rafter_spiral', 'wipe_up', 'twinkle', 'breathing', 'fire', 'christmas',
         'candlelight_dinner', 'starry_night', 'slow_ember_glow', 'aurora', 'golden_hour',
         'eye_of_sauron', 'lantern_fireflies']

def parse_header(b):
    """Minimal FSEQ v1/v2 header parse (mirrors web/js/fseq.js)."""
    if b[:4] not in (b'PSEQ', b'FSEQ'): raise ValueError('bad magic %r' % b[:4])
    off, minor, major, hlen, ch, nf, step = struct.unpack_from('<HBBHIIB', b, 4)
    h = dict(magic=b[:4].decode(), data_offset=off, version=f'{major}.{minor}', header_len=hlen,
             channels=ch, frames=nf, step_ms=step)
    if major >= 2:
        comp = b[20] & 0x0F; nblk = b[21] | ((b[20] & 0xF0) << 4); nsparse = b[22]
        h.update(compression={0: 'none', 1: 'zstd', 2: 'zlib'}.get(comp, f'unknown({comp})'),
                 blocks=nblk, sparse_ranges=nsparse, uuid=b[24:32].hex())
    else:
        h.update(compression='none', blocks=0, sparse_ranges=0)
    return h

def readme_table():
    rows = {}
    for line in open('animations/README.md', encoding='utf-8'):
        m = re.match(r'\|\s*(\d+)\s*\|\s*([a-z_]+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', line)
        if m:
            n, name, dur, loops, desc, mood = (x.strip() for x in m.groups())
            rows[name] = dict(n=int(n), duration=dur, loops=loops, description=desc, mood=mood)
    return rows

def title(name):
    return {'eye_of_sauron': 'Eye of Sauron'}.get(name, name.replace('_', ' ').title())

def main():
    regen = '--regen' in sys.argv
    meta = readme_table(); ok = True
    os.makedirs(f'{WEB}/sequences', exist_ok=True); os.makedirs(f'{WEB}/model', exist_ok=True)
    # pixel table
    rows = list(csv.DictReader(open('model/gazebo_pixels.csv')))
    npx = len(rows)
    for i, r in enumerate(rows):
        assert int(r['index']) == i + 1 and int(r['channel_start']) == 3 * i + 1, f'CSV row {i+1} channel order'
    xyz = np.array([[float(r['x_in']), float(r['y_in']), float(r['z_in'])] for r in rows])
    # g5.py (imported by xl_common) writes renders/ and model/*.obj on import: import it from a temp dir
    import io, contextlib, tempfile
    tmp = tempfile.mkdtemp(); os.makedirs(f'{tmp}/model'); shutil.copy('model/gazebo.xmodel', f'{tmp}/model/')
    os.chdir(tmp)
    with contextlib.redirect_stdout(io.StringIO()):
        import xl_common
        if regen: import xl_anim, xl_anim2
    os.chdir(ROOT); shutil.rmtree(tmp, ignore_errors=True)
    # every pixel must sit outside the wood, or it is hidden in the 3D preview (and would be in xLights 3D too)
    try:
        from scipy.spatial import Delaunay
        g5 = xl_common.g5; buried = {}
        for kind, polys in g5.G.items():
            k = 4 if kind == 'ring' else 6          # polys per solid (ring segments have no end caps)
            for i in range(0, len(polys), k):
                hull = Delaunay(np.array([p for q in polys[i:i + k] for p in q]))
                hit = np.where(hull.find_simplex(xl_common.XYZ) >= 0)[0]
                for h in hit: buried.setdefault(f'{xl_common.MEM[h]} in {kind}', 0); buried[f'{xl_common.MEM[h]} in {kind}'] += 1
        print('pixels inside wood:', buried or 'none'); ok &= not buried
    except ImportError:
        print('(scipy not installed: skipped the pixels-inside-wood check)')
    dxyz = np.abs(xyz - xl_common.XYZ).max()
    print(f'pixels: {npx} rows, {3*npx} channels; CSV vs xl_common.XYZ max |diff| = {dxyz:.4f} in')
    ok &= dxyz < 0.006
    shutil.copy('model/gazebo_pixels.csv', f'{WEB}/model/gazebo_pixels.csv')
    gens = {}
    if regen:
        gens = {**{n: (lambda n=n: xl_anim.frames(n)) for n in xl_anim.ANIMS},
                **{n: (lambda f=f: np.stack([f(k / 20) for k in range(400)])) for n, f in xl_anim2.ANIMS.items()}}
    shows = []
    for name in ORDER:
        src = f'sequences/{name}.fseq'; b = open(src, 'rb').read(); h = parse_header(b)
        size_ok = len(b) == h['data_offset'] + h['channels'] * h['frames']
        good = (h['version'] == '2.0' and h['compression'] == 'none' and h['channels'] == 3 * npx
                and h['step_ms'] == 50 and h['sparse_ranges'] == 0 and size_ok)
        data = np.frombuffer(b, np.uint8, offset=h['data_offset']).reshape(h['frames'], npx, 3)
        cmp = 'n/a'
        ref = None
        if regen and name in gens: ref = gens[name]()
        elif os.path.exists(f'build/anim_{name}.npy'): ref = np.load(f'build/anim_{name}.npy')
        if ref is not None:
            q = np.clip(np.round(ref * 255), 0, 255).astype(np.uint8)
            d = int(np.abs(q.astype(int) - data).max()); cmp = f'max|diff| vs generator = {d}'
            good &= d <= 1
        ok &= good
        print(f"{'OK ' if good else 'BAD'} {name:20s} v{h['version']} off={h['data_offset']} ch={h['channels']} "
              f"frames={h['frames']} step={h['step_ms']}ms comp={h['compression']} size_ok={size_ok} {cmp}")
        shutil.copy(src, f'{WEB}/sequences/{name}.fseq')
        m = meta.get(name, {})
        shows.append(dict(id=name, title=title(name), file=f'sequences/{name}.fseq', bytes=len(b),
                          frames=h['frames'], fps=round(1000 / h['step_ms']), channels=h['channels'],
                          seconds=h['frames'] * h['step_ms'] / 1000, loops=m.get('loops', ''),
                          description=m.get('description', ''), mood=m.get('mood', ''),
                          sha1=hashlib.sha1(b).hexdigest()[:12]))
    man = dict(model=dict(name='gazebo', pixels=npx, channels=3 * npx, csv='model/gazebo_pixels.csv',
                          units='inches', axes='x east, y north (entrance at -y), z up; origin = centre on ground'),
               shows=shows)
    json.dump(man, open(f'{WEB}/sequences/manifest.json', 'w'), indent=1)
    tot = sum(s['bytes'] for s in shows)
    print(f'wrote web/sequences/manifest.json: {len(shows)} shows, {tot/1e6:.1f} MB of .fseq')
    if not ok: sys.exit('verification FAILED')
    print('verification passed')

if __name__ == '__main__':
    main()
