import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def build_contract():
    # 16 useful knobs across 4 modules (VCO, VCF, ENV, LFO/DELAY)
    knobs = [
        # Module 1: VCO (Dual Oscillator)
        {
            "id": "knob_vco1_pitch",
            "node_name": "Knob_01_VCO1_Pitch",
            "module": "VCO",
            "label": "VCO 1 TUNE",
            "parameter": "vco1.pitchSemitones",
            "unit": "st",
            "min": -24.0,
            "max": 24.0,
            "default": 0.0,
            "scale": "linear",
            "smoothing_tc_s": 0.015,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.345, 0.095, 0.012]
        },
        {
            "id": "knob_vco1_wave",
            "node_name": "Knob_02_VCO1_Wave",
            "module": "VCO",
            "label": "VCO 1 WAVE",
            "parameter": "vco1.waveformMorph",
            "unit": "shape",
            "min": 0.0,
            "max": 1.0,
            "default": 0.67,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.245, 0.095, 0.012]
        },
        {
            "id": "knob_vco2_detune",
            "node_name": "Knob_03_VCO2_Detune",
            "module": "VCO",
            "label": "VCO 2 DETUNE",
            "parameter": "vco2.detuneCents",
            "unit": "ct",
            "min": -1200.0,
            "max": 1200.0,
            "default": 8.0,
            "scale": "linear",
            "smoothing_tc_s": 0.015,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.345, 0.010, 0.012]
        },
        {
            "id": "knob_vco2_mix",
            "node_name": "Knob_04_VCO2_Mix",
            "module": "VCO",
            "label": "VCO 2 / SUB MIX",
            "parameter": "vco2.subMix",
            "unit": "lvl",
            "min": 0.0,
            "max": 1.0,
            "default": 0.45,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.245, 0.010, 0.012]
        },
        # Module 2: VCF (24dB Ladder Filter)
        {
            "id": "knob_vcf_cutoff",
            "node_name": "Knob_05_VCF_Cutoff",
            "module": "VCF",
            "label": "CUTOFF FREQ",
            "parameter": "vcf.cutoffHz",
            "unit": "Hz",
            "min": 40.0,
            "max": 16000.0,
            "default": 1200.0,
            "scale": "log",
            "smoothing_tc_s": 0.015,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.145, 0.095, 0.012]
        },
        {
            "id": "knob_vcf_resonance",
            "node_name": "Knob_06_VCF_Resonance",
            "module": "VCF",
            "label": "RESONANCE",
            "parameter": "vcf.resonanceQ",
            "unit": "Q",
            "min": 0.7,
            "max": 18.0,
            "default": 2.8,
            "scale": "linear",
            "smoothing_tc_s": 0.015,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.045, 0.095, 0.012]
        },
        {
            "id": "knob_vcf_env_amt",
            "node_name": "Knob_07_VCF_EnvAmt",
            "module": "VCF",
            "label": "ENV MOD DEPTH",
            "parameter": "vcf.envModCents",
            "unit": "ct",
            "min": -4800.0,
            "max": 4800.0,
            "default": 2200.0,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.145, 0.010, 0.012]
        },
        {
            "id": "knob_vcf_drive",
            "node_name": "Knob_08_VCF_Drive",
            "module": "VCF",
            "label": "LADDER DRIVE",
            "parameter": "vcf.drive",
            "unit": "x",
            "min": 1.0,
            "max": 5.0,
            "default": 1.5,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [-0.045, 0.010, 0.012]
        },
        # Module 3: ENV (ADSR Envelope Generator)
        {
            "id": "knob_env_attack",
            "node_name": "Knob_09_ENV_Attack",
            "module": "ENV",
            "label": "ATTACK",
            "parameter": "env.attackS",
            "unit": "s",
            "min": 0.003,
            "max": 2.5,
            "default": 0.015,
            "scale": "log",
            "smoothing_tc_s": 0.01,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.055, 0.095, 0.012]
        },
        {
            "id": "knob_env_decay",
            "node_name": "Knob_10_ENV_Decay",
            "module": "ENV",
            "label": "DECAY",
            "parameter": "env.decayS",
            "unit": "s",
            "min": 0.02,
            "max": 3.0,
            "default": 0.35,
            "scale": "log",
            "smoothing_tc_s": 0.01,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.155, 0.095, 0.012]
        },
        {
            "id": "knob_env_sustain",
            "node_name": "Knob_11_ENV_Sustain",
            "module": "ENV",
            "label": "SUSTAIN",
            "parameter": "env.sustainLevel",
            "unit": "lvl",
            "min": 0.0,
            "max": 1.0,
            "default": 0.60,
            "scale": "linear",
            "smoothing_tc_s": 0.01,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.055, 0.010, 0.012]
        },
        {
            "id": "knob_env_release",
            "node_name": "Knob_12_ENV_Release",
            "module": "ENV",
            "label": "RELEASE",
            "parameter": "env.releaseS",
            "unit": "s",
            "min": 0.01,
            "max": 4.0,
            "default": 0.45,
            "scale": "log",
            "smoothing_tc_s": 0.01,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.155, 0.010, 0.012]
        },
        # Module 4: LFO & BBD DELAY
        {
            "id": "knob_lfo_rate",
            "node_name": "Knob_13_LFO_Rate",
            "module": "LFO_DELAY",
            "label": "LFO RATE",
            "parameter": "lfo.rateHz",
            "unit": "Hz",
            "min": 0.1,
            "max": 20.0,
            "default": 3.5,
            "scale": "log",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.255, 0.095, 0.012]
        },
        {
            "id": "knob_lfo_depth",
            "node_name": "Knob_14_LFO_Depth",
            "module": "LFO_DELAY",
            "label": "LFO DEPTH",
            "parameter": "lfo.depth",
            "unit": "lvl",
            "min": 0.0,
            "max": 1.0,
            "default": 0.20,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.345, 0.095, 0.012]
        },
        {
            "id": "knob_dly_time",
            "node_name": "Knob_15_DLY_Time",
            "module": "LFO_DELAY",
            "label": "DELAY TIME",
            "parameter": "delay.timeS",
            "unit": "s",
            "min": 0.04,
            "max": 0.85,
            "default": 0.30,
            "scale": "linear",
            "smoothing_tc_s": 0.035,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.255, 0.010, 0.012]
        },
        {
            "id": "knob_dly_mix",
            "node_name": "Knob_16_DLY_Mix",
            "module": "LFO_DELAY",
            "label": "DELAY MIX",
            "parameter": "delay.wetMix",
            "unit": "lvl",
            "min": 0.0,
            "max": 0.85,
            "default": 0.25,
            "scale": "linear",
            "smoothing_tc_s": 0.02,
            "pivot_axis_threejs": "Z",
            "angle_min_deg": -135.0,
            "angle_max_deg": 135.0,
            "panel_local_pos_m": [0.345, 0.010, 0.012]
        }
    ]

    # 12 functional patch sockets (6 outputs, 6 inputs)
    patch_sockets = [
        # Row 1 (Y = -0.076 m on faceplate): 6 Outputs
        {
            "id": "socket_vco1_out",
            "node_name": "Socket_01_VCO1_Out",
            "module": "VCO",
            "label": "VCO 1 OUT",
            "direction": "output",
            "port_type": "audio_out",
            "signal_range": "-1.0 to +1.0 audio",
            "web_audio_node": "vco1OutGain",
            "panel_local_pos_m": [-0.325, -0.076, 0.008]
        },
        {
            "id": "socket_vco2_out",
            "node_name": "Socket_02_VCO2_Out",
            "module": "VCO",
            "label": "VCO 2 OUT",
            "direction": "output",
            "port_type": "audio_out",
            "signal_range": "-1.0 to +1.0 audio",
            "web_audio_node": "vco2OutGain",
            "panel_local_pos_m": [-0.195, -0.076, 0.008]
        },
        {
            "id": "socket_vcf_out",
            "node_name": "Socket_03_VCF_Out",
            "module": "VCF",
            "label": "VCF OUT",
            "direction": "output",
            "port_type": "audio_out",
            "signal_range": "-1.0 to +1.0 audio",
            "web_audio_node": "vcfOutGain",
            "panel_local_pos_m": [-0.065, -0.076, 0.008]
        },
        {
            "id": "socket_env_out",
            "node_name": "Socket_04_ENV_Out",
            "module": "ENV",
            "label": "ENV CV OUT",
            "direction": "output",
            "port_type": "cv_out",
            "signal_range": "0.0 to +1.0 CV",
            "web_audio_node": "envCvOutGain",
            "panel_local_pos_m": [0.065, -0.076, 0.008]
        },
        {
            "id": "socket_lfo_out",
            "node_name": "Socket_05_LFO_Out",
            "module": "LFO_DELAY",
            "label": "LFO CV OUT",
            "direction": "output",
            "port_type": "cv_out",
            "signal_range": "-1.0 to +1.0 CV",
            "web_audio_node": "lfoCvOutGain",
            "panel_local_pos_m": [0.195, -0.076, 0.008]
        },
        {
            "id": "socket_phono_out",
            "node_name": "Socket_06_Phono_Out",
            "module": "LFO_DELAY",
            "label": "PHONO OUT",
            "direction": "output",
            "port_type": "audio_out",
            "signal_range": "-1.0 to +1.0 audio",
            "web_audio_node": "phonoPreampOutGain",
            "panel_local_pos_m": [0.325, -0.076, 0.008]
        },
        # Row 2 (Y = -0.128 m on faceplate): 6 Inputs
        {
            "id": "socket_vco_pitch_cv",
            "node_name": "Socket_07_VCO_PitchCV",
            "module": "VCO",
            "label": "VCO PITCH CV",
            "direction": "input",
            "port_type": "cv_in",
            "signal_range": "CV -> +/-1200 cents",
            "web_audio_node": "vcoPitchCvInGain",
            "panel_local_pos_m": [-0.325, -0.128, 0.008]
        },
        {
            "id": "socket_vcf_in",
            "node_name": "Socket_08_VCF_In",
            "module": "VCF",
            "label": "VCF AUDIO IN",
            "direction": "input",
            "port_type": "audio_in",
            "signal_range": "Audio -> Ladder Filter In",
            "web_audio_node": "vcfAudioInGain",
            "panel_local_pos_m": [-0.195, -0.128, 0.008]
        },
        {
            "id": "socket_vcf_cutoff_cv",
            "node_name": "Socket_09_VCF_CutoffCV",
            "module": "VCF",
            "label": "VCF CUTOFF CV",
            "direction": "input",
            "port_type": "cv_in",
            "signal_range": "CV -> +/-3600 cents",
            "web_audio_node": "vcfCutoffCvInGain",
            "panel_local_pos_m": [-0.065, -0.128, 0.008]
        },
        {
            "id": "socket_vca_in",
            "node_name": "Socket_10_VCA_In",
            "module": "ENV",
            "label": "VCA AUDIO IN",
            "direction": "input",
            "port_type": "audio_in",
            "signal_range": "Audio -> Master VCA In",
            "web_audio_node": "vcaAudioInGain",
            "panel_local_pos_m": [0.065, -0.128, 0.008]
        },
        {
            "id": "socket_vca_cv",
            "node_name": "Socket_11_VCA_CV",
            "module": "ENV",
            "label": "VCA GAIN CV",
            "direction": "input",
            "port_type": "cv_in",
            "signal_range": "CV -> VCA Gain Mod",
            "web_audio_node": "vcaCvInGain",
            "panel_local_pos_m": [0.195, -0.128, 0.008]
        },
        {
            "id": "socket_dly_in",
            "node_name": "Socket_12_DLY_In",
            "module": "LFO_DELAY",
            "label": "DELAY IN",
            "direction": "input",
            "port_type": "audio_in",
            "signal_range": "Audio -> BBD Delay In",
            "web_audio_node": "delayAudioInGain",
            "panel_local_pos_m": [0.325, -0.128, 0.008]
        }
    ]

    # 25 hinged keys from C3 (MIDI 48) to C5 (MIDI 72)
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    qwerty_map = [
        "Z", "S", "X", "D", "C", "V", "G", "B", "H", "N", "J", "M",
        "Q", "2", "W", "3", "E", "R", "5", "T", "6", "Y", "7", "U", "I"
    ]
    keys = []
    white_idx = 0
    # 15 white keys across 0.72 m bed width -> spacing 0.048 m
    white_spacing = 0.048
    start_x = -0.336
    # Map each semitone offset within octave to white-key index offset
    semitone_x_offset = {
        0: 0.0, 1: 0.55, 2: 1.0, 3: 1.55, 4: 2.0,
        5: 3.0, 6: 3.52, 7: 4.0, 8: 4.50, 9: 5.0, 10: 5.48, 11: 6.0
    }
    for i in range(25):
        midi = 48 + i
        octave = (midi // 12) - 1
        semi = midi % 12
        n_str = f"{note_names[semi]}{octave}"
        safe_name = n_str.replace("#", "s")
        is_sharp = "#" in n_str
        freq = round(440.0 * (2.0 ** ((midi - 69) / 12.0)), 3)
        oct_idx = (midi - 48) // 12
        w_pos = oct_idx * 7.0 + semitone_x_offset[semi]
        x_m = round(start_x + w_pos * white_spacing, 4)
        keys.append({
            "id": f"key_{i+1:02d}_{safe_name.lower()}",
            "node_name": f"Key_{i+1:02d}_{safe_name}",
            "note_name": n_str,
            "midi_note": midi,
            "frequency_hz": freq,
            "is_sharp": is_sharp,
            "qwerty_binding": qwerty_map[i],
            "keybed_local_pos_m": [x_m, 0.012 if is_sharp else 0.0, -0.065]
        })

    contract = {
        "schema_version": "1.0.0",
        "project_id": "modular-synth-turntable-studio-1970s",
        "units": {
            "source_unit_m": 0.1,
            "runtime_unit_m": 1.0,
            "rack_width_m": 0.8,
            "rack_width_source_units": 8.0,
            "rack_backward_tilt_deg": 15.0
        },
        "dimensions": {
            "rack_width_m": 0.8,
            "rack_height_m": 0.42,
            "rack_depth_m": 0.38,
            "keyboard_bed_depth_m": 0.18,
            "turntable_plinth_width_m": 0.42,
            "turntable_plinth_depth_m": 0.35,
            "turntable_platter_diameter_m": 0.30
        },
        "axis_conversion": {
            "blender_axes": {
                "right": "+X",
                "back": "+Y",
                "forward_to_operator": "-Y",
                "up": "+Z"
            },
            "threejs_axes": {
                "right": "+X",
                "up": "+Y",
                "forward_to_operator": "+Z"
            },
            "gltf_export_yup": True,
            "position_mapping": "three_x = blender_x; three_y = blender_z; three_z = -blender_y",
            "rotation_mapping": "Faceplate tilted -15 deg around +X in Three.js (+15 deg in Blender); knobs childed to Synth_Faceplate_Frame rotate around local Z axis; keys childed to Synth_Keybed_Frame rotate around local +X rear hinge axis; platter rotates around local +Y axis."
        },
        "knobs": knobs,
        "patch_sockets": patch_sockets,
        "patch_rules": {
            "allowed_port_pairs": [
                {"from": "audio_out", "to": "audio_in", "description": "Standard audio signal routing"},
                {"from": "cv_out", "to": "cv_in", "description": "Control voltage modulation routing"},
                {"from": "audio_out", "to": "cv_in", "description": "Audio-rate FM / filter modulation"}
            ],
            "rejected_conditions": [
                {"code": "self_connection", "rule": "source_id == target_id", "message": "Cannot patch a socket to itself."},
                {"code": "unsafe_output_to_output", "rule": "source.direction == 'output' and target.direction == 'output'", "message": "Unsafe routing: cannot tie two low-impedance outputs together."},
                {"code": "invalid_input_to_input", "rule": "source.direction == 'input' and target.direction == 'input'", "message": "Invalid routing: cannot patch two inputs together without a signal source."},
                {"code": "dc_offset_cv_to_audio_in", "rule": "source.port_type == 'cv_out' and target.port_type == 'audio_in'", "message": "Rejected: unipolar/low-frequency CV into AC audio input introduces DC thump."},
                {"code": "unsafe_feedback_loop", "rule": "source_id == 'socket_vcf_out' and target_id == 'socket_vcf_in'", "message": "Unsafe direct filter feedback loop rejected to prevent runaway self-oscillation clipping."}
            ],
            "default_normalled_connections": [
                {"from": "socket_vcf_out", "to": "socket_vca_in", "note": "VCF output is normalled to VCA input unless overridden, while VCO1->VCF requires an explicit patch cable for the signature patch interaction or preset load."}
            ],
            "cable_clearance_min_m": 0.012
        },
        "keyboard": {
            "key_count": 25,
            "range": "C3-C5",
            "hinge_axis_threejs": "X",
            "travel_angle_deg": 4.5,
            "spring_return_time_s": 0.065,
            "keys": keys
        },
        "turntable": {
            "platter_node": {
                "node_name": "Turntable_Platter",
                "pivot_axis_threejs": "Y",
                "spin_direction": "clockwise_from_top (-Y rotation in Three.js)",
                "local_pos_m": [-0.035, 0.072, 0.0]
            },
            "tonearm_gimbal_node": {
                "node_name": "Tonearm_Gimbal",
                "yaw_axis_threejs": "Y",
                "pitch_axis_threejs": "X",
                "rest_yaw_deg": 0.0,
                "outer_groove_yaw_deg": -18.5,
                "inner_groove_yaw_deg": -33.5,
                "raised_pitch_deg": 5.5,
                "lowered_pitch_deg": 0.0,
                "local_pos_m": [0.140, 0.086, -0.095]
            },
            "tonearm_headshell_node": {
                "node_name": "Tonearm_Headshell",
                "stylus_contact_height_m": 0.078
            },
            "speed_switch_node": {
                "node_name": "Turntable_SpeedSwitch",
                "local_pos_m": [-0.125, 0.066, 0.135]
            },
            "start_stop_node": {
                "node_name": "Turntable_StartStop",
                "local_pos_m": [-0.168, 0.066, 0.135]
            },
            "native_rpm": 33.333333,
            "rpm_presets": {
                "33": {
                    "rpm": 33.333333,
                    "angular_velocity_rad_s": round(33.333333 * 2.0 * math.pi / 60.0, 5),
                    "playback_rate": 1.0
                },
                "45": {
                    "rpm": 45.0,
                    "angular_velocity_rad_s": round(45.0 * 2.0 * math.pi / 60.0, 5),
                    "playback_rate": 1.35
                }
            },
            "states": [
                "stopped_rest",
                "cued_spinning",
                "playing_33",
                "playing_45",
                "paused_on_record"
            ]
        },
        "audio_graph": {
            "require_user_gesture": True,
            "sample_rate_hz": 44100,
            "max_safe_peak": 0.95,
            "soft_clipper_enabled": True,
            "presets": [
                {
                    "id": "signature_unpatched",
                    "name": "00. Ready to Patch (Connect VCO 1 -> VCF IN)",
                    "cables": [
                        ["socket_vcf_out", "socket_vca_in"],
                        ["socket_env_out", "socket_vcf_cutoff_cv"]
                    ],
                    "knobs": {
                        "knob_vcf_cutoff": 650.0,
                        "knob_vcf_resonance": 3.5,
                        "knob_vcf_env_amt": 1800.0
                    }
                },
                {
                    "id": "signature_patched_lead",
                    "name": "01. Signature 1974 Ladder Lead (VCO 1 -> VCF)",
                    "cables": [
                        ["socket_vco1_out", "socket_vcf_in"],
                        ["socket_vco2_out", "socket_vcf_in"],
                        ["socket_vcf_out", "socket_vca_in"],
                        ["socket_env_out", "socket_vcf_cutoff_cv"],
                        ["socket_vcf_out", "socket_dly_in"]
                    ],
                    "knobs": {
                        "knob_vco1_pitch": 0.0,
                        "knob_vco1_wave": 0.72,
                        "knob_vco2_detune": 9.0,
                        "knob_vco2_mix": 0.55,
                        "knob_vcf_cutoff": 1400.0,
                        "knob_vcf_resonance": 4.2,
                        "knob_vcf_env_amt": 2400.0,
                        "knob_vcf_drive": 1.8,
                        "knob_env_attack": 0.012,
                        "knob_env_decay": 0.42,
                        "knob_env_sustain": 0.55,
                        "knob_env_release": 0.48,
                        "knob_dly_time": 0.32,
                        "knob_dly_mix": 0.28
                    }
                },
                {
                    "id": "velvet_bass_pluck",
                    "name": "02. Warm Walnut Sub Bass",
                    "cables": [
                        ["socket_vco1_out", "socket_vcf_in"],
                        ["socket_vco2_out", "socket_vcf_in"],
                        ["socket_vcf_out", "socket_vca_in"],
                        ["socket_env_out", "socket_vcf_cutoff_cv"]
                    ],
                    "knobs": {
                        "knob_vco1_pitch": -12.0,
                        "knob_vco1_wave": 0.65,
                        "knob_vco2_detune": 5.0,
                        "knob_vco2_mix": 0.80,
                        "knob_vcf_cutoff": 260.0,
                        "knob_vcf_resonance": 5.5,
                        "knob_vcf_env_amt": 3200.0,
                        "knob_vcf_drive": 2.4,
                        "knob_env_attack": 0.005,
                        "knob_env_decay": 0.24,
                        "knob_env_sustain": 0.18,
                        "knob_env_release": 0.20,
                        "knob_dly_mix": 0.08
                    }
                },
                {
                    "id": "cosmic_lfo_sweep",
                    "name": "03. Kosmische LFO Modulated Pad",
                    "cables": [
                        ["socket_vco1_out", "socket_vcf_in"],
                        ["socket_vco2_out", "socket_vcf_in"],
                        ["socket_lfo_out", "socket_vcf_cutoff_cv"],
                        ["socket_lfo_out", "socket_vco_pitch_cv"],
                        ["socket_vcf_out", "socket_vca_in"],
                        ["socket_vcf_out", "socket_dly_in"]
                    ],
                    "knobs": {
                        "knob_vco1_pitch": 0.0,
                        "knob_vco1_wave": 0.50,
                        "knob_vco2_detune": 14.0,
                        "knob_vco2_mix": 0.65,
                        "knob_vcf_cutoff": 980.0,
                        "knob_vcf_resonance": 6.8,
                        "knob_vcf_env_amt": 1200.0,
                        "knob_env_attack": 0.35,
                        "knob_env_decay": 0.85,
                        "knob_env_sustain": 0.75,
                        "knob_env_release": 1.40,
                        "knob_lfo_rate": 4.2,
                        "knob_lfo_depth": 0.45,
                        "knob_dly_time": 0.42,
                        "knob_dly_mix": 0.45
                    }
                },
                {
                    "id": "phono_through_filter",
                    "name": "04. Vinyl Turntable -> Ladder VCF & BBD Delay",
                    "cables": [
                        ["socket_phono_out", "socket_vcf_in"],
                        ["socket_vcf_out", "socket_dly_in"],
                        ["socket_lfo_out", "socket_vcf_cutoff_cv"]
                    ],
                    "knobs": {
                        "knob_vcf_cutoff": 2400.0,
                        "knob_vcf_resonance": 3.2,
                        "knob_lfo_rate": 0.6,
                        "knob_lfo_depth": 0.25,
                        "knob_dly_time": 0.36,
                        "knob_dly_mix": 0.30
                    }
                }
            ]
        }
    }
    return contract


def build_world(contract):
    entities = [
        {
            "entity_id": "studio_desk",
            "node_name": "Studio_Desk_Surface",
            "parent_id": None,
            "category": "environment",
            "coord_tag": "threejs_local_m",
            "position_m": [0.0, -0.02, 0.0],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_studio_slate_desk"
        },
        {
            "entity_id": "synth_cabinet_root",
            "node_name": "Synth_Cabinet_Root",
            "parent_id": None,
            "category": "cabinet",
            "coord_tag": "threejs_local_m",
            "position_m": [-0.22, 0.0, 0.0],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_walnut_cabinet"
        },
        {
            "entity_id": "synth_faceplate_frame",
            "node_name": "Synth_Faceplate_Frame",
            "parent_id": "synth_cabinet_root",
            "category": "panel",
            "coord_tag": "threejs_local_m",
            "position_m": [0.0, 0.255, -0.045],
            "rotation_euler_deg": [-15.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_anodised_panel"
        },
        {
            "entity_id": "synth_keybed_frame",
            "node_name": "Synth_Keybed_Frame",
            "parent_id": "synth_cabinet_root",
            "category": "keybed",
            "coord_tag": "threejs_local_m",
            "position_m": [0.0, 0.048, 0.165],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_anodised_trim"
        }
    ]

    # Add 16 knobs
    for k in contract["knobs"]:
        entities.append({
            "entity_id": k["id"],
            "node_name": k["node_name"],
            "parent_id": "synth_faceplate_frame",
            "category": "knob",
            "coord_tag": "threejs_local_m",
            "position_m": k["panel_local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_bakelite_knob",
            "contract_ref_id": k["id"]
        })

    # Add 12 patch sockets
    for s in contract["patch_sockets"]:
        entities.append({
            "entity_id": s["id"],
            "node_name": s["node_name"],
            "parent_id": "synth_faceplate_frame",
            "category": "patch_socket",
            "coord_tag": "threejs_local_m",
            "position_m": s["panel_local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_chrome_fitting",
            "contract_ref_id": s["id"]
        })

    # Add 25 hinged keys
    for key in contract["keyboard"]["keys"]:
        entities.append({
            "entity_id": key["id"],
            "node_name": key["node_name"],
            "parent_id": "synth_keybed_frame",
            "category": "key",
            "coord_tag": "threejs_local_m",
            "position_m": key["keybed_local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_ebony_key" if key["is_sharp"] else "mat_ivory_key",
            "contract_ref_id": key["id"]
        })

    # Add Turntable hierarchy
    tt_entities = [
        {
            "entity_id": "turntable_root",
            "node_name": "Turntable_Root",
            "parent_id": None,
            "category": "turntable_cabinet",
            "coord_tag": "threejs_local_m",
            "position_m": [0.44, 0.0, 0.05],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_walnut_cabinet"
        },
        {
            "entity_id": "turntable_platter",
            "node_name": "Turntable_Platter",
            "parent_id": "turntable_root",
            "category": "turntable_platter",
            "coord_tag": "threejs_local_m",
            "position_m": contract["turntable"]["platter_node"]["local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_vinyl_record"
        },
        {
            "entity_id": "tonearm_gimbal",
            "node_name": "Tonearm_Gimbal",
            "parent_id": "turntable_root",
            "category": "tonearm",
            "coord_tag": "threejs_local_m",
            "position_m": contract["turntable"]["tonearm_gimbal_node"]["local_pos_m"],
            "rotation_euler_deg": [5.5, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_chrome_fitting"
        },
        {
            "entity_id": "tonearm_headshell",
            "node_name": "Tonearm_Headshell",
            "parent_id": "tonearm_gimbal",
            "category": "tonearm_cartridge",
            "coord_tag": "threejs_local_m",
            "position_m": [-0.052, -0.008, 0.195],
            "rotation_euler_deg": [0.0, 22.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_bakelite_knob"
        },
        {
            "entity_id": "turntable_speed_switch",
            "node_name": "Turntable_SpeedSwitch",
            "parent_id": "turntable_root",
            "category": "turntable_control",
            "coord_tag": "threejs_local_m",
            "position_m": contract["turntable"]["speed_switch_node"]["local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_chrome_fitting"
        },
        {
            "entity_id": "turntable_start_stop",
            "node_name": "Turntable_StartStop",
            "parent_id": "turntable_root",
            "category": "turntable_control",
            "coord_tag": "threejs_local_m",
            "position_m": contract["turntable"]["start_stop_node"]["local_pos_m"],
            "rotation_euler_deg": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_chrome_fitting"
        },
        {
            "entity_id": "vinyl_sleeve_stand",
            "node_name": "Vinyl_Sleeve_Stand",
            "parent_id": "turntable_root",
            "category": "prop",
            "coord_tag": "threejs_local_m",
            "position_m": [0.02, 0.185, -0.195],
            "rotation_euler_deg": [-12.0, -8.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "material_id": "mat_record_sleeve"
        }
    ]
    entities.extend(tt_entities)

    world = {
        "schema_version": "1.0.0",
        "contract_ref": "contract.json",
        "revision": 4,
        "coordinate_frame": "threejs_meters_yup",
        "selected_visual_direction": {
            "id": "dir_01_1974_walnut_anodised_studio",
            "name": "1974 American Black Walnut & Charcoal Anodised Laboratory Console (Dark-Room PS5 Pro PBR Revision 4)",
            "rationale": "Combines luthier-oriented oiled American walnut cabinetry with clearcoat and wood-pore normal/roughness maps, deep charcoal-black brushed anodised aluminium panels (#101215) with engraved module bay seams, corner screws, and potentiometer shaft bushings, high-contrast warm cream silk-screened scales (#faf2e0), 56-segment bevelled fluted black bakelite knobs, woven braided 3D patch cables routed cleanly through the inter-row corridor, and a dark gunmetal direct-drive turntable deck with a 240-segment 2-track strobe platter and sculpted strobe prism under a custom 1974 dark-room studio softbox HDRI.",
            "reference_images": [
                "evidence/captures/concept_direction_1_walnut_anodised.png",
                "evidence/captures/concept_direction_2_teak_silver_broadcast.png",
                "public/assets/textures/walnut_wood_grain.png",
                "public/assets/textures/vinyl_sleeve_art.png",
                "public/assets/textures/synth_faceplate_albedo.png",
                "public/assets/textures/turntable_deck_albedo.png",
                "public/assets/textures/ui_hardware_console_skin.png"
            ],
            "settled_decisions": [
                "0.8 m rack width (8 x 0.1 m source units) divided into 4 x 0.2 m module bays: VCO, VCF, ENV/VCA, LFO/DELAY.",
                "15-degree backward tilt on Synth_Faceplate_Frame for natural sightlines to all 16 knobs and 12 patch sockets.",
                "Custom 1974 dark-room studio environment map (dark acoustic ceiling + grazing 3200K warm key, cool cyan fill, and amber rim softbox strips) so the 180g vinyl LP stays jet-black with sharp anisotropic bow-tie groove reflections.",
                "Luthier-grade wood UV orientation along the longest axis of every cabinet cheek, rail, bullnose trim, and acoustic slat.",
                "240-segment 2-track cast-aluminium strobe platter rim with a glowing neon-amber prism tower, 45-RPM adapter puck, hydraulic cueing lever, and slotted die-cast magnesium headshell.",
                "Cross-bay patch cables routed through the clear horizontal corridor between upper [OUT] and lower [IN] jack rows so intermediate sockets (VCA GAIN CV) remain 100% unobstructed.",
                "GPU-composited brushed-metal hardware HUD (ui_hardware_console_skin.png, zero backdrop-filter blur) running at 60 FPS alongside 30 Hz throttled hover raycasting and fast oscilloscope telemetry."
            ]
        },
        "assets": [
            {
                "asset_id": "calibration_knob_glb",
                "type": "glb_model",
                "source_path": "blender/calibration_knob.blend",
                "runtime_path": "public/assets/models/calibration_knob.glb",
                "revision": 1,
                "generator_script": "scripts/build_calibration_knob.py"
            },
            {
                "asset_id": "studio_scene_glb",
                "type": "glb_model",
                "source_path": "blender/studio_scene.blend",
                "runtime_path": "public/assets/models/studio_scene.glb",
                "revision": 4,
                "generator_script": "scripts/build_studio_assets.py"
            },
            {
                "asset_id": "tex_walnut_albedo",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/walnut_wood_grain.png",
                "runtime_path": "public/assets/textures/walnut_wood_grain.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_walnut_normal",
                "type": "texture_normal",
                "source_path": "public/assets/textures/walnut_wood_normal.png",
                "runtime_path": "public/assets/textures/walnut_wood_normal.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_walnut_roughness",
                "type": "texture_roughness",
                "source_path": "public/assets/textures/walnut_wood_roughness.png",
                "runtime_path": "public/assets/textures/walnut_wood_roughness.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_faceplate_albedo",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/synth_faceplate_albedo.png",
                "runtime_path": "public/assets/textures/synth_faceplate_albedo.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_faceplate_normal",
                "type": "texture_normal",
                "source_path": "public/assets/textures/synth_faceplate_normal.png",
                "runtime_path": "public/assets/textures/synth_faceplate_normal.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_faceplate_roughness",
                "type": "texture_roughness",
                "source_path": "public/assets/textures/synth_faceplate_roughness.png",
                "runtime_path": "public/assets/textures/synth_faceplate_roughness.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_turntable_deck_albedo",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/turntable_deck_albedo.png",
                "runtime_path": "public/assets/textures/turntable_deck_albedo.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_turntable_deck_normal",
                "type": "texture_normal",
                "source_path": "public/assets/textures/turntable_deck_normal.png",
                "runtime_path": "public/assets/textures/turntable_deck_normal.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_turntable_deck_roughness",
                "type": "texture_roughness",
                "source_path": "public/assets/textures/turntable_deck_roughness.png",
                "runtime_path": "public/assets/textures/turntable_deck_roughness.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_studio_desk_albedo",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/studio_desk_albedo.png",
                "runtime_path": "public/assets/textures/studio_desk_albedo.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_studio_desk_normal",
                "type": "texture_normal",
                "source_path": "public/assets/textures/studio_desk_normal.png",
                "runtime_path": "public/assets/textures/studio_desk_normal.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_studio_desk_roughness",
                "type": "texture_roughness",
                "source_path": "public/assets/textures/studio_desk_roughness.png",
                "runtime_path": "public/assets/textures/studio_desk_roughness.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_ui_hardware_skin",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/ui_hardware_console_skin.png",
                "runtime_path": "public/assets/textures/ui_hardware_console_skin.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_vinyl_grooves_normal",
                "type": "texture_normal",
                "source_path": "public/assets/textures/vinyl_grooves_normal.png",
                "runtime_path": "public/assets/textures/vinyl_grooves_normal.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_vinyl_label",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/vinyl_label_albedo.png",
                "runtime_path": "public/assets/textures/vinyl_label_albedo.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "tex_sleeve_art",
                "type": "texture_albedo",
                "source_path": "public/assets/textures/vinyl_sleeve_art.png",
                "runtime_path": "public/assets/textures/vinyl_sleeve_art.png",
                "revision": 4,
                "generator_script": "scripts/prepare_textures.py"
            },
            {
                "asset_id": "audio_turntable_lp",
                "type": "audio_wav",
                "source_path": "public/assets/audio/chrono_analogue_side_a_33rpm.wav",
                "runtime_path": "public/assets/audio/chrono_analogue_side_a_33rpm.wav",
                "revision": 1,
                "generator_script": "scripts/generate_record_audio.py"
            }
        ],
        "materials": [
            {
                "material_id": "mat_walnut_cabinet",
                "base_color_hex": "#4e2c18",
                "roughness": 0.32,
                "metalness": 0.0,
                "textures": {
                    "map": "public/assets/textures/walnut_wood_grain.png",
                    "normalMap": "public/assets/textures/walnut_wood_normal.png",
                    "roughnessMap": "public/assets/textures/walnut_wood_roughness.png"
                },
                "notes": "Hand-rubbed satin oiled American walnut cabinet cheeks, plinth, and bullnose rail with long-axis luthier UVs and clearcoat=0.54."
            },
            {
                "material_id": "mat_anodised_panel",
                "base_color_hex": "#101215",
                "roughness": 0.38,
                "metalness": 0.50,
                "textures": {
                    "map": "public/assets/textures/synth_faceplate_albedo.png",
                    "normalMap": "public/assets/textures/synth_faceplate_normal.png",
                    "roughnessMap": "public/assets/textures/synth_faceplate_roughness.png"
                },
                "notes": "Deep charcoal-black brushed anodised aluminium panel with engraved bay seams, corner screws, shaft bushings, and cream silkscreen markings."
            },
            {
                "material_id": "mat_turntable_deck",
                "base_color_hex": "#1f2226",
                "roughness": 0.30,
                "metalness": 0.78,
                "textures": {
                    "map": "public/assets/textures/turntable_deck_albedo.png",
                    "normalMap": "public/assets/textures/turntable_deck_normal.png",
                    "roughnessMap": "public/assets/textures/turntable_deck_roughness.png"
                },
                "notes": "Deep brushed gunmetal direct-drive turntable deck plate with silkscreened CHRONO-DRIVE DD-1974 and speed markings."
            },
            {
                "material_id": "mat_anodised_trim",
                "base_color_hex": "#15171b",
                "roughness": 0.34,
                "metalness": 0.60,
                "notes": "Clean satin dark anodised chassis rails and keybed surround isolated from faceplate normal maps."
            },
            {
                "material_id": "mat_bakelite_knob",
                "base_color_hex": "#070709",
                "roughness": 0.18,
                "metalness": 0.04,
                "notes": "56-segment bevelled fluted phenolic bakelite knob with spun-aluminium cap and bevelled cream indicator inlay."
            },
            {
                "material_id": "mat_chrome_fitting",
                "base_color_hex": "#dce2ea",
                "roughness": 0.08,
                "metalness": 0.97,
                "notes": "Mirror-polished chrome for 32-segment chamfered hex jack nuts, 36-step S-shaped tonearm, gimbal, and 240-segment strobe rim."
            },
            {
                "material_id": "mat_ivory_key",
                "base_color_hex": "#f3ebd9",
                "roughness": 0.15,
                "metalness": 0.0,
                "notes": "Bevelled warm vintage acrylic natural keys with clearcoat=0.82."
            },
            {
                "material_id": "mat_ebony_key",
                "base_color_hex": "#070709",
                "roughness": 0.18,
                "metalness": 0.04,
                "notes": "Sculpted sloped satin black sharp keys with clearcoat=0.72."
            },
            {
                "material_id": "mat_vinyl_record",
                "base_color_hex": "#050507",
                "roughness": 0.16,
                "metalness": 0.08,
                "textures": {
                    "normalMap": "public/assets/textures/vinyl_grooves_normal.png",
                    "labelMap": "public/assets/textures/vinyl_label_albedo.png"
                },
                "notes": "Jet-black 180g vinyl LP with height-derived concentric micro-groove normal map, clearcoat=0.92, and anisotropy=0.90."
            },
            {
                "material_id": "mat_record_sleeve",
                "base_color_hex": "#e8dfd1",
                "roughness": 0.48,
                "metalness": 0.0,
                "textures": {
                    "map": "public/assets/textures/vinyl_sleeve_art.png"
                },
                "notes": "Gatefold cardboard LP jacket with bevelled spine, inner dust sleeve, peeking vinyl rim, and 1974 Nano Banana cover artwork."
            },
            {
                "material_id": "mat_studio_slate_desk",
                "base_color_hex": "#161210",
                "roughness": 0.74,
                "metalness": 0.02,
                "textures": {
                    "map": "public/assets/textures/studio_desk_albedo.png",
                    "normalMap": "public/assets/textures/studio_desk_normal.png",
                    "roughnessMap": "public/assets/textures/studio_desk_roughness.png"
                },
                "notes": "Deep espresso-charcoal padded studio console leatherette blotter surface with front walnut bullnose rail and full-span L-wrap walnut acoustic slat wall."
            }
        ],
        "camera_presets": [
            {
                "preset_id": "opening_studio",
                "label": "Studio Overview (Both Instruments)",
                "position_m": [0.02, 0.52, 1.18],
                "target_m": [0.02, 0.15, 0.02],
                "fov_deg": 40.0
            },
            {
                "preset_id": "synth_rack_closeup",
                "label": "Modular Rack & Patch Bay",
                "position_m": [-0.22, 0.34, 0.76],
                "target_m": [-0.22, 0.21, -0.04],
                "fov_deg": 36.0
            },
            {
                "preset_id": "patch_and_keys",
                "label": "Patch Sockets & Hinged Keyboard",
                "position_m": [-0.22, 0.33, 0.68],
                "target_m": [-0.22, 0.11, 0.06],
                "fov_deg": 37.0
            },
            {
                "preset_id": "turntable_closeup",
                "label": "Turntable, Platter & Tonearm",
                "position_m": [0.44, 0.42, 0.58],
                "target_m": [0.44, 0.04, 0.02],
                "fov_deg": 33.0
            },
            {
                "preset_id": "side_profile_tilt",
                "label": "15° Rack Tilt & Cable Clearance Profile",
                "position_m": [-0.84, 0.28, 0.34],
                "target_m": [-0.22, 0.17, 0.02],
                "fov_deg": 34.0
            }
        ],
        "lighting_rig": [
            {
                "light_id": "warm_key_side_left",
                "type": "DirectionalLight",
                "color_hex": "#ffd8ad",
                "intensity": 3.15,
                "position_m": [-0.86, 0.92, 0.78]
            },
            {
                "light_id": "panel_fill_front",
                "type": "DirectionalLight",
                "color_hex": "#b8d4f2",
                "intensity": 0.82,
                "position_m": [0.74, 0.96, 0.78]
            },
            {
                "light_id": "amber_back_rim",
                "type": "DirectionalLight",
                "color_hex": "#ff9c3b",
                "intensity": 1.75,
                "position_m": [0.86, 0.56, -0.62]
            },
            {
                "light_id": "strobe_prism_neon",
                "type": "PointLight",
                "color_hex": "#ff5e14",
                "intensity": 0.42,
                "position_m": [0.295, 0.066, 0.142]
            }
        ],
        "entities": entities
    }
    return world


def build_progress():
    return {
        "schema_version": "1.0.0",
        "current_milestone": "M4_DELIVERED_AND_VERIFIED",
        "build_revision": 4,
        "updated_at": "2026-10-14T19:30:00+11:00",
        "assigned_owners": {
            "lead_integrator": {
                "agent": "main_gemini_4_argon",
                "scope": "Shared records (contract.json, world.json, progress.json), schema validation, pipeline calibration, Dark-Room PS5 Pro PBR shader & 60 FPS UI upgrade, final integration and verification."
            },
            "asset_lead": {
                "agent": "image-generator & scripts/build_studio_assets.py",
                "scope": "Nano Banana textures, 16-map PBR texture synthesis (scripts/prepare_textures.py), luthier long-axis wood UV alignment, 240-segment 2-track strobe platter, sculpted headshell/strobe prism, and headless Blender 5.2.2 LTS studio_scene.glb export."
            },
            "runtime_interaction_lead": {
                "agent": "main_gemini_4_argon (public/src/studio-app.js & audio-engine.js)",
                "scope": "Three.js r169 MeshPhysicalMaterial PBR loader with custom dark-room 1974 studio softbox PMREM HDRI, anisotropic jet-black vinyl grooves, corridor-routed braided 3D patch cables, 30 Hz throttled hover raycasting, GPU-composited hardware UI, QWERTY/MIDI input, and Web Audio synth + turntable engine."
            },
            "independent_reviewer": {
                "agent": "gravitas-visual-critic (7de762f3 & baa9205c)",
                "scope": "Independent read-only perceptual visual critique across Revisions 1, 2, 3, and 4."
            }
        },
        "completed_work": [
            {
                "id": "env_and_calibration_pipeline",
                "summary": "Verified Blender 5.2.2 LTS, Python 3.10, Nano Banana image-generator, and proved Blender -> calibration_knob.glb -> Three.js -> browser capture route (evidence/captures/calibration_knob_browser.png)."
            },
            {
                "id": "nano_banana_and_16_pbr_maps",
                "summary": "Generated Nano Banana concept studies and base textures (walnut, brushed gunmetal turntable deck, 1974 LP sleeve art, hardware UI console skin) and synthesized 16 high-DPI PBR albedo/normal/roughness maps via scripts/prepare_textures.py."
            },
            {
                "id": "high_poly_bevelled_blender_scene",
                "summary": "Built and verified 64/64 world.json entities in blender/studio_scene.blend and public/assets/models/studio_scene.glb with luthier-aligned long-axis wood UVs, 240-segment 2-track strobe platter, sculpted headshell/strobe prism, 56-segment fluted bakelite knobs, 32-segment hex sockets, 25 sculpted keys C3-C5, gatefold LP jacket, and full-span L-wrap walnut acoustic slat wall."
            },
            {
                "id": "dark_room_ps5_pro_pbr_and_60fps_ui",
                "summary": "Replaced white-ceiling RoomEnvironment with custom 1974 dark-room studio softbox PMREM HDRI so 180g vinyl stays jet-black with sharp amber/cyan anisotropic groove reflections, widened synth_rack_closeup framing, routed cross-bay patch cables through the clear inter-row corridor, and verified 60+ FPS and all audio/routing/tuning/self-test gates."
            }
        ],
        "unresolved_work": [],
        "decisions": [
            {
                "id": "dec_01_units_and_axes",
                "summary": "Locked 0.1 m source unit (8 units = 0.8 m rack width), 15-degree backward faceplate tilt, and glTF Y-up export mapping."
            },
            {
                "id": "dec_02_ps5_pro_pbr_and_fast_ui",
                "summary": "Replaced CSS backdrop-filter blur with Nano Banana brushed dark-bronze hardware rack skin (ui_hardware_console_skin.png), throttled hover raycasting and scope drawing to 30 Hz, and upgraded all 163 mesh primitives to MeshPhysicalMaterial."
            },
            {
                "id": "dec_03_grill_me_rev4_dark_room_and_luthier_uvs",
                "summary": "Locked 4 /grill-me decisions: (1) custom dark-room 1974 studio HDRI with dark ceiling and grazing 3200K/amber/cyan softboxes, (2) luthier-oriented long-axis walnut UVs + 240-segment 2-track strobe platter & sculpted headshell/strobe prism, (3) widened Modular Rack camera + inter-row corridor cable routing + shaft washers, and (4) extended acoustic slat wall + deep espresso leatherette desk with walnut bullnose trim."
            }
        ],
        "next_actions": [
            "Maintain http://127.0.0.1:8088/ studio server for live user exploration."
        ],
        "review_evidence": [
            {
                "evidence_id": "ev_01_calibration_knob",
                "build_revision": 1,
                "type": "screenshot_capture",
                "path": "evidence/captures/calibration_knob_browser.png",
                "summary": "Proved headless Blender to GLB to Three.js browser rendering and audio picking on calibration_knob.glb.",
                "verdict": "PASS"
            },
            {
                "evidence_id": "ev_02_rev1_visual_critique",
                "build_revision": 1,
                "type": "independent_visual_critique",
                "path": "evidence/captures/rev1_opening_studio.png",
                "summary": "Independent gravitas-visual-critic (7de762f3) identified 5 visual/UX defects in Revision 1: top HUD overlap, cable droop over lower socket labels, tight turntable framing, blocky keybed geometry, and plain desk backdrop.",
                "verdict": "REPAIRED_IN_REV2"
            },
            {
                "evidence_id": "ev_03_rev2_visual_critique",
                "build_revision": 2,
                "type": "independent_visual_critique",
                "path": "evidence/captures/rev2_opening_studio.png",
                "summary": "Independent gravitas-visual-critic (baa9205c) confirmed all 5 Revision 1 layout, cable clearance, framing, and key-travel defects were resolved.",
                "verdict": "PASS"
            },
            {
                "evidence_id": "ev_04_rev3_ps5_pro_critique",
                "build_revision": 3,
                "type": "independent_visual_critique",
                "path": "evidence/captures/rev3_opening_studio.png",
                "summary": "Independent gravitas-visual-critic (baa9205c) verified Revision 3 material photorealism, bevelled/smooth geometry, and brushed-bronze hardware HUD.",
                "verdict": "PASS"
            },
            {
                "evidence_id": "ev_05_rev4_dark_room_and_automated_gates",
                "build_revision": 4,
                "type": "runtime_and_audio_verification",
                "path": "evidence/audio_and_interaction_verification.json",
                "summary": "Verified Revision 4 dark-room PBR studio, 64/64 world.json entities, 0 console errors, 0 deprecation warnings, G_SELF_TEST red->green gate, signature VCO1->VCF filter sweep, 5 patch rejection rules, all 16 knobs, 0.000 Hz tuning error across C3-C5, 33.3/45 RPM speed continuity, and 60+ FPS.",
                "verdict": "PASS"
            }
        ],
        "defect_repairs": [
            {
                "defect_id": "def_01_hud_and_cable_clearance",
                "title": "Top HUD text collision and patch cable droop over lower-row socket labels",
                "before_evidence": "evidence/captures/rev1_synth_rack_closeup.png",
                "repair_summary": "Redesigned top HUD into a clean 2-tier flex header and constrained catenary cable sag with forward normal clearance.",
                "after_evidence": "evidence/captures/rev2_synth_rack_closeup.png",
                "status": "VERIFIED_FIXED"
            },
            {
                "defect_id": "def_02_ps1_flat_shading_to_ps5_pbr",
                "title": "Flat-shaded unbevelled geometry and basic materials upgraded to bevelled smooth-shaded 16-map MeshPhysicalMaterial PBR",
                "before_evidence": "evidence/captures/rev2_turntable_closeup.png",
                "repair_summary": "Added 3D bmesh bevels and smooth shading across all cabinet cheeks, plinth, keys, 56-segment knobs, 32-segment hex sockets, and 36-step S-shaped tonearm; generated 16 high-DPI PBR maps; enabled MeshPhysicalMaterial clearcoat, computed tangents, and vinyl anisotropy.",
                "after_evidence": "evidence/captures/rev3_turntable_closeup.png",
                "status": "VERIFIED_FIXED"
            },
            {
                "defect_id": "def_03_ui_lag_and_frame_rate",
                "title": "UI slowness caused by CSS backdrop-filter blur, per-move raycasting, and 60Hz FFT loop",
                "before_evidence": "evidence/captures/rev2_opening_studio.png",
                "repair_summary": "Removed all backdrop-filter blur in favour of GPU-promoted brushed-bronze hardware skin (ui_hardware_console_skin.png), throttled non-drag pointermove raycasting and scope drawing to 30 Hz, and added getFastWaveTelemetry(), achieving 60+ FPS.",
                "after_evidence": "evidence/captures/rev3_opening_studio.png",
                "status": "VERIFIED_FIXED"
            },
            {
                "defect_id": "def_04_dark_room_contrast_wood_uvs_and_corridor_cables",
                "title": "Overhead RoomEnvironment white-ceiling reflection washing out horizontal vinyl/desk surfaces, vertical wood grain on horizontal rails, and cross-bay cable crossing VCA GAIN CV",
                "before_evidence": "evidence/captures/rev3_turntable_closeup.png",
                "repair_summary": "Replaced RoomEnvironment with a custom dark-ceiling 1974 studio softbox HDRI so the 180g vinyl LP stays jet-black with sharp amber/cyan anisotropic streaks; oriented walnut UVs along the longest axis of every board; upgraded platter to 240-segment 2-track strobe dots with sculpted strobe prism; widened synth_rack_closeup camera; and routed cross-bay cables through the clear inter-row corridor.",
                "after_evidence": "evidence/captures/rev4_turntable_closeup.png",
                "status": "VERIFIED_FIXED"
            }
        ]
    }


def main():
    contract = build_contract()
    world = build_world(contract)
    progress = build_progress()

    (ROOT / "contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")
    (ROOT / "world.json").write_text(json.dumps(world, indent=2), encoding="utf-8")
    (ROOT / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")
    print("Wrote contract.json, world.json, progress.json successfully.")


if __name__ == "__main__":
    main()
