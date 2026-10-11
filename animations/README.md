# Animation catalog
All animations are 20 fps, 4,575 channels (1,525 RGB pixels). "Loop" means the last frame flows into the first. Previews are in `../previews/<name>.gif` (5 s excerpt), sequences in `../sequences/<name>.fseq`.

| # | Name | Duration | Loops | Description | Mood / use |
|---|---|---|---|---|---|
| 1 | rainbow_chase | 10 s | yes (hue cycle) | Rainbow colors rotating around the gazebo by angle, with a slight height shift | Bright, party, general use |
| 2 | rafter_spiral | 10 s | mostly | A comet runs from each rafter's wall end toward the ring, staggered per rafter so it spirals; ring has a rotating tail; the 72" rails pulse; the rest dim blue | Dynamic, "vortex" |
| 3 | wipe_up | 10 s | cycles | A color wipes up the whole structure by height, then the next color | Welcome, transitions |
| 4 | twinkle | 10 s | yes | Random white / ice-blue / warm sparkles on a dim blue base | Festive, winter |
| 5 | breathing | 10 s | yes | Each member group breathes in its own color, phase-offset | Relaxed, ambient |
| 6 | fire | 10 s | no | Fire effect rising up each post, glowing embers on the rest, warm ring | Cozy, Halloween-ish |
| 7 | christmas | 10 s | yes | Red/green alternating, swapping every 0.5 s with white sparkles | Christmas |
| 8 | candlelight_dinner | 20 s | yes | Warm amber (~2200 K) glow, independent gentle flicker, brighter posts, dim overall | Dinner, romantic, calm |
| 9 | starry_night | 20 s | yes | Deep blue base, slow white/pale-blue twinkles, three shooting stars running up rafters into the ring (at 3 s, 9.5 s, 15 s) | Calm, evening |
| 10 | slow_ember_glow | 20 s | yes | Warm-white breathing wave (10 s) rising from posts to ring | Very calm, ambient |
| 11 | aurora | 20 s | yes | Drifting green / teal / purple waves around by angle and height | Calm, magical |
| 12 | golden_hour | 20 s | yes | Slow gradient shift amber to rose to soft violet and back, with a small height offset | Sunset, relaxed |
| 13 | eye_of_sauron | 20 s | yes | Ring is a yellow-white slit pupil with orange-red glow; rafters are red-orange flames fading outward; walls are dim pulsing red embers; a bright beam sweeps around the rafters at 2 s and 12 s | Themed, Halloween, party trick |
| 14 | lantern_fireflies | 20 s | yes | 16 warm-yellow fireflies drift around the structure and blink slowly | Summer evening, calm |

Combined files: `gazebo_all.fseq` = animations 1-7 (70 s), `gazebo_calm.fseq` = animations 8-14 (140 s).

## Ideas backlog
1. Halloween: orange/purple chase with random green "lightning" flashes and a slow pumpkin pulse
2. Halloween ghost: pale-white wisps drifting up the posts
3. July 4th: red/white/blue chase with firework bursts from the ring outward along rafters
4. Ocean waves: blue-green waves rolling up and down the posts with white foam crests
5. Lightning storm: dark blue-grey base, random white flashes branching down the rafters
6. Snowfall: white dots falling down the posts, drifting in from the ring
7. Heartbeat: red double-pulse from the ring out along rafters, then down the posts
8. Sunrise/sunset: slow gradient from deep blue to orange to bright warm white, rising from the posts
9. Hanukkah: blue/white alternating with a 9-candle count-up
10. Valentine: pink/red heart-pulse and slow rose wipe
11. Disco / beat-reactive: color per member changing with music (FPP audio sync)
12. Matrix rain: green streaks falling down the posts
13. Police / emergency: red-blue alternating, rotating by angle
14. Thanksgiving / autumn leaves: orange/red/brown fall with slow drifting sparks
15. Spring blossom: pink/white twinkles with soft green wash
16. Plasma / lava lamp: slow blobs of color drifting by 3D position
17. Clock / countdown: a New Year's countdown sweep around the ring, finale burst
18. Pulse by position: use the 3D coordinates for a sphere expanding from the center outward
19. Rain: blue drops sliding down the posts and rails
20. Birthday: confetti sparkles in random colors with a slow rainbow base
