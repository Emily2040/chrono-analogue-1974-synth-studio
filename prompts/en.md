# Chrono Analogue // System 1974: Distilled Single-Shot Master Prompt (English)

[English](en.md) · [简体中文](zh-CN.md) · [日本語](ja.md) · [한국어](ko.md) · [Original Initial Brief](original-brief.en.txt)

This file holds the distilled single-shot prompt.

Copy it to build the studio. It produces the playable **Chrono Analogue // System 1974** 3D modular analogue synthesiser, direct-drive 180g vinyl turntable studio, and 2-minute `1920×1080` (`60.0 fps`) four-symphony showcase video with **Gemini 4 Argon** in Google Antigravity.

## How This Prompt Was Distilled From Five Iterative Stages

The prompt below folds all five engineering and visual-critique stages directly into its initial requirements:

1. **Stage 1 (Pipeline Calibration & Shared Schema Records)**: Proved headless Blender 5.2 (`bpy`) to `calibration_knob.glb` to Three.js picking and Web Audio synthesis first, governed by `contract.json` (`0.1 m` source unit, `0.8 m` rack width, `15°` backward faceplate tilt, 16 knobs, 12 sockets, 25 hinged keys `C3–C5`), `world.json` (64 stable entities), and `progress.json`.
2. **Stage 2 (HUD Layout, Keybed Sculpting & Architectural Framing)**: Eliminated top-bar text collisions with a clean hardware console bar, replaced flat boxes with 25 bevelled waterfall/chamfered keys resting against a crimson felt rail, and added a studio console desk and walnut acoustic slat wall so no camera angle sees empty background void.
3. **Stage 3 (16-Map PBR Pipeline & Zero-Blur 60 FPS Console UI)**: Replaced slow CSS `backdrop-filter: blur()` panels with a zero-blur brushed black-bronze hardware rack skin (`ui_hardware_console_skin.png`) to lock frame rates at `60.1 FPS`. Upgraded all studio materials with 16 matched `2048×2048` albedo, normal, roughness, metalness, and bump maps (`scripts/prepare_textures.py`).
4. **Stage 4 (Dark-Room Studio PMREM Lighting, Luthier Wood UVs & Inter-Row Cable Corridor)**: Replaced Three.js's white-ceiling `RoomEnvironment()` (which washed horizontal vinyl and desk surfaces into pale grey) with a custom dark-ceiling (`#050507`) 1974 studio softbox PMREM environment. Mapped wood UVs along the longest axis of every board (`align_luthier_wood_uvs`), built a 240-segment 2-track strobe platter with an orange prism tower and slotted headshell, and routed cross-bay patch cables through the horizontal inter-row corridor with coaxial plug stacking.
5. **Stage 5 (2-Minute 1080p60 Four-Symphony Social Media Showcase)**: Added a deterministic 48 kHz stereo polyphonic ladder-synth and vinyl audio engine (`scripts/showcase_choreography.py`) and a frame-stepped headless Chrome WebGL2-to-FFmpeg renderer (`scripts/render_social_showcase_1080p60.py`) to produce `showcase-1080p60.mp4` (`7,200` frames, `120.00 s`).

---

## Copy-Pasteable Single-Shot Master Prompt

Copy the complete block below into a **Gemini 4 Argon** session in Google Antigravity:

