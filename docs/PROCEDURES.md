# Project-Local Procedures: 1970s Modular Analogue Synthesiser & Turntable Studio

## 1. Headless Blender (`bpy`) Authoring & glTF Export Procedure
No standalone Blender skill is installed in the host skill catalogue. All 3D asset authoring and glTF/GLB export follows this deterministic procedure:

1. **Executable Resolution**:
   - Path: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (verified Blender 5.2.2 LTS).
   - Invocation:
     ```powershell
     & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python <script.py> -- <script_args>
     ```
2. **Coordinate System & Units**:
   - Source unit in `contract.json`: `0.1 m` (8 source units = `0.8 m` modular rack width).
   - Blender scene units are metric (`1.0` Blender unit = `1.0 m`).
   - Blender authoring axes: `+X` right, `+Y` back (`-Y` front toward operator), `+Z` up.
   - glTF export converts to Three.js right-handed Y-up (`+X` right, `+Y` up, `+Z` front toward operator) via `bpy.ops.export_scene.gltf(..., export_yup=True)`.
3. **Pivot & Hierarchy Discipline**:
   - Every interactive control (`Knob_*`, `Socket_*`, `Key_*`, `Turntable_Platter`, `Tonearm_Gimbal`, `Turntable_SpeedSwitch`, `Turntable_StartStop`) is authored with its local origin at its mechanical pivot point.
   - Controls mounted on the 15-degree tilted synthesiser faceplate are parented under `Synth_Faceplate_Frame` (which carries the `-15°` X-axis tilt in Three.js / `+15°` in Blender), or carry explicit local transforms aligned to the faceplate normal so rotating a knob around its local spin axis never wobbles off-axis.
4. **Editable Source Preservation**:
   - Every generator script saves both the editable `.blend` source file under `blender/*.blend` and the runtime `.glb` binary under `public/assets/models/*.glb`.
   - `scripts/verify_world_assets.py` inspects the exported `.glb` structure to verify that every node name, hierarchy link, and pivot position declared in `contract.json` and `world.json` is present.

## 2. Nano Banana / Image Asset Preparation Procedure
1. **Tool Verification**:
   - Direct `generate_image` is not exposed in the root agent declaration; image generation is routed through the native `image-generator` subagent (which wraps Antigravity's built-in Nano Banana / image generation tool) and verified via `view_file`.
2. **Surface & Artwork Assets**:
   - Use Nano Banana (`image-generator`) for visual direction exploration, American black walnut wood grain studies, and 1970s vinyl record sleeve and center-label imagery.
   - Build technical panel lettering, calibration tick scales, and jack labels deterministically via Python (`PIL` / high-DPI Cairo/Pillow rasterization) so text and graduations remain razor-sharp and exact at every control position.
   - Derive normal/bump maps only from continuous height data (procedural wood pore heightfield and concentric vinyl groove heightfield), never from baked lighting or albedo photographs.

## 3. Browser Inspection & Audio Verification Procedure
1. **Live Browser Inspection**:
   - Serve the studio over local HTTP (`http://127.0.0.1:8088/`) and inspect via `chrome-devtools-mcp` (`new_page`, `navigate_page`, `resize_page`, `take_screenshot`, `evaluate_script`, `list_console_messages`).
   - Assert zero console errors and zero WebGL warnings on every checkpoint.
2. **Audio Verification**:
   - Web Audio requires an explicit user gesture (`AudioContext.resume()`). Verify both locked (pre-gesture) and active (post-gesture) states.
   - Measure RMS level, peak amplitude (checking against clipping `peak < 0.98`), fundamental frequency changes across C3–C5 and filter cutoff sweeps, envelope release decay to silence, and turntable 33⅓ vs 45 RPM pitch/speed ratio (`1.35x`) with position continuity.
   - Record WAV captures from the live Web Audio graph for direct inspection and archival under `evidence/audio/`.

## 4. Independent Visual Critique Procedure
1. Capture fixed camera presets (`overview`, `rack_closeup`, `patch_bay`, `keyboard_closeup`, `turntable_closeup`) to `evidence/captures/`.
2. Pass the captured PNGs to `gravitas-visual-critic` (read-only viewer with no access to code or scene graph) to judge material read, lighting direction, control legibility, cable drape, and cartridge contact.
3. Log defects in `progress.json`, repair the three most consequential visual or audio defects, and re-capture the exact same camera presets for before/after verification.
