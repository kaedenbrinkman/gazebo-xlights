# Wiring (original plan; Kulp controller running FPP, 12 V pixels)

![wiring diagram](wiring_diagram.png)

**Untested plan.** 1,525 pixels in 48 strings, 4,575 channels. No pixels on braces or top joists. Regenerate the diagram with `python scripts/wiring_diagram.py` from the repo root.

> **Superseded for ports, power and controller:** the current plan is [physical_layout_v4.md](physical_layout_v4.md) (4-line plan, Kulp K4); before that [physical_layout_v3.md](physical_layout_v3.md): a Kulp **K4-PB** with 4 ports, data + GND only on the ports, the 12 V trunk from a ground box, and 0.06 A/px worst case. The model node order now follows v4, not the table below.

## Strings
| Item | Strings | Pixels |
|---|---|---|
| Post + rafter unit (x12) | 1 x 50 (string A) + 1 x 25 (string B) | 75 each = 900 |
| 36" rails (faces 2-12, none on the entrance face) | 11 x 25 | 275 |
| 72" rails (faces 1-12) | 12 x 25 | 300 |
| Ring | 1 x 50 | 50 |
| **Total** | **48 strings** (24 + 11 + 12 + 1) | **1,525** |

One unit: string A (50 px) goes up the post (35 px, 1" to 69") and continues 15 px along the rafter; a connector joins string B (25 px), which finishes the rafter (~84", 40 px total) to the ring. Posts are numbered 1-12 counterclockwise from the entrance; in this original plan the entrance face is between posts 1 and 2 (v4 renumbers it as face 12, posts 12-1).

## Ports, chains and power
| Port | Chain | Pixels | Est. current | Suggested supply |
|---|---|---|---|---|
| 1 | Units 1, 2, [12 V], 3, 4 | 300 | 12 A | 12 V 15 A + fuse |
| 2 | Units 5, 6, [12 V], 7, 8 | 300 | 12 A | 12 V 15 A + fuse |
| 3 | Units 9, 10, [12 V], 11, 12 | 300 | 12 A | 12 V 15 A + fuse |
| 4 | 36" rails (11 x 25), then ring (50) | 325 | 13 A | 12 V 20 A + fuse |
| 5 | 72" rails (12 x 25) | 300 | 12 A | 12 V 15 A + fuse |
| **Total** | | **1,525** | **~61 A** | |

- **Current is an estimate:** 0.04 A per pixel at full white, 12 V, pending the pixel datasheet. Typical sequences draw much less than full white.
- **Injection:** 12 V (V+ and GND) injected at the start of every port, and mid-chain on ports 1-3 between units 2 and 3 (about 6 A per feed on those ports). Ports 4 and 5 carry 12-13 A from one feed: use heavy wire (e.g. 14 AWG) or add a mid-chain injection (not drawn).
- **Supplies (options):** (a) one supply per port as above, each fused; or (b) two or three 12 V 30 A supplies (a 2 x 30 A pair has about 1 A of headroom at the full-white estimate, so 3 x 30 A is safer) feeding a fused distribution block. Tie all grounds together and to the controller.
- **Data:** each port's data runs base to ring within a unit, then a data jumper from the unit's ring end to the next unit's post base. Alternative (not modeled): alternate unit direction so ring ends meet at the ring; that needs the xLights node order reversed for those units.
- *(Original plan; the model no longer uses this order and now follows physical_layout_v4.md.)* The node order followed this chain (nodes 1-900 units, 901-1175 36" rails, 1176-1225 ring, 1226-1525 72" rails), so every port was one contiguous channel range. The controller in this original plan was a K16A-B (replaced by a 4-port Kulp K4 in v3/v4); check the spec for per-port limits and whether it accepts 12 V directly for its own power.

## Mounting: 2" pitch strips
Pixels plug into mounting strips (flat bar, PVC or wood) with holes at 2" centres, fixed on the inward-facing side of each post, rail and rafter, so every bulb faces the interior. The strips only hold the pitch; wiring stays a normal daisy chain. Strip stock and hole size depend on the pixels used; confirm against the hardware.

## Number checks
12 x 75 = 900, + 275 + 300 + 50 = 1,525. 1,525 x 0.04 A = 61 A. The string count is 24 + 11 + 12 + 1 = 48.
