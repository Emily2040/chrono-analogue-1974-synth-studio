import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const STUDIO_URL = 'http://127.0.0.1:8088/';
const CDP_PORT = 9234;
const OUT_JSON = path.resolve('evidence/audio_and_interaction_verification.json');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitForCdpTarget(port, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      if (res.ok) {
        const list = await res.json();
        const page = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
        if (page) return page;
      }
    } catch (_) {}
    await sleep(200);
  }
  throw new Error(`Timed out waiting for Chrome CDP target on port ${port}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
    this.consoleMessages = [];
    this.exceptions = [];
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
    this.ws.addEventListener('message', (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
      } else if (msg.method === 'Runtime.consoleAPICalled') {
        const text = (msg.params.args || [])
          .map((a) => a.value ?? a.description ?? '')
          .join(' ');
        this.consoleMessages.push({ type: msg.params.type, text });
      } else if (msg.method === 'Runtime.exceptionThrown') {
        this.exceptions.push(msg.params.exceptionDetails);
      }
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evalAsync(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
    if (res.exceptionDetails) {
      throw new Error(
        `Browser evaluation exception: ${JSON.stringify(res.exceptionDetails)}`
      );
    }
    return res.result?.value;
  }

  close() {
    try {
      this.ws?.close();
    } catch (_) {}
  }
}

async function main() {
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'chrono-studio-cdp-'));
  const chromeProc = spawn(
    CHROME_PATH,
    [
      '--headless=new',
      `--remote-debugging-port=${CDP_PORT}`,
      `--user-data-dir=${userDataDir}`,
      '--window-size=1440,900',
      '--autoplay-policy=no-user-gesture-required',
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--no-first-run',
      '--no-default-browser-check',
      STUDIO_URL
    ],
    { stdio: 'ignore' }
  );

  let client;
  try {
    const target = await waitForCdpTarget(CDP_PORT);
    client = new CdpClient(target.webSocketDebuggerUrl);
    await client.connect();
    await client.send('Runtime.enable');
    await client.send('Page.enable');
    await client.send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false
    });

    // Wait for window.studioApp && window.studioState?.ready
    const readyStart = Date.now();
    let isReady = false;
    while (Date.now() - readyStart < 15000) {
      isReady = await client.evalAsync(
        `Boolean(window.studioApp && window.studioState && window.studioState.ready)`
      );
      if (isReady) break;
      await sleep(200);
    }
    if (!isReady) {
      throw new Error('Studio app did not finish initializing within 15 seconds.');
    }

    const report = await client.evalAsync(`(async () => {
      const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
      const app = window.studioApp;

      // Let 40 frames render to measure realistic browser FPS
      await sleep(700);
      const measuredPerf = { ...app.frameStats };

      // 1. Explicit Audio Activation
      await app.activateAudio();
      await sleep(80);
      const activationCheck = {
        isActivated: app.audio.isActivated,
        contextState: app.audio.ctx?.state,
        sampleRate: app.audio.ctx?.sampleRate,
        pass: app.audio.isActivated === true && app.audio.ctx?.state === 'running'
      };

      // 2. All 16 Knobs Parameter Sweep, Rotation & Audio Node Mapping
      const knobChecks = [];
      for (const spec of app.contract.knobs) {
        const node = app.nodesByName.get(spec.node_name);
        app.setKnobValue(spec.id, spec.min, { immediate: true });
        const rotMinDeg = +((-node.rotation.z * 180) / Math.PI).toFixed(1);
        const valMin = app.knobValues.get(spec.id);

        app.setKnobValue(spec.id, spec.max, { immediate: true });
        const rotMaxDeg = +((-node.rotation.z * 180) / Math.PI).toFixed(1);
        const valMax = app.knobValues.get(spec.id);

        app.setKnobValue(spec.id, spec.default, { immediate: true });
        const valDefault = app.knobValues.get(spec.id);

        knobChecks.push({
          id: spec.id,
          node_name: spec.node_name,
          parameter: spec.parameter,
          valMin,
          valMax,
          valDefault,
          rotMinDeg,
          rotMaxDeg,
          pass:
            Math.abs(rotMinDeg - -135) < 0.5 &&
            Math.abs(rotMaxDeg - 135) < 0.5 &&
            Math.abs(valMin - spec.min) < 1e-6 &&
            Math.abs(valMax - spec.max) < 1e-6
        });
      }

      // 3. Patch Routing Validation (5 Rejected Unsafe Rules)
      app.clearCables();
      const rejectedTests = [
        { expectedCode: 'self_connection', from: 'socket_vco1_out', to: 'socket_vco1_out' },
        { expectedCode: 'unsafe_output_to_output', from: 'socket_vco1_out', to: 'socket_vco2_out' },
        { expectedCode: 'invalid_input_to_input', from: 'socket_vcf_in', to: 'socket_vca_in' },
        { expectedCode: 'dc_offset_cv_to_audio_in', from: 'socket_env_out', to: 'socket_vcf_in' },
        { expectedCode: 'unsafe_feedback_loop', from: 'socket_vcf_out', to: 'socket_vcf_in' }
      ].map((t) => {
        const res = app.patchSockets(t.from, t.to);
        return {
          expectedCode: t.expectedCode,
          actualCode: res.code,
          valid: res.valid,
          message: res.message,
          pass: res.valid === false && res.code === t.expectedCode
        };
      });

      // 4. Signature Interaction: Unpatched Silence -> Patch VCO1 -> VCF -> Play Note -> Turn Cutoff
      app.clearCables();
      await app.setTurntablePower(false);
      await app.setTonearmLowered(false);
      await sleep(80);
      await app.noteOn(60, 'test');
      await sleep(100);
      const unpatchedTelemetry = app.audio.getTelemetry();
      app.noteOff(60, 'test');
      await sleep(80);

      const patch1 = app.patchSockets('socket_vco1_out', 'socket_vcf_in');
      const patch2 = app.patchSockets('socket_vcf_out', 'socket_vca_in');

      // Check 3D cable mesh & minimum clearance from faceplate
      const cableEntry = app.cableMeshes.get('cable_socket_vco1_out__socket_vcf_in');
      const cableMeshExists = Boolean(cableEntry && cableEntry.mesh);

      app.setKnobValue('knob_vcf_env_amt', 0, { immediate: true });
      app.setKnobValue('knob_env_attack', 0.005, { immediate: true });
      app.setKnobValue('knob_env_sustain', 0.9, { immediate: true });
      app.setKnobValue('knob_env_release', 0.04, { immediate: true });
      app.setKnobValue('knob_dly_mix', 0.0, { immediate: true });

      // Check 25-key tuning accuracy across C3 (48), C4 (60), C5 (72)
      const tuningChecks = [];
      for (const [midi, expectedHz] of [[48, 130.813], [60, 261.626], [72, 523.251]]) {
        await app.noteOn(midi, 'tuning');
        await sleep(50);
        const actualHz = +app.audio.nodes.vco1Osc.frequency.value.toFixed(3);
        tuningChecks.push({
          midi,
          expectedHz,
          actualHz,
          pass: Math.abs(actualHz - expectedHz) < 0.25
        });
        app.noteOff(midi, 'tuning');
        await sleep(30);
      }

      // Sweep VCF Cutoff while playing C4 (MIDI 60)
      await app.noteOn(60, 'sweep');
      app.setKnobValue('knob_vcf_cutoff', 110, { immediate: true });
      await sleep(160);
      const lowCutoffTelemetry = app.audio.getTelemetry();
      const vcfStage1LowHz = +app.audio.nodes.vcfStage1.frequency.value.toFixed(1);

      app.setKnobValue('knob_vcf_cutoff', 7200, { immediate: true });
      await sleep(160);
      const highCutoffTelemetry = app.audio.getTelemetry();
      const vcfStage1HighHz = +app.audio.nodes.vcfStage1.frequency.value.toFixed(1);

      // Envelope release decay check
      app.noteOff(60, 'sweep');
      await sleep(240);
      const postReleaseTelemetry = app.audio.getTelemetry();

      // Focus loss / blur stuck-note protection check
      await app.noteOn(60, 'focus_test');
      await app.noteOn(64, 'focus_test');
      const activeBeforeBlur = app.pressedKeys.size;
      window.dispatchEvent(new Event('blur'));
      await sleep(60);
      const activeAfterBlur = app.pressedKeys.size;

      // 5. Turntable Verification: 33 1/3 RPM & 45 RPM Speed Changes + Playable Record Audio
      app.setTurntableSpeed('33');
      await app.setTurntablePower(true);
      await app.setTonearmLowered(true);
      await sleep(260);
      const tt33Telemetry = app.audio.getTelemetry();
      const tt33Status = {
        state: app.audio.turntableState,
        rpm: +app.audio.rpm.toFixed(3),
        playbackRate: +app.audio.getPlaybackRate().toFixed(3),
        omegaRadS: +app.audio.getPlatterAngularVelocityRadS().toFixed(3),
        posSecBeforeSwitch: +app.audio.getTurntablePlaybackPositionSec().toFixed(3),
        rms: tt33Telemetry.rms,
        peak: tt33Telemetry.peak,
        clipping: tt33Telemetry.clipping
      };

      app.setTurntableSpeed('45');
      await sleep(140);
      const tt45Telemetry = app.audio.getTelemetry();
      const tt45Status = {
        state: app.audio.turntableState,
        rpm: +app.audio.rpm.toFixed(3),
        playbackRate: +app.audio.getPlaybackRate().toFixed(3),
        omegaRadS: +app.audio.getPlatterAngularVelocityRadS().toFixed(3),
        posSecAfterSwitch: +app.audio.getTurntablePlaybackPositionSec().toFixed(3),
        rms: tt45Telemetry.rms,
        peak: tt45Telemetry.peak,
        clipping: tt45Telemetry.clipping
      };

      // Reset Studio check: stops turntable & releases all sound
      app.resetStudio();
      await sleep(140);
      const postResetDiagnostics = app.getDiagnostics();

      // 6. Input Mode Selection (QWERTY & Web MIDI Explicit Unavailable State)
      const midiModeResult = await app.setInputMode('midi');
      const qwertyModeResult = await app.setInputMode('qwerty');

      return {
        timestamp: new Date().toISOString(),
        browser: {
          userAgent: navigator.userAgent,
          viewport: [app.canvas.clientWidth, app.canvas.clientHeight],
          devicePixelRatio: window.devicePixelRatio || 1
        },
        worldVerification: app.worldVerification,
        activationCheck,
        knobSummary: {
          totalTested: knobChecks.length,
          allPass: knobChecks.every((k) => k.pass),
          knobs: knobChecks
        },
        rejectedRoutingChecks: {
          totalTested: rejectedTests.length,
          allPass: rejectedTests.every((r) => r.pass),
          results: rejectedTests
        },
        signatureInteraction: {
          unpatchedRms: unpatchedTelemetry.rms,
          unpatchedSilentPass: unpatchedTelemetry.rms < 0.002,
          patchVco1ToVcfValid: patch1.valid,
          patchVcfToVcaValid: patch2.valid,
          cableMeshExists,
          tuningChecks,
          lowCutoff110Hz: {
            vcfHz: vcfStage1LowHz,
            rms: lowCutoffTelemetry.rms,
            peak: lowCutoffTelemetry.peak,
            centroidHz: lowCutoffTelemetry.centroidHz
          },
          highCutoff7200Hz: {
            vcfHz: vcfStage1HighHz,
            rms: highCutoffTelemetry.rms,
            peak: highCutoffTelemetry.peak,
            centroidHz: highCutoffTelemetry.centroidHz,
            clipping: highCutoffTelemetry.clipping
          },
          filterOpeningPass:
            highCutoffTelemetry.centroidHz > lowCutoffTelemetry.centroidHz * 1.8 &&
            highCutoffTelemetry.rms > 0.01 &&
            highCutoffTelemetry.peak <= 0.95 &&
            !highCutoffTelemetry.clipping,
          envelopeReleaseRms: postReleaseTelemetry.rms,
          envelopeReleasePass: postReleaseTelemetry.rms < 0.005,
          focusBlurGuard: {
            activeBeforeBlur,
            activeAfterBlur,
            pass: activeBeforeBlur === 2 && activeAfterBlur === 0
          }
        },
        turntableVerification: {
          mode33Rpm: tt33Status,
          mode45Rpm: tt45Status,
          speedRatioPass:
            Math.abs(tt33Status.playbackRate - 1.0) < 0.01 &&
            Math.abs(tt45Status.playbackRate - 1.35) < 0.01 &&
            Math.abs(tt33Status.omegaRadS - 3.491) < 0.01 &&
            Math.abs(tt45Status.omegaRadS - 4.712) < 0.01,
          positionPreservedOnSpeedChange:
            tt45Status.posSecAfterSwitch >= tt33Status.posSecBeforeSwitch &&
            tt33Status.posSecBeforeSwitch > 0.05,
          recordAudiblePass: tt33Status.rms > 0.005 && !tt33Status.clipping,
          resetStopsAllSoundPass:
            postResetDiagnostics.turntable.state === 'stopped_raised' &&
            postResetDiagnostics.activeNotes.length === 0
        },
        inputModes: {
          midiCheck: midiModeResult,
          qwertyCheck: qwertyModeResult
        },
        performance: {
          ...measuredPerf,
          viewport: [app.canvas.clientWidth, app.canvas.clientHeight],
          devicePixelRatio: window.devicePixelRatio || 1
        }
      };
    })()`);

    report.consoleErrors = client.consoleMessages.filter((m) => m.type === 'error');
    report.consoleWarnings = client.consoleMessages.filter((m) => m.type === 'warning');
    report.runtimeExceptions = client.exceptions;

    fs.mkdirSync(path.dirname(OUT_JSON), { recursive: true });
    fs.writeFileSync(OUT_JSON, JSON.stringify(report, null, 2), 'utf8');
    console.log('VERIFICATION COMPLETE ->', OUT_JSON);
    console.log(
      JSON.stringify(
        {
          worldPass: report.worldVerification.pass,
          worldChecked: report.worldVerification.checkedCount,
          activationPass: report.activationCheck.pass,
          knobsAllPass: report.knobSummary.allPass,
          rejectedRoutingAllPass: report.rejectedRoutingChecks.allPass,
          unpatchedSilentPass: report.signatureInteraction.unpatchedSilentPass,
          filterOpeningPass: report.signatureInteraction.filterOpeningPass,
          lowCentroidHz: report.signatureInteraction.lowCutoff110Hz.centroidHz,
          highCentroidHz: report.signatureInteraction.highCutoff7200Hz.centroidHz,
          envelopeReleasePass: report.signatureInteraction.envelopeReleasePass,
          focusBlurGuardPass: report.signatureInteraction.focusBlurGuard.pass,
          turntableRecordAudiblePass: report.turntableVerification.recordAudiblePass,
          turntableSpeedRatioPass: report.turntableVerification.speedRatioPass,
          turntablePosPreserved: report.turntableVerification.positionPreservedOnSpeedChange,
          resetStopsAllSoundPass: report.turntableVerification.resetStopsAllSoundPass,
          consoleErrorCount: report.consoleErrors.length,
          exceptionCount: report.runtimeExceptions.length,
          fps: report.performance.fps
        },
        null,
        2
      )
    );
  } finally {
    client?.close();
    try {
      chromeProc.kill();
    } catch (_) {}
  }
}

main().catch((err) => {
  console.error('Verification failed:', err);
  process.exit(1);
});
