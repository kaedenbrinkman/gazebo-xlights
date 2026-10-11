# Philips Hue / smart-home integration (untested plan)

Goal: control the gazebo from Hue-style apps, Home Assistant, or scenes (on/off, brightness, colour, "start the candlelight animation"). **None of this was built or tested.** Check each tool's current docs before relying on any detail below.

## What FPP offers
- FPP has a REST API (under `/api/...`) for starting/stopping playlists and sequences, changing volume/settings, and running FPP "commands".
- FPP supports Pixel Overlay Models (generated from xLights models) that can be filled with a colour, a state (on/off/transparent), or text from outside the sequencer, e.g. over the API. This lets another system set a solid colour or brightness while no sequence is playing, or over one.
- FPP can also publish status and receive commands via MQTT (built in or via plugin; check your FPP version).

## Option A: Home Assistant + FPP (recommended starting point)
1. Run Home Assistant on any always-on box.
2. Add FPP to Home Assistant. Either use a community FPP integration if one exists for your version, or use `rest_command` / `shell_command` entries that call the FPP API (start playlist X, stop gracefully, set overlay model colour).
3. Expose each animation as a script or scene in Home Assistant ("Candlelight", "Starry", "Eye", etc.) that starts the matching FPP playlist.
4. Add a light entity (template light) for the gazebo: on/off starts or stops the playlist; brightness maps to the FPP overlay brightness or the model/controller brightness; colour sets an overlay model fill colour (solid colour mode).
5. Expose to Hue-style apps with Home Assistant's Hue emulation or HomeKit/Alexa/Google bridges if you want voice control.
Pros: simple, stays on your network, scriptable, schedules/sunset triggers. Cons: colour/brightness control is solid-colour only and needs an overlay model set up in FPP.

## Option B: diyHue (Hue bridge emulation) bridging to FPP
1. Run diyHue on your network so Hue apps see an emulated bridge.
2. Add a custom light in diyHue that forwards on/off/brightness/colour changes to a small script (or MQTT topic) that calls the FPP REST API or sets the overlay model.
3. Optionally map Hue scenes to FPP playlists (scene "Aurora" starts the aurora sequence).
Pros: appears natively in Hue apps. Cons: more moving parts; diyHue's custom-light support and the exact way to call a script must be verified, and it needs a small bridge service you write and maintain. Colour sync with real Hue bulbs works only if the animation is also fed to them (not planned).

## Option C: MQTT only
FPP and Home Assistant (or diyHue, Node-RED) share an MQTT broker. A Home Assistant or Node-RED flow translates light commands and scene selection to FPP MQTT commands. Useful if you want state feedback ("currently playing X").

## Things to verify before building
- Your FPP version's overlay model and REST endpoint names.
- That overlay models are exported from xLights (the xLights "upload models" step) after this model is imported and its controller ports set.
- How FPP mixes an overlay with a running sequence (overlay modes: full-opaque, transparent, transparent-RGB).
- Brightness control: FPP-level (setting) versus controller-level versus per-model.
- Latency and reliability if scenes switch playlists often.

## Matching to real Hue lights
If you want Hue bulbs to match the animation (e.g. the "candlelight" scene), the usual route is to send scene names to both systems from Home Assistant with the same trigger. Syncing frame-by-frame is not planned.
