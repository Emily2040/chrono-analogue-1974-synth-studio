"""
Headless Chrome CDP Verification & Screenshot Capture Suite (Revision 3 - PS5 Pro Photorealism + Fast Hardware UI).
Launches Chrome on localhost:9234, connects via WebSocket CDP, captures all 5 fixed camera views at 1440x900,
and runs the complete audio, routing, tuning, filter-sweep, turntable 33.3/45 RPM speed change, reset,
MIDI state, and UI frame-time performance verification suite.
"""

import base64
import json
import os
import socket
import struct
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAPTURES_DIR = ROOT / "evidence" / "captures"
EVIDENCE_JSON = ROOT / "evidence" / "audio_and_interaction_verification.json"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STUDIO_URL = "http://127.0.0.1:8088/"
CDP_PORT = 9234


class CDPClient:
    def __init__(self, ws_url: str):
        without_scheme = ws_url.replace("ws://", "")
        host_port, self.path = without_scheme.split("/", 1)
        self.path = "/" + self.path
        host, port_s = host_port.split(":")
        self.host = host
        self.port = int(port_s)
        self.sock = socket.create_connection((self.host, self.port), timeout=30)
        self._handshake()
        self.msg_id = 0

    def _handshake(self):
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode("ascii"))
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("WebSocket handshake failed")
            resp += chunk

    def _send_frame(self, payload: bytes):
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        mask = os.urandom(4)
        header.extend(mask)
        masked = bytearray(length)
        for i in range(length):
            masked[i] = payload[i] ^ mask[i % 4]
        self.sock.sendall(header + masked)

    def _recv_exact(self, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise RuntimeError("Socket closed while reading WebSocket frame")
            buf.extend(chunk)
        return bytes(buf)

    def _recv_frame(self) -> str:
        while True:
            b1, b2 = self._recv_exact(2)
            opcode = b1 & 0x0F
            masked = (b2 & 0x80) != 0
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else b""
            data = self._recv_exact(length)
            if masked:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if opcode == 0x8:
                raise RuntimeError("WebSocket closed by remote")
            if opcode == 0x9:
                pong = bytearray([0x8A, 0x80]) + os.urandom(4)
                self.sock.sendall(pong)
                continue
            if opcode in (0x1, 0x2):
                return data.decode("utf-8", errors="replace")

    def call(self, method: str, params: dict = None) -> dict:
        self.msg_id += 1
        target_id = self.msg_id
        msg = {"id": target_id, "method": method, "params": params or {}}
        self._send_frame(json.dumps(msg).encode("utf-8"))
        while True:
            raw = self._recv_frame()
            data = json.loads(raw)
            if data.get("id") == target_id:
                if "error" in data:
                    raise RuntimeError(f"CDP error in {method}: {data['error']}")
                return data.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = True):
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True,
            },
        )
        if "exceptionDetails" in res:
            raise RuntimeError(f"JS exception: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    def capture_png(self, out_path: Path):
        res = self.call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        b64 = res.get("data", "")
        raw = base64.b64decode(b64)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(raw)
        return len(raw)

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def wait_for_cdp_target(port: int, timeout_s: float = 15.0) -> str:
    deadline = time.time() + timeout_s
    url = f"http://127.0.0.1:{port}/json/list"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as resp:
                targets = json.loads(resp.read().decode("utf-8"))
                for t in targets:
                    if t.get("type") == "page" and "webSocketDebuggerUrl" in t:
                        return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for Chrome CDP target on port {port}")


def main():
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    user_data_dir = ROOT / "evidence" / "chrome_cdp_profile"
    user_data_dir.mkdir(parents=True, exist_ok=True)

    chrome_cmd = [
        CHROME_EXE,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_data_dir}",
        "--window-size=1440,900",
        "--device-scale-factor=1",
        "--autoplay-policy=no-user-gesture-required",
        "--enable-webgl",
        "--ignore-gpu-blocklist",
        "--use-angle=d3d11",
        "--no-first-run",
        "--no-default-browser-check",
        STUDIO_URL,
    ]

    print(f"Launching headless Chrome on port {CDP_PORT}...")
    proc = subprocess.Popen(
        chrome_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ws_url = wait_for_cdp_target(CDP_PORT, timeout_s=15.0)
        print(f"Connected to CDP target: {ws_url}")
        cdp = CDPClient(ws_url)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": 1440,
                "height": 900,
                "deviceScaleFactor": 1,
                "mobile": False,
            },
        )
        cdp.call("Page.navigate", {"url": STUDIO_URL})
        time.sleep(0.4)
        cdp.evaluate(
            """(() => {
                window.__consoleErrors = [];
                window.__consoleWarnings = [];
                const origErr = console.error.bind(console);
                const origWarn = console.warn.bind(console);
                console.error = (...args) => { window.__consoleErrors.push(args.map(String).join(' ')); origErr(...args); };
                console.warn = (...args) => { window.__consoleWarnings.push(args.map(String).join(' ')); origWarn(...args); };
                window.addEventListener('error', (e) => window.__consoleErrors.push(e.message));
                window.addEventListener('unhandledrejection', (e) => window.__consoleErrors.push(String(e.reason)));
            })()""",
            await_promise=False,
        )
        time.sleep(0.6)

        print("Waiting for window.studioApp.getDiagnostics().worldVerification.pass...")
        deadline = time.time() + 30.0
        diag = None
        while time.time() < deadline:
            diag = cdp.evaluate(
                "window.studioApp && window.studioApp.getDiagnostics ? window.studioApp.getDiagnostics() : null",
                await_promise=False,
            )
            if diag and diag.get("worldVerification") and diag["worldVerification"].get("pass"):
                break
            time.sleep(0.35)

        if not diag or not diag.get("worldVerification", {}).get("pass"):
            raise RuntimeError(f"Studio scene did not pass worldVerification within timeout: {diag}")

        wv = diag["worldVerification"]
        print(f"Studio scene ready! World verification: {wv['checkedCount']} entities verified, {len(wv.get('mismatches', []))} mismatches.")

        # Activate audio engine explicitly and load signature patched preset + turntable spinning
        cdp.evaluate(
            """(async () => {
                await window.studioApp.activateAudio();
                window.studioApp.loadPreset('signature_patched_lead');
                await window.studioApp.setTurntablePower(true);
                await window.studioApp.setTonearmLowered(true);
                await new Promise(r => setTimeout(r, 400));
                return true;
            })()"""
        )

        # Capture the 5 fixed camera views for Revision 4 (preserving rev3_*.png for before/after comparison)
        presets = [
            ("opening_studio", "rev4_opening_studio.png", False),
            ("synth_rack_closeup", "rev4_synth_rack_closeup.png", False),
            ("patch_and_keys", "rev4_patch_and_keys.png", True),
            ("turntable_closeup", "rev4_turntable_closeup.png", False),
            ("side_profile_tilt", "rev4_side_profile_tilt.png", True),
        ]

        captured_files = {}
        for preset_id, filename, press_chord in presets:
            cdp.evaluate(
                f"""(async () => {{
                    window.studioApp.setCameraPreset('{preset_id}', {{ immediate: true }});
                    if ({'true' if press_chord else 'false'}) {{
                        await window.studioApp.noteOn(48, 'verify');
                        await window.studioApp.noteOn(52, 'verify');
                        await window.studioApp.noteOn(55, 'verify');
                    }} else {{
                        window.studioApp.releaseAllNotes();
                    }}
                    await new Promise(r => setTimeout(r, 450));
                    return true;
                }})()"""
            )
            out_path = CAPTURES_DIR / filename
            sz = cdp.capture_png(out_path)
            captured_files[preset_id] = {
                "path": f"evidence/captures/{filename}",
                "bytes": sz,
            }
            print(f"Captured {filename} ({sz:,} bytes)")

        # Release chord and return to opening_studio before running full automated verification
        cdp.evaluate(
            """(async () => {
                window.studioApp.releaseAllNotes();
                window.studioApp.setCameraPreset('opening_studio', { immediate: true });
                await new Promise(r => setTimeout(r, 200));
                return true;
            })()"""
        )

        print("Running full audio, interaction, PBR material, and FPS verification suite...")
        verification_report = cdp.evaluate(
            """(async () => {
                const app = window.studioApp;
                const audio = app.audio;
                const sleep = (ms) => new Promise(r => setTimeout(r, ms));

                // 1. Check PBR MeshPhysicalMaterial upgrades & textures
                let physicalMatCount = 0;
                let clearcoatMatCount = 0;
                let anisotropyMatCount = 0;
                let normalMapMatCount = 0;
                app.scene.traverse((obj) => {
                    if (obj.isMesh && obj.material) {
                        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
                        for (const m of mats) {
                            if (m.isMeshPhysicalMaterial) physicalMatCount++;
                            if (m.clearcoat > 0) clearcoatMatCount++;
                            if (m.anisotropy > 0) anisotropyMatCount++;
                            if (m.normalMap) normalMapMatCount++;
                        }
                    }
                });

                // Stop turntable first so synth measurements are isolated
                await app.setTurntablePower(false);
                await app.setTonearmLowered(false);
                await sleep(150);

                // 2. Signature patch verification: unpatched silence vs patched VCO1 -> VCF -> VCA + filter sweep
                app.resetStudio();
                app.clearCables();
                await sleep(250);
                await app.noteOn(60, 'test');
                await sleep(200);
                const unpatchedTelem = audio.getTelemetry();
                app.noteOff(60, 'test');
                await sleep(150);

                // Connect signature patch: socket_vco1_out -> socket_vcf_in, socket_vcf_out -> socket_vca_in, socket_env_out -> socket_vcf_cutoff_cv
                const p1 = app.patchSockets('socket_vco1_out', 'socket_vcf_in');
                const p2 = app.patchSockets('socket_vcf_out', 'socket_vca_in');
                const p3 = app.patchSockets('socket_env_out', 'socket_vcf_cutoff_cv');

                // Set low cutoff (160 Hz) and measure spectral centroid
                app.setKnobValue('knob_vcf_cutoff', 160.0, { immediate: true });
                app.setKnobValue('knob_vcf_env_amt', 0.0, { immediate: true });
                await app.noteOn(60, 'test');
                await sleep(240);
                const lowCutoffTelem = audio.getTelemetry();

                // Sweep cutoff open to 7200 Hz while note is held
                app.setKnobValue('knob_vcf_cutoff', 7200.0, { immediate: true });
                await sleep(240);
                const highCutoffTelem = audio.getTelemetry();
                app.noteOff(60, 'test');
                await sleep(250);

                // 3. Patch validation rules (compatible vs incompatible/unsafe)
                const selfConn = app.patchSockets('socket_vco1_out', 'socket_vco1_out');
                const outToOut = app.patchSockets('socket_vco1_out', 'socket_vco2_out');
                const inToIn = app.patchSockets('socket_vcf_in', 'socket_vca_in');
                const cvToAudio = app.patchSockets('socket_env_out', 'socket_vcf_in');
                const feedbackLoop = app.patchSockets('socket_vcf_out', 'socket_vcf_in');

                // 4. All 16 knobs range & parameter check
                const knobChecks = [];
                for (const k of app.contract.knobs) {
                    const midVal = (k.min + k.max) * 0.5;
                    const applied = app.setKnobValue(k.id, midVal, { immediate: true });
                    const node = app.nodesByName.get(k.node_name);
                    knobChecks.push({
                        id: k.id,
                        parameter: k.parameter,
                        value: applied,
                        nodeRotated: Boolean(node && Number.isFinite(node.rotation.z))
                    });
                }
                // Restore signature preset
                app.loadPreset('signature_patched_lead');
                await sleep(150);

                // 5. Tuning check across C3 (48, 130.813 Hz), A3 (57, 220.0 Hz), C4 (60, 261.626 Hz), C5 (72, 523.251 Hz)
                const tuningChecks = [];
                for (const midi of [48, 57, 60, 72]) {
                    const kSpec = app.contract.keyboard.keys.find(k => k.midi_note === midi);
                    await app.noteOn(midi, 'tuning');
                    await sleep(160);
                    const vco1Freq = audio.nodes && audio.nodes.vco1Saw ? audio.nodes.vco1Saw.frequency.value : 0;
                    tuningChecks.push({
                        keyId: kSpec.id,
                        note: kSpec.note_name,
                        midi,
                        expectedHz: kSpec.frequency_hz,
                        actualVco1Hz: Number(vco1Freq.toFixed(3)),
                        errorHz: Number(Math.abs(vco1Freq - kSpec.frequency_hz).toFixed(4))
                    });
                    app.noteOff(midi, 'tuning');
                    await sleep(70);
                }

                // 6. Stuck-note prevention on window blur
                await app.noteOn(48, 'blur_test');
                await app.noteOn(52, 'blur_test');
                const activeBeforeBlur = app.pressedKeys.size;
                window.dispatchEvent(new Event('blur'));
                await sleep(100);
                const activeAfterBlur = app.pressedKeys.size;

                // 7. MIDI input mode check (explicit unavailable state when 0 hardware devices present)
                const midiResult = await app.setInputMode('midi');
                await app.setInputMode('qwerty');

                // 8. Turntable 33 1/3 and 45 RPM speed & pitch ratio + position continuity
                await app.setTurntablePower(true);
                await app.setTonearmLowered(true);
                app.setTurntableSpeed('33');
                await sleep(320);
                const tt33 = app.getDiagnostics().turntable;
                const posBeforeSwitch = audio.getTurntablePlaybackPositionSec();
                app.setTurntableSpeed('45');
                await sleep(120);
                const tt45 = app.getDiagnostics().turntable;
                const posAfterSwitch = audio.getTurntablePlaybackPositionSec();
                app.setTurntableSpeed('33');

                // 9. Reset stops and releases all active sound
                await app.noteOn(60, 'reset_test');
                await sleep(120);
                app.resetStudio();
                await sleep(350);
                const postResetDiag = app.getDiagnostics();

                // Restore signature lead preset + turntable for live interactive state
                app.loadPreset('signature_patched_lead');
                await app.setTurntablePower(true);
                await app.setTonearmLowered(true);
                await app.noteOn(60, 'perf_test');

                // 10. Measure UI + 3D rendering frame rate over 90 frames while playing note & spinning platter
                const frameDeltas = [];
                let lastT = performance.now();
                for (let i = 0; i < 90; i++) {
                    await new Promise(r => requestAnimationFrame(r));
                    const nowT = performance.now();
                    frameDeltas.push(nowT - lastT);
                    lastT = nowT;
                }
                app.noteOff(60, 'perf_test');
                const avgFrameMs = frameDeltas.reduce((a, b) => a + b, 0) / frameDeltas.length;
                const fps = 1000.0 / avgFrameMs;
                const sortedDeltas = [...frameDeltas].sort((a, b) => a - b);
                const p95FrameMs = sortedDeltas[Math.floor(sortedDeltas.length * 0.95)];

                // 11. Self-test gate (Gravitas 05-acceptance.md): inject a fake missing entity into world.entities,
                // run _verifyWorldAgainstGLB(), verify it goes RED (pass === false), then restore and verify GREEN!
                app.world.entities.push({
                    entity_id: '__injected_bogus_entity',
                    node_name: '__Injected_Bogus_Node_Must_Fail',
                    parent_id: null,
                    category: 'test',
                    coord_tag: 'threejs_local_m',
                    position_m: [0, 0, 0],
                    rotation_euler_deg: [0, 0, 0],
                    scale: [1, 1, 1],
                    material_id: 'mat_bakelite_knob'
                });
                app._verifyWorldAgainstGLB();
                const failedWhenInjected = (app.worldVerification.pass === false && app.worldVerification.mismatches.length === 1);
                app.world.entities.pop();
                app._verifyWorldAgainstGLB();
                const restoredPass = (app.worldVerification.pass === true && app.worldVerification.mismatches.length === 0);

                const gl = app.renderer.getContext();
                const dbgInfo = gl.getExtension('WEBGL_debug_renderer_info');
                const gpuRenderer = dbgInfo ? gl.getParameter(dbgInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);

                return {
                    timestamp: new Date().toISOString(),
                    revision: 4,
                    browser: {
                        userAgent: navigator.userAgent,
                        viewport: { width: window.innerWidth, height: window.innerHeight, devicePixelRatio: window.devicePixelRatio },
                        gpuRenderer
                    },
                    consoleAndShadowGate: {
                        consoleErrors: window.__consoleErrors || [],
                        consoleWarnings: window.__consoleWarnings || [],
                        zeroConsoleErrors: (window.__consoleErrors || []).length === 0,
                        zeroDeprecationWarnings: (window.__consoleWarnings || []).filter(w => w.includes('THREE.')).length === 0,
                        shadowMapEnabled: app.renderer.shadowMap.enabled,
                        shadowMapType: app.renderer.shadowMap.type
                    },
                    selfTestGate: {
                        failedWhenBogusNodeInjected: failedWhenInjected,
                        restoredCleanPass: restoredPass,
                        selfTestPassed: failedWhenInjected && restoredPass
                    },
                    sceneVerification: {
                        worldVerification: app.worldVerification,
                        physicalMatCount,
                        clearcoatMatCount,
                        anisotropyMatCount,
                        normalMapMatCount
                    },
                    signaturePatchVerification: {
                        unpatchedRms: unpatchedTelem.rms,
                        lowCutoffHz: 160.0,
                        lowCutoffRms: lowCutoffTelem.rms,
                        lowCutoffCentroidHz: lowCutoffTelem.centroidHz,
                        highCutoffHz: 7200.0,
                        highCutoffRms: highCutoffTelem.rms,
                        highCutoffCentroidHz: highCutoffTelem.centroidHz,
                        filterSweepOpenedAudibly: highCutoffTelem.centroidHz > lowCutoffTelem.centroidHz * 1.8,
                        peakBelowClipping: highCutoffTelem.peak < 0.99 && !highCutoffTelem.clipping
                    },
                    patchRuleValidation: {
                        validConnectionsCreated: Boolean(p1.valid && p2.valid && p3.valid),
                        selfConnectionRejected: !selfConn.valid && selfConn.code === 'self_connection',
                        outputToOutputRejected: !outToOut.valid && outToOut.code === 'unsafe_output_to_output',
                        inputToInputRejected: !inToIn.valid && inToIn.code === 'invalid_input_to_input',
                        cvToAudioInRejected: !cvToAudio.valid && cvToAudio.code === 'dc_offset_cv_to_audio_in',
                        unsafeFeedbackLoopRejected: !feedbackLoop.valid && feedbackLoop.code === 'unsafe_feedback_loop'
                    },
                    knobVerification: {
                        totalKnobsTested: knobChecks.length,
                        all16Functional: knobChecks.length === 16 && knobChecks.every(k => k.value !== null && k.nodeRotated)
                    },
                    tuningVerification: {
                        checks: tuningChecks,
                        allAccurateWithin0_05Hz: tuningChecks.every(t => t.errorHz < 0.05)
                    },
                    stuckNotePrevention: {
                        activeBeforeBlur,
                        activeAfterBlur,
                        blurReleasesAllNotes: activeBeforeBlur === 2 && activeAfterBlur === 0
                    },
                    midiInputVerification: midiResult,
                    turntableVerification: {
                        rpm33State: tt33,
                        rpm45State: tt45,
                        rate33Expected: 1.0,
                        rate45Expected: 1.35,
                        positionBeforeSwitchSec: Number(posBeforeSwitch.toFixed(3)),
                        positionAfterSwitchSec: Number(posAfterSwitch.toFixed(3)),
                        positionPreservedAcrossSpeedChange: posAfterSwitch >= posBeforeSwitch && (posAfterSwitch - posBeforeSwitch) < 0.35
                    },
                    panicResetVerification: {
                        activeNotesAfterReset: postResetDiag.activeNotes.length,
                        turntableMotorAfterReset: postResetDiag.turntable.motorOn,
                        rmsAfterReset: postResetDiag.levels.rms
                    },
                    performanceTelemetry: {
                        sampledFrames: frameDeltas.length,
                        avgFrameTimeMs: Number(avgFrameMs.toFixed(2)),
                        p95FrameTimeMs: Number(p95FrameMs.toFixed(2)),
                        measuredFps: Number(fps.toFixed(1)),
                        drawCalls: app.renderer.info.render.calls,
                        triangles: app.renderer.info.render.triangles
                    }
                };
            })()"""
        )

        verification_report["capturedScreenshots"] = captured_files
        EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE_JSON.write_text(json.dumps(verification_report, indent=2), encoding="utf-8")
        print(f"Wrote verification report to {EVIDENCE_JSON}")
        print("Performance Telemetry:", json.dumps(verification_report["performanceTelemetry"], indent=2))
        print("Console & Shadow Gate:", json.dumps(verification_report["consoleAndShadowGate"], indent=2))
        print("Self-Test Gate:", json.dumps(verification_report["selfTestGate"], indent=2))
        print("Tuning Verification:", json.dumps(verification_report["tuningVerification"], indent=2))
        cdp.close()

        # Assert all critical gates pass or exit 1
        assert verification_report["consoleAndShadowGate"]["zeroConsoleErrors"], "Console errors detected!"
        assert verification_report["selfTestGate"]["selfTestPassed"], "Self-test gate failed!"
        assert verification_report["sceneVerification"]["worldVerification"]["pass"], "World verification failed!"
        assert verification_report["signaturePatchVerification"]["filterSweepOpenedAudibly"], "Filter sweep gate failed!"
        assert verification_report["knobVerification"]["all16Functional"], "Knob verification gate failed!"
        assert verification_report["tuningVerification"]["allAccurateWithin0_05Hz"], "Tuning accuracy gate failed!"
        assert verification_report["stuckNotePrevention"]["blurReleasesAllNotes"], "Stuck-note blur gate failed!"
        assert verification_report["turntableVerification"]["positionPreservedAcrossSpeedChange"], "Turntable position continuity gate failed!"
        print("ALL AUTOMATED GATES PASSED (INCLUDING G_SELF_TEST RED->GREEN VERIFICATION).")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
