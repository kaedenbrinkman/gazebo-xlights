// FSEQ (Falcon Player sequence) parser for the browser.
// Supports v1 (uncompressed) and v2 with compression none / zstd (via vendored fzstd) / zlib
// (via the built-in DecompressionStream), sparse channel ranges and variable headers.
import { decompress as zstdDecompress } from '../vendor/fzstd/index.mjs';

export class FseqError extends Error {}

const COMP = { 0: 'none', 1: 'zstd', 2: 'zlib' };

async function inflateZlib(bytes) {
  if (typeof DecompressionStream === 'undefined')
    throw new FseqError('This browser has no DecompressionStream, so zlib-compressed .fseq cannot be read. Re-export uncompressed or zstd.');
  const ds = new DecompressionStream('deflate'); // zlib-wrapped deflate, as written by xLights/FPP
  const out = new Response(new Blob([bytes]).stream().pipeThrough(ds));
  return new Uint8Array(await out.arrayBuffer());
}

/** Parse the header only (cheap). */
export function parseFseqHeader(buffer) {
  const b = new Uint8Array(buffer);
  const dv = new DataView(buffer);
  if (b.length < 28) throw new FseqError('File too small to be an .fseq (' + b.length + ' bytes).');
  const magic = String.fromCharCode(b[0], b[1], b[2], b[3]);
  if (magic !== 'PSEQ' && magic !== 'FSEQ' && magic !== 'V1FS')
    throw new FseqError(`Not an FSEQ file (magic "${magic}", expected "PSEQ").`);
  const h = {
    magic,
    dataOffset: dv.getUint16(4, true),
    minor: b[6], major: b[7],
    headerLen: dv.getUint16(8, true),
    channels: dv.getUint32(10, true),
    frames: dv.getUint32(14, true),
  };
  h.version = `${h.major}.${h.minor}`;
  let pos;
  if (h.major === 1) {
    h.stepMs = dv.getUint16(18, true);
    h.compression = 'none'; h.compressionId = 0; h.blocks = []; h.sparse = [];
    h.uuid = '';
    pos = h.headerLen || 28;
  } else if (h.major === 2) {
    h.stepMs = b[18];
    h.flags = b[19];
    h.compressionId = b[20] & 0x0f;
    h.compression = COMP[h.compressionId] || `unknown (${h.compressionId})`;
    const nBlocks = b[21] | ((b[20] & 0xf0) << 4);
    const nSparse = b[22];
    h.uuid = Array.from(b.slice(24, 32), (x) => x.toString(16).padStart(2, '0')).join('');
    pos = 32;
    h.blocks = [];
    for (let i = 0; i < nBlocks; i++, pos += 8)
      h.blocks.push({ frame: dv.getUint32(pos, true), length: dv.getUint32(pos + 4, true) });
    h.sparse = [];
    for (let i = 0; i < nSparse; i++, pos += 6)
      h.sparse.push({
        start: b[pos] | (b[pos + 1] << 8) | (b[pos + 2] << 16),
        count: b[pos + 3] | (b[pos + 4] << 8) | (b[pos + 5] << 16),
      });
  } else {
    throw new FseqError(`Unsupported FSEQ major version ${h.major}.`);
  }
  // variable headers (e.g. "mf" media file, "sp" sequence producer)
  h.vars = {};
  while (pos + 4 <= h.dataOffset) {
    const len = dv.getUint16(pos, true);
    if (len < 4 || pos + len > h.dataOffset) break;
    const code = String.fromCharCode(b[pos + 2], b[pos + 3]);
    let s = new TextDecoder().decode(b.subarray(pos + 4, pos + len));
    h.vars[code] = s.replace(/\0+$/, '');
    pos += len;
  }
  if (!h.stepMs) throw new FseqError('Header step time is 0 ms.');
  h.fps = 1000 / h.stepMs;
  h.seconds = (h.frames * h.stepMs) / 1000;
  return h;
}

