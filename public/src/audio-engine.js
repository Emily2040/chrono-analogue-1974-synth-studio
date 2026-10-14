/**
 * 1974 Modular Analogue Synthesiser & Direct-Drive Turntable Web Audio Engine
 * Consumes contract.json port definitions, parameter ranges, smoothing time constants, and routing rules.
 */

export class StudioAudioEngine {
  constructor(contract) {
    this.contract = contract;
    this.ctx = null;
    this.isActivated = false;
    this.isMuted = false;
    this.masterVolume = 0.80;

    // Parameter state keyed by contract knob ID
    this.knobValues = {};
    for (const k of contract.knobs) {
      this.knobValues[k.id] = k.default;
    }

    // Active patch cables: Array of { id, fromSocketId, toSocketId, color }
    this.cables = [];

    // Active notes Map: midiNote -> Set of trigger sources ('pointer', 'qwerty:Z', 'midi:48')
    this.activeNotes = new Map();
    this.currentMidiNote = null;
    this.currentNoteFreq = 130.81; // C3 default
    this.gateOpen = false;

    // Turntable state
    this.turntableState = 'stopped_rest'; // stopped_rest | cued_spinning | playing_33 | playing_45 | paused_on_record
    this.motorOn = false;
    this.tonearmLowered = false;
    this.tonearmProgress = 0.0; // 0 = outer groove, 1 = inner groove
    this.rpm = 33.333333;
    this.recordBuffer = null;
    this.recordSource = null;
    this.recordOffsetSec = 0.0;
    this.recordStartCtxTime = 0.0;

    // Web Audio nodes
    this.nodes = {};
    this.portMap = {};
    this.analyser = null;
    this.timeDomainBuf = null;
    this.freqDomainBuf = null;

    // Recording capture buffer for offline/WAV verification
    this.mediaRecorder = null;
  }

