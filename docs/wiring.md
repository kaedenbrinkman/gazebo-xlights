# Wiring (Kulp K16A-B running FPP)

![wiring diagram](wiring_diagram.png)

**Untested plan.** Totals: **1,525 pixels in 48 strings**, 4,575 channels. No pixels on braces or top joists.

## Strings
| Item | Strings | Pixels |
|---|---|---|
| Post + rafter unit (x12) | 1 x 50 + 1 x 25 each | 75 each = 900 |
| 36" rails (faces 2-12, none on entrance) | 11 x 25 | 275 |
| 72" rails (faces 1-12) | 12 x 25 | 300 |
| Ring | 1 x 50 | 50 |
| **Total** | **48 strings** (24 + 11 + 12 + 1) | **1,525** |

A post+rafter unit: the 50-px string goes up the post (35 px at 2", bottom 1" to 69") and continues 15 px along the rafter; the 25-px string finishes the rafter (25 px) to the ring. That is 35 post + 40 rafter = 75 px. The rafter is about 84", so 40 px at 2" covers about 80". (An earlier model had 41 rafter pixels = 76 per unit; the model is now regenerated at 75.)

## Ports
| Port | Chain order | Pixels |
|---|---|---|
| 1 | Unit 1 (A50, B25) -> unit 2 -> unit 3 -> unit 4 (posts 1-4) | 300 |
| 2 | Units 5-8 (posts 5-8) | 300 |
| 3 | Units 9-12 (posts 9-12) | 300 |
| 4 | 36" rails faces 2-12 (11 x 25), then the ring (50) | 325 |
| 5 | 72" rails faces 1-12 (12 x 25) | 300 |

Posts are numbered 1-12 counterclockwise from the entrance; the entrance face is between posts 1 and 2. The ring is on port 4 after the rails (325 px); if you want every port at 300 or less, move the ring to its own port 6. Port 4 jumpers from the last 36" rail (face 12) up to the ring. The K16A-B has more ports than this uses; check its current spec for per-port limits.

Node order in the xLights model follows this chain exactly (nodes 1-900 units, 901-1175 36" rails, 1176-1225 ring, 1226-1525 72" rails), so each port is one contiguous channel range.

## Mounting: 2" pitch strips
Pixels plug into mounting strips (flat bar, PVC or wood) with holes drilled at 2" centres, fixed on the inward-facing side of each post, rail and rafter, so every bulb faces the interior. The strips only hold the pitch; wiring stays a normal daisy chain. The hole size depends on your pixels (for example 12 mm bullet nodes). The strip stock and hole size are assumptions to confirm against your hardware.

## Power
Assumed 5 V pixels (check yours). Inject power at the start of every port and at the 50 -> 25 string joint of each post/rafter unit (the diagram marks both). 12 V pixels need much less injection. Share ground with the controller.

## Number checks
- 12 x 75 = 900, + 275 + 300 + 50 = **1,525**.
- An earlier request quoted "~2075" and, later, "1,825" (with 12 joist strings); with the joists dropped the sum is 1,525. The 48-string count is my arithmetic (24 + 11 + 12 + 1); a quoted "61 strings" does not match this layout.
