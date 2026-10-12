# Gazebo xLights: web preview

A static Three.js site that shows the 12-sided gazebo at night with its 1,525 pixels and plays the real
xLights/FPP `.fseq` shows in the browser. It needs no server code, build step or CDN: Three.js and the zstd
decoder are vendored, and every URL is relative, so it works from any static host, including
`https://<user>.github.io/gazebo-xlights/` or from `https://kaedenb.org/gazebo-xlights/`.

## Run locally
```bash
cd web && python3 -m http.server 8000      # then open http://localhost:8000/
```
(Opening `index.html` straight from disk with `file://` does not work, because browsers block `fetch()` and ES modules there.)

URL parameters (handy for links and screenshots): `?show=aurora&cam=inside&mode=wood&t=6&paused=1&orbit=1`.
`cam` is `outside`, `inside`, `entrance` or `top`.

## What is in here
| Path | What |
|---|---|
| `index.html`, `css/style.css` | UI: sidebar (shows, transport, brightness/speed/glow, camera presets, auto-rotate, night / wood-lit), loading screen, drag-and-drop overlay. Collapses to a bottom sheet on phones. |
| `js/main.js` | Scene (sky, stars, moon, fog, grass, pavers, wood), pixel renderer (additive sprite shader + UnrealBloom), playback loop, file loading. |
| `js/gazebo.js` | Framing geometry ported from `scripts/g5.py` (posts, 36"/72" rails, top joists, upper/lower braces, rafters, ring). |
| `js/fseq.js` | FSEQ parser: v1, v2 uncompressed / zstd / zlib, multi-block, sparse ranges, variable headers (`mf`, `sp`). |
| `js/textures.js` | Procedural canvas textures (wood, grass, concrete, moon). No image downloads. |
| `sequences/*.fseq` | The 14 shows, byte-for-byte copies of `../sequences/<name>.fseq`. |
| `sequences/manifest.json` | Show list: id, title, file, frames, fps, channels, description and mood (from `animations/README.md`). |
| `model/gazebo_pixels.csv` | Copy of `../model/gazebo_pixels.csv`. Row order and `channel_start` define the channel to pixel mapping. |
| `vendor/three/` | three.js r186 (`build/three.module.js` + `three.core.js`) and the `examples/jsm` modules used. MIT. |
| `vendor/fzstd/` | fzstd 0.1.1, a pure-JS Zstandard decoder (MIT), for zstd `.fseq` files from xLights. |

Total size is about 21 MB, of which 19.2 MB is the 14 `.fseq` files. Only the selected show is downloaded (0.9 or 1.8 MB),
plus about 2.4 MB of code on first load. The next show in the list is prefetched.

## Updating the site
```bash
python3 scripts/build_web_assets.py          # copy .fseq + CSV into web/, write manifest.json, verify
python3 scripts/build_web_assets.py --regen  # same, but also regenerate every frame from scripts/xl_anim*.py and compare
scripts/vendor_web_deps.sh [three-version]   # re-vendor three.js + fzstd via `npm pack`
python3 scripts/make_test_fseq.py aurora     # zstd/zlib/sparse/v1/oversized/short test files in build/test_fseq/
```
`build_web_assets.py` checks every header (`PSEQ`, v2.0, data offset 32, 4,575 channels, 200 or 400 frames, 50 ms, no
compression, no sparse ranges, exact file size), checks that the CSV `channel_start` is `3*(index-1)+1` and that the CSV
coordinates match `xl_common.XYZ`, and compares every frame byte with the generator output (max difference 0 for all 14 shows).