```text
Build a complete, photorealistic playable 3D 1974 modular analogue synthesiser and direct-drive 180g vinyl turntable studio ("CHRONO ANALOGUE // SYSTEM 1974"), and render a 2-minute (120.00 s, 7,200 frames) Full HD 1920x1080 @ 60.0 fps showcase video performing four classical symphonies. Use Gemini 4 Argon to direct and integrate the project, headless Blender 5.2 Python (bpy) for editable bevelled 3D assets, Nano Banana (image-generator) + deterministic Python Sobel/PBR synthesis for 16 surface textures, Three.js (r169 MeshPhysicalMaterial) for 60 FPS interaction, Web Audio API for live sound, and FFmpeg for 1080p60 H.264/AAC encoding.

1. SHARED SCHEMA RECORDS & PIPELINE CALIBRATION
Maintain three schema-validated JSON records at the project root (and mirrored to public/ for runtime verification):
- contract.json: 0.1 m source unit (1.0 m exported glTF unit), 0.8 m rack width (4 bays of 0.2 m: VCO BANK, VCF 24 dB/OCT LADDER FILTER, CONTOUR ADSR/VCA, MODULATION LFO & BBD DELAY), 15.0-degree backward faceplate tilt, Blender (+X right, -Y forward, +Z up) to Three.js (+X right, +Y up, +Z forward) conversion, 16 calibrated knobs (-135 deg to +135 deg around local Z), 12 patch sockets (6 upper [OUT] jacks: VCO 1 OUT, VCO 2 OUT, VCF OUT, ENV CV OUT, LFO CV OUT, PHONO OUT; 6 lower [IN] jacks: VCO PITCH CV, VCF AUDIO IN, VCF CUTOFF CV, VCA AUDIO IN, VCA GAIN CV, DELAY IN), 25 hinged keys from C3 to C5 (MIDI 48-72, rotating +4.5 deg around local +X rear hinge), and Turntable_Platter / Tonearm_Gimbal / Tonearm_Headshell / Turntable_SpeedSwitch / Turntable_StartStop contracts.
- world.json: 64 stable entities with parent relationships, coordinate-tagged transforms, 16 texture asset records, 5 camera presets (opening_studio, synth_rack_closeup, patch_and_keys, turntable_closeup, side_profile_tilt), and settled visual decisions.
- progress.json: current milestone, role owners, completed/unresolved work, and verification evidence paths.
Prove the pipeline first by exporting blender/calibration_knob.blend to public/assets/models/calibration_knob.glb and verifying picking and audio activation before building the full 64-entity scene.

2. LUTHIER-GRADE BLENDER GEOMETRY, UVS & 16-MAP PBR TEXTURES
- Generate base surface imagery with Nano Banana (oiled American black walnut, brushed gunmetal turntable deck, 1974 progressive electronic LP cover art, dark espresso pebble leatherette desk, and brushed black-bronze UI console skin) and run scripts/prepare_textures.py to synthesise 16 high-DPI PBR maps (albedo, Sobel height-to-normal, micro-roughness, metallic, and radial vinyl groove normal maps).
- In scripts/build_studio_assets.py, bevel all rectangular cabinet, plinth, key, and slat meshes first (3 segments) and map the V coordinate along the longest axis of every board face so horizontal cabinet rails and plinth ledges display horizontal wood grain while vertical cheeks and slats display vertical wood grain.
- Deepen the synth faceplate (synth_faceplate_albedo.png) to #101215 charcoal-black anodised aluminium with crisp cream silkscreened scales (#faf2e0), amber/cyan sub-headers, engraved bay seams, corner screws, and metallic potentiometer shaft washers under all 16 knobs. Separate mat_anodised_panel (silkscreened faceplate) from mat_anodised_trim (matte dark keybed chassis with zero texture bleed).
- Model 56-segment fluted Bakelite knobs with spun-aluminium top caps and high-contrast cream indicator inlays; 32-segment hex-nut 3.5mm patch sockets with dark bores; 25 sculpted waterfall naturals and chamfered ebony accidentals resting against a crimson felt strip; a 240-segment cast-aluminium platter rim with 2 distinct strobe dot tracks (33 1/3 and 45 RPM) and a recessed black separator channel; a sculpted prism strobe illuminator tower with a glowing neon-amber lens; a recessed 45-RPM adapter puck; a gimbal hydraulic cueing lever; a 36-step S-shaped tubular chrome tonearm with a slotted die-cast magnesium headshell, cartridge, and finger lift; a gatefold 12-inch LP jacket stand; and a 3.80 m x 1.60 m espresso leatherette studio desk with a rounded walnut bullnose front edge and continuous L-shaped walnut acoustic slat wall (slat_i from -32 to 32 with a walnut wainscot ledger rail so zero background void appears in any view).

3. DARK-ROOM 1974 STUDIO PMREM LIGHTING & 60 FPS HARDWARE CONSOLE UI
- Do NOT use Three.js's default white-ceiling RoomEnvironment(), which washes horizontal vinyl and desk surfaces into pale grey. Build a custom dark-ceiling (0x060709) 1974 studio softbox PMREM environment with grazing 3200K warm key, cool cyan control-room fill, and warm amber rim softboxes, plus a local neon-amber PointLight (0xff5e14) at the turntable strobe prism.
- Upgrade all meshes to MeshPhysicalMaterial with computed tangents and anisotropic texture filtering. Set mat_vinyl_record to jet-black (0x050507, clearcoat: 0.92, anisotropy: 0.90) for sharp bow-tie groove reflections, and keep horizontal metal surfaces (mat_turntable_deck, mat_anodised_trim) low-glare (roughness: 0.58-0.78, specularIntensity: 0.15-0.32) so they never blow out under directional lights.
- Eliminate CSS backdrop-filter: blur() completely. Style the top and bottom HUD bars with the solid skeuomorphic brushed black-bronze rack skin (ui_hardware_console_skin.png), throttle non-drag hover raycasting and 2D oscilloscope drawing to 30 Hz, and useTHREE.PCFShadowMap so the interactive studio sustains 60 FPS with zero console errors and zero deprecation warnings.

4. WEB AUDIO SYNTHESISER, TURNTABLE & CORRIDOR CABLE ROUTING
- Implement a live Web Audio API synthesiser (dual oscillators with continuous waveform morphing and sub-octave square, 24 dB/oct resonant ladder filter with saturation drive, ADSR envelope, LFO, and stereo BBD delay) plus a playable 180g vinyl turntable with 33 1/3 RPM (1.00x) and 45 RPM (1.35x) speed presets that preserve playback position across speed switches.
- Route cross-bay patch cables (horizDist > 0.26 m) through the clear horizontal corridor halfway between the upper [OUT] and lower [IN] socket rows (corridorY = (p0.y + p1.y) * 0.5 - 0.005) with per-cable depth/height lane offsets so intermediate sockets (ENV CV OUT, LFO CV OUT, VCA AUDIO IN, VCA GAIN CV) and labels are never occluded. Stack co-located plugs coaxially (+0.014 m along the faceplate normal) so multiple cables sharing a socket never Z-fight.
- Verify all 64 GLB nodes, red-to-green self-test failure injection, 0.000 Hz tuning accuracy across C3-C5, patch validation/rejection rules, stuck-note prevention on window blur, and 60 FPS telemetry via scripts/verify_and_capture_rev3.py.

5. 2-MINUTE FULL HD 1080p60 FOUR-SYMPHONY SOCIAL MEDIA SHOWCASE
- Create scripts/showcase_choreography.py and scripts/render_social_showcase_1080p60.py to render a deterministic 120.00-second (7,200 frames at 60.0 fps, 1920x1080) showcase video (showcase-1080p60.mp4) and 48 kHz stereo WAV master (evidence/social_showcase_1974_symphonies_48k.wav), plus companion .srt subtitles and social media post copy:
  - 0:00-0:30 (Movement I: Beethoven — Symphony No. 5 in C Minor, Op. 67): Live animated cable patching (VCO 1 + VCO 2 -> VCF, ENV CV -> VCF CUTOFF, 4 cables) and sweeping CUTOFF FREQ (280 Hz -> 7,400 Hz) & LADDER DRIVE (3.8x).
  - 0:30-1:00 (Movement II: Bach — Toccata & Fugue in D Minor, BWV 565 / Vivaldi — Winter Allegro): Live cable switching (LFO CV -> VCO PITCH CV, VCF OUT -> DELAY IN, 5 cables), reed/square organ registration, rapid 16th-note counterpoint across C3-C5, and stereo BBD delay.
  - 1:00-1:30 (Movement III: Mozart — Symphony No. 40 in G Minor, K. 550): Patching PHONO OUT -> VCF AUDIO IN (5 cables), lowering the S-shaped tonearm onto the spinning 180g LP at 33 1/3 RPM, flipping live to 45 RPM (1.35x pitch & tempo) for the Mannheim rocket bridge, and returning to 33 1/3 RPM.
  - 1:30-2:00 (Movement IV: Beethoven — Symphony No. 9 "Ode to Joy" Finale): Full-rack maximalist patch occupying all 6 [OUT] sockets across all 4 bays simultaneously + spinning turntable accompaniment, sweeping CUTOFF FREQ to 11.5 kHz and LADDER DRIVE to 4.2x.
- Use a 3D dual-ring crown highlight on the actively swept knob, highlight both source and destination sockets in green during live cable patching, frame all camera presets cleanly between the 96 px Top HUD and 216 px Bottom HUD, and run 30-frame pre-roll warm-ups across parallel Chrome workers so key travel, tonearm angles, and timecodes (floored tenths) are seamless across all 7,200 frames.
```