/** Parse a whole file: returns { header, data } where data is frames x channels (stored channels) bytes. */
export async function parseFseq(buffer) {
  const h = parseFseqHeader(buffer);
  const b = new Uint8Array(buffer);
  const need = h.frames * h.channels;
  if (h.dataOffset > b.length) throw new FseqError('Data offset is past the end of the file.');
  let data;
  if (h.compressionId === 0) {
    if (b.length - h.dataOffset < need)
      throw new FseqError(`File is truncated: ${h.frames} frames x ${h.channels} channels needs ${need} bytes, found ${b.length - h.dataOffset}.`);
    data = b.subarray(h.dataOffset, h.dataOffset + need);
  } else if (h.compressionId === 1 || h.compressionId === 2) {
    data = new Uint8Array(need);
    let src = h.dataOffset, dst = 0;
    const blocks = h.blocks.filter((x) => x.length > 0);
    if (!blocks.length) blocks.push({ frame: 0, length: b.length - h.dataOffset });
    for (const blk of blocks) {
      if (src + blk.length > b.length) throw new FseqError('Compressed block runs past the end of the file.');
      const comp = b.subarray(src, src + blk.length);
      src += blk.length;
      let out;
      try {
        out = h.compressionId === 1 ? zstdDecompress(comp) : await inflateZlib(comp);
      } catch (e) {
        if (e instanceof FseqError) throw e;
        throw new FseqError(`Could not decompress ${h.compression} block at frame ${blk.frame}: ${e.message || e}`);
      }
      const at = blk.frame * h.channels; // blocks start on frame boundaries
      const n = Math.min(out.length, need - at);
      if (n > 0) data.set(out.subarray(0, n), at);
      dst = Math.max(dst, at + n);
    }
    if (dst < need) h.warning = `Only ${Math.floor(dst / h.channels)} of ${h.frames} frames decoded.`;
  } else {
    throw new FseqError(`Unsupported compression "${h.compression}". Re-export from xLights as uncompressed or zstd FSEQ v2.`);
  }
  return { header: h, data };
}

/**
 * Build a lookup from model channel slots (pixel i, colour c -> slot 3*i+c) to stored-channel
 * indices in the file. channelStarts: 1-based start channel per pixel (from the CSV).
 * startChannel: 1-based absolute channel where the model starts in the file.
 * Returns { map: Int32Array (-1 = channel not in file), contiguous: bool, offset, missing }.
 */
export function buildChannelMap(header, channelStarts, startChannel = 1) {
  const n = channelStarts.length * 3;
  const map = new Int32Array(n).fill(-1);
  // absolute 0-based channel -> stored index
  let lookup;
  if (header.sparse && header.sparse.length) {
    const ranges = []; let acc = 0;
    for (const r of header.sparse) { ranges.push([r.start, r.count, acc]); acc += r.count; }
    lookup = (abs) => { for (const [s, c, a] of ranges) if (abs >= s && abs < s + c) return a + abs - s; return -1; };
  } else {
    lookup = (abs) => (abs >= 0 && abs < header.channels ? abs : -1);
  }
  let missing = 0;
  for (let i = 0; i < channelStarts.length; i++)
    for (let c = 0; c < 3; c++) {
      const abs = startChannel - 1 + channelStarts[i] - 1 + c;
      const k = lookup(abs);
      map[3 * i + c] = k; if (k < 0) missing++;
    }
  let contiguous = missing === 0;
  for (let k = 1; contiguous && k < n; k++) if (map[k] !== map[0] + k) contiguous = false;
  return { map, contiguous, offset: map[0], missing };
}

/** Absolute channel extent covered by the file (for sparse files, the highest range end). */
export function channelExtent(header) {
  if (header.sparse && header.sparse.length) return Math.max(...header.sparse.map((r) => r.start + r.count));
  return header.channels;
}