## Playing your own xLights sequence
Use **Load .fseq** or drop a file anywhere on the page. The file is parsed locally; nothing is uploaded.
- Supported: FSEQ v1, v2 uncompressed, v2 **zstd** (the xLights default) and v2 **zlib**, any number of compression blocks,
  sparse channel ranges, any frame time (it uses the file's step time, not a fixed 20 fps).
- Channel layout: pixel *n* = CSV row *n*, RGB at `channel_start .. +2` (1-based, relative to the model start). The gazebo needs 4,575 channels.
  - Exactly 4,575 channels: it plays.
  - More channels (a whole show): it plays channels 1-4,575 and shows a **Start ch** box so you can move the gazebo to its real start
    channel. For sparse files it picks the first sparse range big enough to hold the gazebo.
  - Fewer channels, or a start channel that runs past the end: it shows a clear "Channel count mismatch" error and keeps playing the current show.
- Unknown compression types, truncated files and bad magic are reported in the panel.
- Colour order is assumed RGB (as in `model/gazebo.xmodel`). Gamma is a fixed display curve (1.6), not the controller's.

## Deploying to kaedenb.org/gazebo-xlights
`.github/workflows/pages.yml` uploads `web/` as the Pages artifact and deploys it on every push to `main` that touches
`web/**` (or the workflow file), and on manual runs (**Actions > Deploy web preview to GitHub Pages > Run workflow**).
It uses `actions/configure-pages`, `actions/upload-pages-artifact` (path `web`) and `actions/deploy-pages` with
`pages: write` and `id-token: write`.

One-time setup:
1. Push this repo to GitHub as **`kaedenbrinkman/gazebo-xlights`** (that is the configured `origin`).
2. In the repo: **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. Push to `main` (or run the workflow by hand).

Why the URL is `kaedenb.org/gazebo-xlights/`: `https://kaedenbrinkman.github.io/` currently redirects (301) to
`https://kaedenb.org/` and kaedenb.org is served by GitHub Pages (`server: GitHub.com`). So kaedenb.org is the custom
domain of the account's **user site**. Project sites of the same account are then served under that domain at
`/<repo-name>/` automatically. With the repo named `gazebo-xlights` the site appears at
`https://kaedenb.org/gazebo-xlights/` with no DNS or CNAME change, and **do not** set a custom domain on this repo
(that would move it off the subpath). Because all paths are relative, the same build also works at any other subpath.

Assumptions and caveats:
- The repo appears to be **private** (the GitHub API returns 404 without auth). Pages for private repos needs a paid plan
  (GitHub Pro, Team or Enterprise). On GitHub Free, make the repo public or Pages will not be available. With Pro, a Pages site
  from a private repo is still **publicly visible** (access control for Pages needs Enterprise Cloud).
- If kaedenb.org is not the user-site custom domain (for example it is served by a different account, or a separate org),
  the site will be at `https://kaedenbrinkman.github.io/gazebo-xlights/` instead. Check under Settings > Pages after the first deploy.
- `/gazebo-xlights` without the trailing slash is redirected to `/gazebo-xlights/` by GitHub Pages. Relative URLs need the slash.
- GitHub Pages limits: 1 GB site, 100 GB/month soft bandwidth. The site is about 21 MB.
- `.fseq` is served as `application/octet-stream` and probably not compressed in transit. Fine at 0.9-1.8 MB per show.

## Rendering notes
- Units: CSV and `g5.py` use inches, origin at the centre on the ground, +z up, entrance face (posts 1-2) at -y.
  Scene units are metres with Y up: `(X, Y, Z) = (x, z, -y) * 0.0254`, so the entrance faces +Z. The whole gazebo sits 1" up, on the pavers.
- Pavers: 16" x 16" x 2" concrete slabs under each post, aligned radially, set 1" proud of the grass (assumed).
- Pixels face inward: each sprite is dimmed (down to 14%) when you see it from behind. Posts and rails face the centre axis; rafter
  pixels face down and in; ring pixels face down.
- All pixel positions come straight from the CSV. `scripts/build_web_assets.py` checks that no pixel is inside the wood
  (an earlier model had the 72" rail pixels inside the top joists and the ring pixels inside the ring, so they were hidden).
- Wood and grass are lit by 13 coloured point lights that follow the average colour of nearby pixels (12 wall sectors + the roof),
  an approximation of real spill light.
- "Wood lit" adds warm floodlights so you can see the framing. "Night" is moonlight only.