  async initAndResume() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx({ sampleRate: this.contract.audio_graph.sample_rate_hz || 44100 });
      this._buildAudioGraph();
      await this._loadTurntableBuffer();
      this._syncAllParameters(true);
      this._rebuildPatchRouting();
    }
    if (this.ctx.state === 'suspended') {
      await this.ctx.resume();
    }
    this.isActivated = (this.ctx.state === 'running');
    return this.isActivated;
  }

  _makeSoftClipCurve(amount = 1.5) {
    const n = 8192;
    const curve = new Float32Array(n);
    const norm = Math.tanh(amount);
    for (let i = 0; i < n; i++) {
      const x = (i * 2) / (n - 1) - 1;
      curve[i] = Math.tanh(x * amount) / norm;
    }
    return curve;
  }

  _buildAudioGraph() {
    const ctx = this.ctx;

    // 1. VCO 1 (Morphing Sine -> Triangle -> Sawtooth -> Square)
    const vco1Sine = ctx.createOscillator(); vco1Sine.type = 'sine';
    const vco1Tri = ctx.createOscillator(); vco1Tri.type = 'triangle';
    const vco1Saw = ctx.createOscillator(); vco1Saw.type = 'sawtooth';
    const vco1Sq = ctx.createOscillator(); vco1Sq.type = 'square';

    const gSine = ctx.createGain();
    const gTri = ctx.createGain();
    const gSaw = ctx.createGain();
    const gSq = ctx.createGain();
    const vco1OutGain = ctx.createGain();
    vco1OutGain.gain.value = 0.55;

    vco1Sine.connect(gSine); gSine.connect(vco1OutGain);
    vco1Tri.connect(gTri); gTri.connect(vco1OutGain);
    vco1Saw.connect(gSaw); gSaw.connect(vco1OutGain);
    vco1Sq.connect(gSq); gSq.connect(vco1OutGain);

    // 2. VCO 2 + Sub Oscillator (-1 octave square)
    const vco2Saw = ctx.createOscillator(); vco2Saw.type = 'sawtooth';
    const vco2Sub = ctx.createOscillator(); vco2Sub.type = 'square';
    const gVco2Main = ctx.createGain(); gVco2Main.gain.value = 0.6;
    const gVco2Sub = ctx.createGain(); gVco2Sub.gain.value = 0.4;
    const vco2OutGain = ctx.createGain();
    vco2OutGain.gain.value = 0.50;

    vco2Saw.connect(gVco2Main); gVco2Main.connect(vco2OutGain);
    vco2Sub.connect(gVco2Sub); gVco2Sub.connect(vco2OutGain);

    // Pitch CV Input (modulates detune of VCO1 & VCO2 in cents)
    const vcoPitchCvInGain = ctx.createGain();
    vcoPitchCvInGain.gain.value = 600.0; // +/- 600 cents at full CV
    vcoPitchCvInGain.connect(vco1Sine.detune);
    vcoPitchCvInGain.connect(vco1Tri.detune);
    vcoPitchCvInGain.connect(vco1Saw.detune);
    vcoPitchCvInGain.connect(vco1Sq.detune);
    vcoPitchCvInGain.connect(vco2Saw.detune);
    vcoPitchCvInGain.connect(vco2Sub.detune);

    // 3. VCF (24 dB/oct Cascaded 4-Pole Ladder Low-Pass Filter with Drive Saturation)
    const vcfAudioInGain = ctx.createGain();
    vcfAudioInGain.gain.value = 1.0;

    const vcfDriveGain = ctx.createGain();
    vcfDriveGain.gain.value = 1.5;

    const vcfDriveShaper = ctx.createWaveShaper();
    vcfDriveShaper.curve = this._makeSoftClipCurve(1.6);
    vcfDriveShaper.oversample = '2x';

    const vcfStage1 = ctx.createBiquadFilter();
    vcfStage1.type = 'lowpass';
    vcfStage1.frequency.value = 1200.0;
    vcfStage1.Q.value = 2.0;

    const vcfStage2 = ctx.createBiquadFilter();
    vcfStage2.type = 'lowpass';
    vcfStage2.frequency.value = 1200.0;
    vcfStage2.Q.value = 1.2;

    const vcfOutGain = ctx.createGain();
    vcfOutGain.gain.value = 0.90;

    vcfAudioInGain.connect(vcfDriveGain);
    vcfDriveGain.connect(vcfDriveShaper);
    vcfDriveShaper.connect(vcfStage1);
    vcfStage1.connect(vcfStage2);
    vcfStage2.connect(vcfOutGain);

    // VCF Cutoff CV Input (scales CV to cents on both ladder filter poles)
    const vcfCutoffCvInGain = ctx.createGain();
    vcfCutoffCvInGain.gain.value = 2200.0;
    vcfCutoffCvInGain.connect(vcfStage1.detune);
    vcfCutoffCvInGain.connect(vcfStage2.detune);

    // 4. ADSR Envelope Generator (ConstantSourceNode -> envCvNode -> envCvOutGain & internal VCA gate)
    const envSource = ctx.createConstantSource();
    envSource.offset.value = 1.0;
    const envContourGain = ctx.createGain();
    envContourGain.gain.value = 0.0;
    const envCvOutGain = ctx.createGain();
    envCvOutGain.gain.value = 1.0;

    envSource.connect(envContourGain);
    envContourGain.connect(envCvOutGain);

    // 5. Master Synth VCA
    const vcaAudioInGain = ctx.createGain();
    vcaAudioInGain.gain.value = 1.0;

    const vcaGateGain = ctx.createGain();
    vcaGateGain.gain.value = 0.0; // Driven by envContourGain + vcaCvInGain
    envContourGain.connect(vcaGateGain.gain);

    const vcaCvInGain = ctx.createGain();
    vcaCvInGain.gain.value = 0.5;
    vcaCvInGain.connect(vcaGateGain.gain);

    vcaAudioInGain.connect(vcaGateGain);

    // 6. Modulation LFO
    const lfoOsc = ctx.createOscillator();
    lfoOsc.type = 'triangle';
    lfoOsc.frequency.value = 3.5;
    const lfoCvOutGain = ctx.createGain();
    lfoCvOutGain.gain.value = 0.20;
    lfoOsc.connect(lfoCvOutGain);

    // 7. BBD Analogue Delay
    const delayAudioInGain = ctx.createGain();
    delayAudioInGain.gain.value = 1.0;
    const delayNode = ctx.createDelay(2.0);
    delayNode.delayTime.value = 0.30;
    const delayToneFilter = ctx.createBiquadFilter();
    delayToneFilter.type = 'lowpass';
    delayToneFilter.frequency.value = 2600.0;
    const delayFeedbackGain = ctx.createGain();
    delayFeedbackGain.gain.value = 0.38;
    const delayWetGain = ctx.createGain();
    delayWetGain.gain.value = 0.25;

    delayAudioInGain.connect(delayNode);
    delayNode.connect(delayToneFilter);
    delayToneFilter.connect(delayFeedbackGain);
    delayFeedbackGain.connect(delayNode);
    delayToneFilter.connect(delayWetGain);

    // 8. Turntable Phono Preamp Output & Direct Deck Monitor
    const phonoPreampOutGain = ctx.createGain();
    phonoPreampOutGain.gain.value = 0.85;
    const phonoDirectMonitorGain = ctx.createGain();
    phonoDirectMonitorGain.gain.value = 0.72;
    phonoPreampOutGain.connect(phonoDirectMonitorGain);

    // 9. Master Console Bus -> Soft Clipper -> Master Volume -> Analyser -> Destination
    const masterBus = ctx.createGain();
    masterBus.gain.value = 0.85;

    const masterClipper = ctx.createWaveShaper();
    masterClipper.curve = this._makeSoftClipCurve(1.35);
    masterClipper.oversample = '2x';

    const masterOutGain = ctx.createGain();
    masterOutGain.gain.value = this.masterVolume;

    this.analyser = ctx.createAnalyser();
    this.analyser.fftSize = 2048;
    this.analyser.smoothingTimeConstant = 0.65;
    this.timeDomainBuf = new Float32Array(this.analyser.fftSize);
    this.freqDomainBuf = new Uint8Array(this.analyser.frequencyBinCount);

    vcaGateGain.connect(masterBus);
    delayWetGain.connect(masterBus);
    phonoDirectMonitorGain.connect(masterBus);

    masterBus.connect(masterClipper);
    masterClipper.connect(masterOutGain);
    masterOutGain.connect(this.analyser);
    this.analyser.connect(ctx.destination);

    // Start continuous oscillators
    vco1Sine.start();
    vco1Tri.start();
    vco1Saw.start();
    vco1Sq.start();
    vco2Saw.start();
    vco2Sub.start();
    envSource.start();
    lfoOsc.start();

    this.nodes = {
      vco1Sine, vco1Tri, vco1Saw, vco1Sq,
      gSine, gTri, gSaw, gSq, vco1OutGain,
      vco2Saw, vco2Sub, gVco2Main, gVco2Sub, vco2OutGain,
      vcoPitchCvInGain,
      vcfAudioInGain, vcfDriveGain, vcfDriveShaper, vcfStage1, vcfStage2, vcfOutGain, vcfCutoffCvInGain,
      envSource, envContourGain, envCvOutGain,
      vcaAudioInGain, vcaGateGain, vcaCvInGain,
      lfoOsc, lfoCvOutGain,
      delayAudioInGain, delayNode, delayToneFilter, delayFeedbackGain, delayWetGain,
      phonoPreampOutGain, phonoDirectMonitorGain,
      masterBus, masterClipper, masterOutGain
    };

    // Map contract socket IDs to Web Audio nodes
    this.portMap = {
      socket_vco1_out: vco1OutGain,
      socket_vco2_out: vco2OutGain,
      socket_vcf_out: vcfOutGain,
      socket_env_out: envCvOutGain,
      socket_lfo_out: lfoCvOutGain,
      socket_phono_out: phonoPreampOutGain,
      socket_vco_pitch_cv: vcoPitchCvInGain,
      socket_vcf_in: vcfAudioInGain,
      socket_vcf_cutoff_cv: vcfCutoffCvInGain,
      socket_vca_in: vcaAudioInGain,
      socket_vca_cv: vcaCvInGain,
      socket_dly_in: delayAudioInGain
    };
  }

  async _loadTurntableBuffer() {
    if (!this.ctx) return;
    const resp = await fetch('/assets/audio/chrono_analogue_side_a_33rpm.wav');
    const arrayBuf = await resp.arrayBuffer();
    this.recordBuffer = await this.ctx.decodeAudioData(arrayBuf);
  }

  setKnobValue(knobId, rawValue, immediate = false) {
    const kSpec = this.contract.knobs.find(k => k.id === knobId);
    if (!kSpec) return null;
    const val = Math.max(kSpec.min, Math.min(kSpec.max, rawValue));
    this.knobValues[knobId] = val;
    if (this.ctx) {
      this._applyKnobToAudio(kSpec, val, immediate);
    }
    return val;
  }

  getKnobNormalized(knobId) {
    const kSpec = this.contract.knobs.find(k => k.id === knobId);
    if (!kSpec) return 0.5;
    const val = this.knobValues[knobId] ?? kSpec.default;
    if (kSpec.scale === 'log') {
      return Math.log(val / kSpec.min) / Math.log(kSpec.max / kSpec.min);
    }
    return (val - kSpec.min) / (kSpec.max - kSpec.min);
  }

  setKnobNormalized(knobId, norm01, immediate = false) {
    const kSpec = this.contract.knobs.find(k => k.id === knobId);
    if (!kSpec) return null;
    const n = Math.max(0.0, Math.min(1.0, norm01));
    const val = (kSpec.scale === 'log')
      ? kSpec.min * Math.pow(kSpec.max / kSpec.min, n)
      : kSpec.min + n * (kSpec.max - kSpec.min);
    return this.setKnobValue(knobId, val, immediate);
  }

  _syncAllParameters(immediate = false) {
    for (const kSpec of this.contract.knobs) {
      this._applyKnobToAudio(kSpec, this.knobValues[kSpec.id], immediate);
    }
    this._updateOscillatorFrequencies(immediate);
  }

  _updateOscillatorFrequencies(immediate = false) {
    if (!this.ctx || !this.nodes.vco1Saw) return;
    const now = this.ctx.currentTime;
    const tc = immediate ? 0.001 : 0.012;
    const baseFreq = this.currentNoteFreq || 130.81;

    const vco1Semi = this.knobValues.knob_vco1_pitch || 0.0;
    const f1 = baseFreq * Math.pow(2.0, vco1Semi / 12.0);
    for (const osc of [this.nodes.vco1Sine, this.nodes.vco1Tri, this.nodes.vco1Saw, this.nodes.vco1Sq]) {
      osc.frequency.setTargetAtTime(f1, now, tc);
    }

    const vco2Cents = this.knobValues.knob_vco2_detune || 8.0;
    const f2 = baseFreq * Math.pow(2.0, vco2Cents / 1200.0);
    this.nodes.vco2Saw.frequency.setTargetAtTime(f2, now, tc);
    this.nodes.vco2Sub.frequency.setTargetAtTime(f2 * 0.5, now, tc);
  }

  _applyKnobToAudio(kSpec, val, immediate = false) {
    if (!this.ctx || !this.nodes.vco1Saw) return;
    const now = this.ctx.currentTime;
    const tc = immediate ? 0.001 : (kSpec.smoothing_tc_s || 0.015);
    const n = this.nodes;

    switch (kSpec.id) {
      case 'knob_vco1_pitch':
      case 'knob_vco2_detune':
        this._updateOscillatorFrequencies(immediate);
        break;
      case 'knob_vco1_wave': {
        // 0.0=Sine, 0.333=Tri, 0.667=Saw, 1.0=Square
        const pos = val * 3.0;
        const wSine = Math.max(0.0, 1.0 - Math.abs(pos - 0.0));
        const wTri = Math.max(0.0, 1.0 - Math.abs(pos - 1.0));
        const wSaw = Math.max(0.0, 1.0 - Math.abs(pos - 2.0));
        const wSq = Math.max(0.0, 1.0 - Math.abs(pos - 3.0));
        n.gSine.gain.setTargetAtTime(wSine, now, tc);
        n.gTri.gain.setTargetAtTime(wTri, now, tc);
        n.gSaw.gain.setTargetAtTime(wSaw, now, tc);
        n.gSq.gain.setTargetAtTime(wSq, now, tc);
        break;
      }
      case 'knob_vco2_mix':
        n.vco2OutGain.gain.setTargetAtTime(val * 0.65, now, tc);
        n.gVco2Sub.gain.setTargetAtTime(0.25 + val * 0.55, now, tc);
        break;
      case 'knob_vcf_cutoff':
        n.vcfStage1.frequency.setTargetAtTime(val, now, tc);
        n.vcfStage2.frequency.setTargetAtTime(Math.min(18000, val * 1.12), now, tc);
        break;
      case 'knob_vcf_resonance':
        n.vcfStage1.Q.setTargetAtTime(val * 0.65, now, tc);
        n.vcfStage2.Q.setTargetAtTime(Math.max(0.5, val * 0.35), now, tc);
        break;
      case 'knob_vcf_env_amt':
        n.vcfCutoffCvInGain.gain.setTargetAtTime(val, now, tc);
        break;
      case 'knob_vcf_drive':
        n.vcfDriveGain.gain.setTargetAtTime(val, now, tc);
        break;
      case 'knob_lfo_rate':
        n.lfoOsc.frequency.setTargetAtTime(val, now, tc);
        break;
      case 'knob_lfo_depth':
        n.lfoCvOutGain.gain.setTargetAtTime(val, now, tc);
        break;
      case 'knob_dly_time':
        n.delayNode.delayTime.setTargetAtTime(val, now, tc);
        break;
      case 'knob_dly_mix':
        n.delayWetGain.gain.setTargetAtTime(val, now, tc);
        n.delayFeedbackGain.gain.setTargetAtTime(Math.min(0.72, 0.15 + val * 0.60), now, tc);
        break;
      default:
        break;
    }
  }

  /**
   * Validates a proposed patch connection between socketA and socketB against contract.json rules.
   */
  validatePatchConnection(socketAId, socketBId) {
    if (socketAId === socketBId) {
      return { valid: false, code: 'self_connection', message: 'Cannot patch a socket to itself.' };
    }
    const sA = this.contract.patch_sockets.find(s => s.id === socketAId);
    const sB = this.contract.patch_sockets.find(s => s.id === socketBId);
    if (!sA || !sB) {
      return { valid: false, code: 'unknown_socket', message: 'Unknown patch socket ID.' };
    }
    if (sA.direction === 'output' && sB.direction === 'output') {
      return { valid: false, code: 'unsafe_output_to_output', message: 'Unsafe routing: cannot tie two low-impedance outputs together.' };
    }
    if (sA.direction === 'input' && sB.direction === 'input') {
      return { valid: false, code: 'invalid_input_to_input', message: 'Invalid routing: cannot connect two input sockets without an output source.' };
    }

    // Normalize direction so source is always output and target is always input
    const source = (sA.direction === 'output') ? sA : sB;
    const target = (sA.direction === 'input') ? sA : sB;

    if (source.id === 'socket_vcf_out' && target.id === 'socket_vcf_in') {
      return { valid: false, code: 'unsafe_feedback_loop', message: 'Unsafe direct filter feedback loop rejected to prevent runaway self-oscillation clipping.' };
    }
    if (source.port_type === 'cv_out' && target.port_type === 'audio_in') {
      return { valid: false, code: 'dc_offset_cv_to_audio_in', message: 'Rejected: unipolar/low-frequency CV into AC audio input introduces DC offset.' };
    }

    const allowed = this.contract.patch_rules.allowed_port_pairs.some(
      p => p.from === source.port_type && p.to === target.port_type
    );
    if (!allowed) {
      return { valid: false, code: 'incompatible_ports', message: `Incompatible port types (${source.port_type} -> ${target.port_type}).` };
    }

    return {
      valid: true,
      code: 'ok',
      fromSocketId: source.id,
      toSocketId: target.id,
      sourceSocket: source,
      targetSocket: target,
      message: `Patched ${source.label} -> ${target.label}`
    };
  }

  addPatchCable(socketAId, socketBId, color = null) {
    const check = this.validatePatchConnection(socketAId, socketBId);
    if (!check.valid) return check;

    const existingIdx = this.cables.findIndex(
      c => c.fromSocketId === check.fromSocketId && c.toSocketId === check.toSocketId
    );
    if (existingIdx !== -1) {
      return { valid: true, duplicate: true, cable: this.cables[existingIdx], message: 'Patch cable already connected.' };
    }

    const palette = ['#d4573b', '#d99b38', '#4593a8', '#68a36f', '#c76d85', '#e0d4b8'];
    const cable = {
      id: `cable_${check.fromSocketId}__${check.toSocketId}`,
      fromSocketId: check.fromSocketId,
      toSocketId: check.toSocketId,
      color: color || palette[this.cables.length % palette.length]
    };
    this.cables.push(cable);
    this._rebuildPatchRouting();
    return { valid: true, cable, message: check.message };
  }

  removePatchCable(cableIdOrSocketId) {
    const before = this.cables.length;
    this.cables = this.cables.filter(
      c => c.id !== cableIdOrSocketId && c.fromSocketId !== cableIdOrSocketId && c.toSocketId !== cableIdOrSocketId
    );
    if (this.cables.length !== before) {
      this._rebuildPatchRouting();
      return true;
    }
    return false;
  }

  clearAllCables() {
    this.cables = [];
    this._rebuildPatchRouting();
  }

  _rebuildPatchRouting() {
    if (!this.ctx || !this.nodes.vco1OutGain) return;
    const n = this.nodes;

    // Disconnect all patchable output nodes first
    const outputs = ['socket_vco1_out', 'socket_vco2_out', 'socket_vcf_out', 'socket_env_out', 'socket_lfo_out', 'socket_phono_out'];
    for (const outId of outputs) {
      try { this.portMap[outId].disconnect(); } catch (e) {}
    }

    // Keep turntable direct monitor connected unless PHONO OUT is patched into the synth rack!
    const phonoPatchedIntoSynth = this.cables.some(c => c.fromSocketId === 'socket_phono_out');
    if (!phonoPatchedIntoSynth) {
      n.phonoPreampOutGain.connect(n.phonoDirectMonitorGain);
    }

    // Default normalled connection: VCF OUT -> VCA IN if nothing is explicitly patched into VCA IN
    const vcaInPatched = this.cables.some(c => c.toSocketId === 'socket_vca_in');
    if (!vcaInPatched) {
      n.vcfOutGain.connect(n.vcaAudioInGain);
    }

    // Connect all active user patch cables
    for (const c of this.cables) {
      const srcNode = this.portMap[c.fromSocketId];
      const dstNode = this.portMap[c.toSocketId];
      if (srcNode && dstNode) {
        srcNode.connect(dstNode);
      }
    }

    // If PHONO OUT is patched into VCF IN and nothing is holding the VCA gate open,
    // bias VCA gate slightly so external turntable audio through the filter is audible immediately!
    const now = this.ctx.currentTime;
    if (phonoPatchedIntoSynth && !this.gateOpen) {
      n.vcaGateGain.gain.setTargetAtTime(0.65, now, 0.02);
    } else if (!this.gateOpen) {
      n.vcaGateGain.gain.setTargetAtTime(0.0, now, 0.02);
    }
  }

  noteOn(midiNote, source = 'pointer') {
    const keySpec = this.contract.keyboard.keys.find(k => k.midi_note === midiNote);
    if (!keySpec) return;

    if (!this.activeNotes.has(midiNote)) {
      this.activeNotes.set(midiNote, new Set());
    }
    this.activeNotes.get(midiNote).add(source);

    this.currentMidiNote = midiNote;
    this.currentNoteFreq = keySpec.frequency_hz;
    this._updateOscillatorFrequencies(false);
    this._triggerEnvelopeAttack();
  }

  noteOff(midiNote, source = 'pointer') {
    if (!this.activeNotes.has(midiNote)) return;
    const sources = this.activeNotes.get(midiNote);
    sources.delete(source);
    if (sources.size === 0) {
      this.activeNotes.delete(midiNote);
    }

    if (this.activeNotes.size > 0) {
      // Highest remaining held note takes priority (classic mono-synth highest-note priority)
      const remainingNotes = Array.from(this.activeNotes.keys()).sort((a, b) => b - a);
      const nextMidi = remainingNotes[0];
      const nextKey = this.contract.keyboard.keys.find(k => k.midi_note === nextMidi);
      if (nextKey) {
        this.currentMidiNote = nextMidi;
        this.currentNoteFreq = nextKey.frequency_hz;
        this._updateOscillatorFrequencies(false);
      }
    } else {
      this.currentMidiNote = null;
      this._triggerEnvelopeRelease();
    }
  }

  releaseAllNotes() {
    this.activeNotes.clear();
    this.currentMidiNote = null;
    this._triggerEnvelopeRelease(true);
  }

  _triggerEnvelopeAttack() {
    this.gateOpen = true;
    if (!this.ctx || !this.nodes.envContourGain) return;
    const now = this.ctx.currentTime;
    const atk = Math.max(0.003, this.knobValues.knob_env_attack || 0.015);
    const dec = Math.max(0.02, this.knobValues.knob_env_decay || 0.35);
    const sus = Math.max(0.0, Math.min(1.0, this.knobValues.knob_env_sustain ?? 0.60));

    const g = this.nodes.envContourGain.gain;
    g.cancelScheduledValues(now);
    g.setValueAtTime(g.value, now);
    g.linearRampToValueAtTime(0.85, now + atk);
    g.setTargetAtTime(0.85 * sus, now + atk, dec / 3.0);
  }

  _triggerEnvelopeRelease(fast = false) {
    this.gateOpen = false;
    if (!this.ctx || !this.nodes.envContourGain) return;
    const now = this.ctx.currentTime;
    const rel = fast ? 0.03 : Math.max(0.01, this.knobValues.knob_env_release || 0.45);
    const g = this.nodes.envContourGain.gain;
    g.cancelScheduledValues(now);
    g.setValueAtTime(g.value, now);
    g.setTargetAtTime(0.0, now, rel / 4.0);
  }

  loadPreset(presetId) {
    const preset = this.contract.audio_graph.presets.find(p => p.id === presetId);
    if (!preset) return false;
    this.releaseAllNotes();

    // Reset knobs to defaults then overlay preset values
    for (const k of this.contract.knobs) {
      this.knobValues[k.id] = (preset.knobs && preset.knobs[k.id] !== undefined)
        ? preset.knobs[k.id]
        : k.default;
    }
    this._syncAllParameters(false);

    this.cables = [];
    for (const [src, dst] of (preset.cables || [])) {
      this.addPatchCable(src, dst);
    }
    return true;
  }

  /**
   * Turntable controls: motor, tonearm cueing, 33 1/3 vs 45 RPM with position preservation
   */
  setTurntableMotor(motorOn) {
    this.motorOn = Boolean(motorOn);
    this._updateTurntableState();
  }

  setTonearmLowered(lowered) {
    this.tonearmLowered = Boolean(lowered);
    if (this.tonearmLowered && !this.motorOn) {
      // Lowering the tonearm starts playable record automatically if motor was off
      this.motorOn = true;
    }
    this._updateTurntableState();
  }

  setTurntableRpm(rpmPreset) {
    const targetRpm = (Number(rpmPreset) > 40) ? 45.0 : 33.333333;
    if (this.ctx && this._isRecordAudiblyPlaying() && this.recordBuffer) {
      const now = this.ctx.currentTime;
      const oldRate = this.getPlaybackRate();
      const elapsed = (now - this.recordStartCtxTime) * oldRate;
      this.recordOffsetSec = (this.recordOffsetSec + elapsed) % this.recordBuffer.duration;
      this.recordStartCtxTime = now;
    }
    this.rpm = targetRpm;
    if (this.recordSource && this.ctx) {
      this.recordSource.playbackRate.setValueAtTime(this.getPlaybackRate(), this.ctx.currentTime);
    }
    this._updateTurntableState();
  }

  getPlaybackRate() {
    return this.rpm / (this.contract.turntable.native_rpm || 33.333333);
  }

  getPlatterAngularVelocityRadS() {
    if (!this.motorOn) return 0.0;
    return (this.rpm * 2.0 * Math.PI) / 60.0;
  }

  _isRecordAudiblyPlaying() {
    return this.motorOn && this.tonearmLowered;
  }

  _updateTurntableState() {
    const shouldPlayAudio = this._isRecordAudiblyPlaying();

    if (shouldPlayAudio) {
      this.turntableState = (this.rpm > 40) ? 'playing_45' : 'playing_33';
      this._startRecordSourceIfNeeded();
    } else {
      this._stopRecordSourceAndSaveOffset();
      if (this.motorOn && !this.tonearmLowered) {
        this.turntableState = 'cued_spinning';
      } else if (!this.motorOn && this.tonearmLowered) {
        this.turntableState = 'paused_on_record';
      } else {
        this.turntableState = 'stopped_rest';
      }
    }
  }

  _startRecordSourceIfNeeded() {
    if (!this.ctx || !this.recordBuffer || this.recordSource) return;
    const now = this.ctx.currentTime;
    const src = this.ctx.createBufferSource();
    src.buffer = this.recordBuffer;
    src.loop = true;
    src.playbackRate.value = this.getPlaybackRate();
    src.connect(this.nodes.phonoPreampOutGain);
    this.recordStartCtxTime = now;
    src.start(0, this.recordOffsetSec % this.recordBuffer.duration);
    this.recordSource = src;
  }

  _stopRecordSourceAndSaveOffset() {
    if (!this.recordSource || !this.ctx || !this.recordBuffer) return;
    const now = this.ctx.currentTime;
    const elapsed = (now - this.recordStartCtxTime) * this.getPlaybackRate();
    this.recordOffsetSec = (this.recordOffsetSec + elapsed) % this.recordBuffer.duration;
    try {
      this.recordSource.stop();
      this.recordSource.disconnect();
    } catch (e) {}
    this.recordSource = null;
  }

  getTurntablePlaybackPositionSec() {
    if (!this.recordBuffer) return 0.0;
    if (this.recordSource && this.ctx && this._isRecordAudiblyPlaying()) {
      const elapsed = (this.ctx.currentTime - this.recordStartCtxTime) * this.getPlaybackRate();
      return (this.recordOffsetSec + elapsed) % this.recordBuffer.duration;
    }
    return this.recordOffsetSec;
  }

  setMasterVolume(vol01) {
    this.masterVolume = Math.max(0.0, Math.min(1.0, vol01));
    if (this.ctx && this.nodes.masterOutGain) {
      const target = this.isMuted ? 0.0 : this.masterVolume;
      this.nodes.masterOutGain.gain.setTargetAtTime(target, this.ctx.currentTime, 0.015);
    }
  }

  setMuted(muted) {
    this.isMuted = Boolean(muted);
    this.setMasterVolume(this.masterVolume);
  }

  resetAllSound() {
    this.releaseAllNotes();
    this.motorOn = false;
    this.tonearmLowered = false;
    this._updateTurntableState();
    this.recordOffsetSec = 0.0;
    this.tonearmProgress = 0.0;
    if (this.ctx && this.nodes.envContourGain) {
      const now = this.ctx.currentTime;
      this.nodes.envContourGain.gain.cancelScheduledValues(now);
      this.nodes.envContourGain.gain.setValueAtTime(0.0, now);
      this.nodes.vcaGateGain.gain.cancelScheduledValues(now);
      this.nodes.vcaGateGain.gain.setValueAtTime(0.0, now);
      if (this.nodes.delayFeedbackGain && this.nodes.delayWetGain) {
        this.nodes.delayFeedbackGain.gain.cancelScheduledValues(now);
        this.nodes.delayFeedbackGain.gain.setValueAtTime(0.0, now);
        this.nodes.delayWetGain.gain.cancelScheduledValues(now);
        this.nodes.delayWetGain.gain.setValueAtTime(0.0, now);
        this.nodes.delayFeedbackGain.gain.setTargetAtTime(0.38, now + 0.12, 0.02);
      }
    }
  }

  getFastWaveTelemetry() {
    if (!this.analyser || !this.timeDomainBuf) {
      return { rms: 0.0, peak: 0.0, clipping: false };
    }
    this.analyser.getFloatTimeDomainData(this.timeDomainBuf);
    let sumSq = 0.0;
    let peak = 0.0;
    const len = this.timeDomainBuf.length;
    for (let i = 0; i < len; i += 2) {
      const a = Math.abs(this.timeDomainBuf[i]);
      sumSq += a * a;
      if (a > peak) peak = a;
    }
    const rms = Math.sqrt(sumSq / (len * 0.5));
    return {
      rms: Number(rms.toFixed(4)),
      peak: Number(peak.toFixed(4)),
      clipping: peak > 0.98
    };
  }

  getTelemetry() {
    if (!this.analyser || !this.timeDomainBuf) {
      return { rms: 0.0, peak: 0.0, clipping: false, centroidHz: 0.0 };
    }
    this.analyser.getFloatTimeDomainData(this.timeDomainBuf);
    this.analyser.getByteFrequencyData(this.freqDomainBuf);

    let sumSq = 0.0;
    let peak = 0.0;
    for (let i = 0; i < this.timeDomainBuf.length; i++) {
      const a = Math.abs(this.timeDomainBuf[i]);
      sumSq += a * a;
      if (a > peak) peak = a;
    }
    const rms = Math.sqrt(sumSq / this.timeDomainBuf.length);

    let weightedSum = 0.0;
    let magSum = 0.0;
    const binHz = (this.ctx ? this.ctx.sampleRate : 44100) / this.analyser.fftSize;
    for (let i = 0; i < this.freqDomainBuf.length; i++) {
      const m = this.freqDomainBuf[i];
      weightedSum += i * binHz * m;
      magSum += m;
    }
    const centroidHz = magSum > 0 ? (weightedSum / magSum) : 0.0;

    return {
      rms: Number(rms.toFixed(4)),
      peak: Number(peak.toFixed(4)),
      clipping: peak > 0.98,
      centroidHz: Number(centroidHz.toFixed(1))
    };
  }
}
