#!/usr/bin/env bash
# Vendor Three.js (core + the examples/jsm modules the site uses) and fzstd into web/vendor
# so the site works offline and under any subpath. Usage: scripts/vendor_three.sh [version]
set -euo pipefail
VER="${1:-0.186.1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
( cd "$TMP" && npm pack "three@$VER" >/dev/null && tar xzf three-*.tgz )
PKG="$TMP/package"; OUT="$ROOT/web/vendor/three"
rm -rf "$OUT"; mkdir -p "$OUT/build" "$OUT/examples/jsm"
cp "$PKG/build/three.module.js" "$PKG/build/three.core.js" "$OUT/build/"
cp "$PKG/LICENSE" "$OUT/LICENSE"
# copy entry modules + their relative imports, recursively
ENTRIES="controls/OrbitControls.js postprocessing/EffectComposer.js postprocessing/RenderPass.js postprocessing/UnrealBloomPass.js postprocessing/OutputPass.js"
python3 - "$PKG/examples/jsm" "$OUT/examples/jsm" $ENTRIES <<'PY'
import sys,re,os,shutil
src,dst,*todo=sys.argv[1:];seen=set()
while todo:
    rel=os.path.normpath(todo.pop())
    if rel in seen: continue
    seen.add(rel);os.makedirs(os.path.dirname(os.path.join(dst,rel)),exist_ok=True)
    shutil.copy(os.path.join(src,rel),os.path.join(dst,rel))
    for m in re.findall(r"""from\s+['"](\.[^'"]+)['"]""",open(os.path.join(src,rel)).read()):
        todo.append(os.path.join(os.path.dirname(rel),m))
print('vendored',sorted(seen))
PY
echo "three@$VER" > "$OUT/VERSION"

# fzstd (pure-JS Zstandard decoder, MIT) for zstd-compressed .fseq files exported by xLights
FZ="${FZSTD_VERSION:-0.1.1}"; mkdir -p "$TMP/fz"
( cd "$TMP/fz" && npm pack "fzstd@$FZ" >/dev/null && tar xzf fzstd-*.tgz )
mkdir -p "$ROOT/web/vendor/fzstd"
cp "$TMP/fz/package/esm/index.mjs" "$ROOT/web/vendor/fzstd/index.mjs"
cp "$TMP/fz/package/LICENSE" "$ROOT/web/vendor/fzstd/LICENSE"
echo "fzstd@$FZ" > "$ROOT/web/vendor/fzstd/VERSION"
