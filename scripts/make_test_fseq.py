#!/usr/bin/env python3
"""Write FSEQ variants of a show to exercise the web player's parser (not used by the site itself).

  python3 scripts/make_test_fseq.py [show] [outdir]     (needs: pip install zstandard)

Outputs <outdir>/<show>_zstd.fseq (v2, zstd, multi-block like xLights), _zlib.fseq, _sparse.fseq
(gazebo at start channel 1001 of a sparse 2-range file), _v1.fseq, _bigger.fseq (gazebo at channel 1
of a 6000-channel file) and _short.fseq (wrong channel count -> must be rejected).
"""
import os, struct, sys, zlib
import numpy as np

def header_v2(ch, nf, step, comp, blocks, sparse, var=b''):
    idx = b''.join(struct.pack('<II', f, l) for f, l in blocks)
    sp = b''.join(struct.pack('<I', s)[:3] + struct.pack('<I', c)[:3] for s, c in sparse)
    off = 32 + len(idx) + len(sp) + len(var)
    off = (off + 3) // 4 * 4
    nb = len(blocks)
    h = struct.pack('<4sHBBHIIBBBBBB8s', b'PSEQ', off, 0, 2, 32, ch, nf, step, 0,
                    (comp & 0x0F) | ((nb >> 4) & 0xF0), nb & 0xFF, len(sparse), 0, b'testfseq')
    return (h + idx + sp + var).ljust(off, b'\0')

def var_header(code, text):
    d = text.encode() + b'\0'
    return struct.pack('<H', 4 + len(d)) + code.encode() + d

def compressed(frames, comp, step, sparse=()):
    nf, ch = frames.shape
    # xLights writes a small first block (fast start) then larger ones
    bounds = [0, min(10, nf)] + list(range(min(10, nf) + 64, nf, 64)) + [nf]
    bounds = sorted(set(bounds))
    chunks, blocks = [], []
    for a, b in zip(bounds[:-1], bounds[1:]):
        raw = frames[a:b].tobytes()
        if comp == 1:
            import zstandard
            c = zstandard.ZstdCompressor(level=10).compress(raw)
        else:
            c = zlib.compress(raw, 6)
        chunks.append(c); blocks.append((a, len(c)))
    var = var_header('sp', 'gazebo-xlights make_test_fseq.py')
    return header_v2(ch, nf, step, comp, blocks, sparse, var) + b''.join(chunks)

def main():
    show = sys.argv[1] if len(sys.argv) > 1 else 'aurora'
    out = sys.argv[2] if len(sys.argv) > 2 else 'build/test_fseq'
    os.makedirs(out, exist_ok=True)
    b = open(f'sequences/{show}.fseq', 'rb').read()
    off, = struct.unpack_from('<H', b, 4); ch, nf = struct.unpack_from('<II', b, 10); step = b[18]
    fr = np.frombuffer(b, np.uint8, offset=off).reshape(nf, ch)
    w = lambda n, d: (open(f'{out}/{show}_{n}.fseq', 'wb').write(d), print(f'{out}/{show}_{n}.fseq', len(d)))
    w('zstd', compressed(fr, 1, step))
    w('zlib', compressed(fr, 2, step))
    # sparse: other model at channels 1..300 (zeros), gazebo at absolute channel 1001 (0-based 1000)
    other = np.zeros((nf, 300), np.uint8)
    w('sparse', compressed(np.concatenate([other, fr], 1), 1, step, sparse=[(0, 300), (1000, ch)]))
    v1 = struct.pack('<4sHBBHIIHHHBBH', b'PSEQ', 28, 0, 1, 28, ch, nf, step, 0, 0, 1, 0, 0)
    w('v1', v1 + fr.tobytes())
    big = np.zeros((nf, 6000), np.uint8); big[:, :ch] = fr
    w('bigger', header_v2(6000, nf, step, 0, [], []) + big.tobytes())
    w('short', header_v2(1500, 20, step, 0, [], []) + fr[:20, :1500].tobytes())

if __name__ == '__main__':
    main()
