"""
Generates the master 120.0-second (7,200 frames @ 60.0 fps) choreography, musical score,
sample-accurate 48 kHz stereo audio (evidence/social_showcase_1974_symphonies_48k.wav),
companion SRT subtitles (evidence/social_showcase_1974_symphonies.srt), and social media
post copy (evidence/social_media_post_caption.md) for the 4-Symphony 1974 Modular Studio Showcase.
"""

import json
import math
import struct
import wave
from pathlib import Path
import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT / "evidence"
WAV_OUT = EVIDENCE_DIR / "social_showcase_1974_symphonies_48k.wav"
SRT_OUT = EVIDENCE_DIR / "social_showcase_1974_symphonies.srt"
MD_OUT = EVIDENCE_DIR / "social_media_post_caption.md"
TIMELINE_JSON = EVIDENCE_DIR / "showcase_timeline.json"

DURATION_S = 120.0
FPS = 60
TOTAL_FRAMES = int(DURATION_S * FPS)  # 7200
SAMPLE_RATE = 48000
TOTAL_SAMPLES = int(DURATION_S * SAMPLE_RATE)  # 5,760,000


def midi_to_hz(midi_note: float) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))


def clamp_to_manual(midi_note: int) -> int:
    """Folds any MIDI note into the 25-key physical manual range C3 (48) .. C5 (72) for visual key depression."""
    n = int(round(midi_note))
    while n < 48:
        n += 12
    while n > 72:
        n -= 12
    return n


# ==============================================================================
# 1. MUSICAL SCORE FOR FOUR SYMPHONIES (30.0s EACH = 120.0s TOTAL)
# ==============================================================================

def build_symphony_notes():
    """
    Returns list of note dicts:
      { "t0": float, "t1": float, "midi": int, "vel": float, "voice": "lead"|"harmony"|"bass", "visual_midi": int }
    """
    notes = []

    def add_note(t0, dur, midi, vel=0.85, voice="lead", gate_ratio=0.88):
        if t0 >= DURATION_S or dur <= 0.01:
            return
        t1 = min(DURATION_S - 0.02, t0 + dur * gate_ratio)
        if t1 <= t0 + 0.01:
            return
        notes.append({
            "t0": round(float(t0), 4),
            "t1": round(float(t1), 4),
            "midi": int(midi),
            "vel": round(float(vel), 3),
            "voice": voice,
            "visual_midi": clamp_to_manual(midi),
        })

    def add_oct(t0, dur, midi_high, vel=0.9, gate_ratio=0.88):
        add_note(t0, dur, midi_high, vel=vel, voice="lead", gate_ratio=gate_ratio)
        add_note(t0, dur, midi_high - 12, vel=vel * 0.82, voice="bass", gate_ratio=gate_ratio)

    def add_chord(t0, dur, midis, vel=0.82, gate_ratio=0.90):
        for i, m in enumerate(midis):
            role = "lead" if i == len(midis) - 1 else ("bass" if i == 0 else "harmony")
            add_note(t0, dur, m, vel=vel * (1.0 if role == "lead" else 0.76), voice=role, gate_ratio=gate_ratio)

    # --------------------------------------------------------------------------
    # MOVEMENT I (0.0s - 30.0s): BEETHOVEN — SYMPHONY NO. 5 IN C MINOR, OP. 67
    # --------------------------------------------------------------------------
    # 0.0 - 4.6s: Iconic Fate Motif I (G-G-G-Eb) & II (F-F-F-D) with Fermatas
    # Motif 1: G4 (67), Eb4 (63)
    for k, t_hit in enumerate([0.25, 0.47, 0.69]):
        add_oct(t_hit, 0.19, 67, vel=0.95, gate_ratio=0.82)
    add_chord(0.92, 1.55, [51, 55, 63, 67], vel=0.98, gate_ratio=0.95)  # Eb3, G3, Eb4, G4 fermata

    # Motif 2: F4 (65), D4 (62) + G3 (55) / B3 (59)
    for k, t_hit in enumerate([2.65, 2.87, 3.09]):
        add_oct(t_hit, 0.19, 65, vel=0.96, gate_ratio=0.82)
    add_chord(3.32, 1.45, [50, 55, 59, 62, 65], vel=0.98, gate_ratio=0.95)  # G7/D fermata

    # 4.8s - 14.0s: Allegro con brio rapid imitative Fate cells climbing C minor
    # Eighth note = 0.20s (150 BPM allegro con brio pulse)
    e = 0.20
    t_cur = 4.90
    imitative_cells = [
        # (three_short_midi, long_midi, bass_midi, long_beats)
        (67, 63, 48, 4),   # G4-G4-G4-Eb4 over C3
        (68, 65, 53, 4),   # Ab4-Ab4-Ab4-F4 over F3
        (65, 62, 55, 4),   # F4-F4-F4-D4 over G3
        (67, 60, 48, 4),   # G4-G4-G4-C4 over C3
        (72, 68, 56, 4),   # C5-C5-C5-Ab4 over Ab3
        (70, 67, 51, 4),   # Bb4-Bb4-Bb4-G4 over Eb3
        (68, 65, 50, 4),   # Ab4-Ab4-Ab4-F4 over D3
        (67, 71, 55, 5),   # G4-G4-G4-B4 -> G7 climax!
    ]
    for s_m, l_m, b_m, l_len in imitative_cells:
        add_note(t_cur + 0 * e, e, s_m, vel=0.88, voice="lead", gate_ratio=0.80)
        add_note(t_cur + 1 * e, e, s_m, vel=0.88, voice="lead", gate_ratio=0.80)
        add_note(t_cur + 2 * e, e, s_m, vel=0.92, voice="lead", gate_ratio=0.80)
        add_note(t_cur + 3 * e, l_len * e, l_m, vel=0.95, voice="lead", gate_ratio=0.92)
        # Driving bass pulse underneath
        for b_step in range(l_len + 1):
            add_note(t_cur + (2 + b_step) * e, e, b_m if b_step % 2 == 0 else b_m + 12, vel=0.72, voice="bass", gate_ratio=0.78)
        t_cur += (2 + l_len) * e  # overlapping imitative stretto!

    # 14.5s - 16.5s: Heroic Horn Call in Eb Major (G4 - Eb4 - D4 - C4 - D4 - Eb4 - F4 - G4 - Eb4 - Bb3)
    horn_call = [
        (14.50, 0.35, 67, 55),
        (14.85, 0.35, 63, 51),
        (15.20, 0.22, 62, 50),
        (15.42, 0.22, 60, 48),
        (15.64, 0.22, 62, 50),
        (15.86, 0.22, 63, 51),
        (16.08, 0.25, 65, 53),
        (16.33, 0.42, 67, 55),
        (16.75, 0.45, 63, 51),
    ]
    for th, dur, m_top, m_bot in horn_call:
        add_note(th, dur, m_top, vel=0.94, voice="lead", gate_ratio=0.90)
        add_note(th, dur, m_bot, vel=0.78, voice="bass", gate_ratio=0.90)

    # 17.2s - 22.4s: Second Subject in Eb Major over Fate Bass Ostinato
    second_subj = [
        # Phrase 1: Bb4 - Eb4 - F4 - G4 | Ab4 - F4 - D4 - Eb4
        (17.20, 0.32, 70), (17.52, 0.32, 63), (17.84, 0.32, 65), (18.16, 0.34, 67),
        (18.50, 0.32, 68), (18.82, 0.32, 65), (19.14, 0.32, 62), (19.46, 0.34, 63),
        # Phrase 2: C5 - F4 - G4 - Ab4 | Bb4 - G4 - E4 - F4
        (19.80, 0.32, 72), (20.12, 0.32, 65), (20.44, 0.32, 67), (20.76, 0.34, 68),
        (21.10, 0.32, 70), (21.42, 0.32, 67), (21.74, 0.32, 64), (22.06, 0.34, 65),
    ]
    for ts, dur, m in second_subj:
        add_note(ts, dur, m, vel=0.90, voice="lead", gate_ratio=0.90)
    # Fate ostinato in bass during Second Subject
    for bar_i, b_root in enumerate([51, 58, 53, 48]):
        bt = 17.20 + bar_i * 1.30
        add_note(bt + 0.00, 0.20, b_root, vel=0.76, voice="bass", gate_ratio=0.80)
        add_note(bt + 0.20, 0.20, b_root, vel=0.76, voice="bass", gate_ratio=0.80)
        add_note(bt + 0.40, 0.20, b_root, vel=0.80, voice="bass", gate_ratio=0.80)
        add_note(bt + 0.60, 0.65, b_root - 5 if b_root >= 53 else b_root + 7, vel=0.84, voice="bass", gate_ratio=0.90)

    # 22.4s - 30.0s: Stormy C Minor Development, Ascending Scale & Searing Climax
    c_minor_scale = [48, 50, 51, 53, 55, 56, 59, 60, 62, 63, 65, 67, 68, 71, 72]
    for idx, m in enumerate(c_minor_scale):
        add_note(22.45 + idx * 0.14, 0.14, m, vel=0.86 + 0.008 * idx, voice="lead", gate_ratio=0.88)
        if idx % 2 == 0:
            add_note(22.45 + idx * 0.14, 0.26, max(48, m - 12), vel=0.75, voice="bass", gate_ratio=0.85)

    # Fortissimo Fate Fanfare Climax (24.6s - 29.8s)
    climax_events = [
        (24.60, 0.22, [55, 63, 67, 72]),
        (24.82, 0.22, [55, 63, 67, 72]),
        (25.04, 0.22, [55, 63, 67, 72]),
        (25.26, 0.84, [51, 58, 63, 67]),
        (26.15, 0.22, [53, 62, 68, 71]),
        (26.37, 0.22, [53, 62, 68, 71]),
        (26.59, 0.22, [53, 62, 68, 71]),
        (26.81, 0.84, [55, 59, 62, 67, 71]),
        # Final C Minor Cadence
        (27.70, 0.25, [48, 60, 67, 72]),
        (27.95, 0.25, [55, 59, 62, 71]),
        (28.20, 0.25, [48, 60, 63, 72]),
        (28.45, 0.25, [55, 59, 67, 71]),
        (28.70, 1.15, [48, 55, 60, 63, 67, 72]),
    ]
    for tc, dur, ch in climax_events:
        add_chord(tc, dur, ch, vel=0.96, gate_ratio=0.92)

    # --------------------------------------------------------------------------
    # MOVEMENT II (30.0s - 60.0s): BACH TOCCATA & FUGUE IN D MINOR BWV 565
    #                              + VIVALDI "WINTER" ALLEGRO STORM
    # --------------------------------------------------------------------------
    # 30.0 - 36.6s: Bach Toccata in D Minor Opening Mordent & Diminished 7th Arpeggio
    # Mordent 1 (high): A4 (69) - G4 (67) - A4 (69 held) -> G4-F4-E4-D4-C#4-D4
    add_oct(30.40, 0.14, 69, vel=0.95, gate_ratio=0.92)
    add_oct(30.54, 0.14, 67, vel=0.92, gate_ratio=0.92)
    add_oct(30.68, 0.82, 69, vel=0.98, gate_ratio=0.95)
    for i, m in enumerate([67, 65, 64, 62, 61]):
        add_oct(31.55 + i * 0.13, 0.13, m, vel=0.92, gate_ratio=0.90)
    add_chord(32.20, 1.05, [50, 57, 62], vel=0.96, gate_ratio=0.95)

    # Diminished 7th Arpeggio Climb over D2/D3 Pedal (33.35s - 36.6s)
    add_note(33.35, 3.15, 50, vel=0.88, voice="bass", gate_ratio=0.98)  # D3 pedal
    dim_arp = [49, 52, 55, 58, 61, 64, 67, 70, 69]  # C#3, E3, G3, Bb3, C#4, E4, G4, Bb4 -> A4
    for i, m in enumerate(dim_arp[:-1]):
        add_note(33.40 + i * 0.22, 1.80 - i * 0.15, m, vel=0.88 + i * 0.01, voice="lead", gate_ratio=0.95)
    add_chord(35.16, 0.65, [49, 57, 61, 64, 69], vel=0.95, gate_ratio=0.92)  # A7
    add_chord(35.85, 0.75, [50, 57, 62, 65, 69], vel=0.98, gate_ratio=0.94)  # Dm resolution

    # 36.7s - 48.0s: Rapid 16th-Note Baroque Bariolage Counterpoint (C3-C5)
    # 16th note = 0.115s
    s16 = 0.115
    bariolage_seq = [
        # D minor -> A7 -> Dm -> Gm -> E dim -> A7 -> Dm -> Bb -> Gm -> A7 -> Dm
        (62, 69, 65, 69, 50), (61, 69, 64, 69, 49), (62, 69, 65, 69, 50), (64, 69, 67, 69, 52),
        (65, 69, 62, 69, 53), (67, 70, 64, 70, 55), (65, 69, 62, 69, 53), (64, 69, 61, 69, 49),
        (62, 70, 67, 70, 55), (60, 69, 65, 69, 53), (58, 67, 64, 67, 52), (57, 65, 62, 65, 50),
        (56, 64, 59, 64, 52), (57, 64, 61, 64, 49), (62, 69, 65, 69, 50), (65, 72, 69, 72, 53),
        (67, 70, 62, 70, 55), (65, 69, 62, 69, 57), (64, 67, 61, 67, 49), (62, 65, 57, 65, 50),
        # Virtuosic ascending sequence
        (50, 53, 57, 62, 50), (52, 55, 58, 64, 52), (53, 57, 62, 65, 53), (55, 58, 62, 67, 55),
        (57, 61, 64, 69, 57), (58, 62, 67, 70, 58), (61, 64, 67, 72, 61), (62, 65, 69, 72, 50),
    ]
    t_bar = 36.70
    for n1, n2, n3, n4, b_note in bariolage_seq:
        if t_bar + 4 * s16 > 48.0:
            break
        add_note(t_bar + 0 * s16, s16, n1, vel=0.90, voice="lead", gate_ratio=0.84)
        add_note(t_bar + 1 * s16, s16, n2, vel=0.82, voice="lead", gate_ratio=0.84)
        add_note(t_bar + 2 * s16, s16, n3, vel=0.88, voice="lead", gate_ratio=0.84)
        add_note(t_bar + 3 * s16, s16, n4, vel=0.82, voice="lead", gate_ratio=0.84)
        add_note(t_bar, 4 * s16, b_note, vel=0.76, voice="bass", gate_ratio=0.88)
        t_bar += 4 * s16

    # 48.0s - 60.0s: Vivaldi "Winter" (Allegro non molto) Icy Tremolando & Lightning Scales
    # 48.0s - 52.8s: Shivering 16th-note baroque chords
    winter_chords = [
        [50, 57, 62, 65],  # Dm
        [49, 58, 64, 67],  # C#dim7
        [50, 57, 65, 69],  # Dm6
        [54, 60, 62, 69],  # F#dim7
        [55, 58, 62, 70],  # Gm
        [52, 58, 64, 67],  # Edim7
        [53, 57, 62, 65],  # Dm/F
        [49, 57, 61, 69],  # A7
    ]
    t_w = 48.05
    for ch in winter_chords:
        for rep in range(4):
            add_chord(t_w + rep * 0.14, 0.14, ch, vel=0.84 + 0.03 * rep, gate_ratio=0.76)
        t_w += 4 * 0.14

    # 52.6s - 59.8s: Vivaldi Winter Solo Violin Virtuoso Storm Runs & Cadence
    winter_runs = [
        [72, 70, 69, 67, 65, 64, 62, 61, 62, 57, 53, 50],
        [70, 69, 67, 65, 64, 62, 61, 58, 57, 55, 52, 49],
        [50, 53, 57, 62, 65, 69, 72, 69, 65, 62, 57, 53],
        [55, 58, 62, 67, 70, 67, 64, 61, 64, 67, 69, 61],
    ]
    t_r = 52.60
    for r_idx, run in enumerate(winter_runs):
        bass_p = [50, 49, 53, 57][r_idx]
        add_note(t_r, len(run) * 0.11, bass_p, vel=0.80, voice="bass", gate_ratio=0.92)
        for n_i, m in enumerate(run):
            add_note(t_r + n_i * 0.11, 0.11, m, vel=0.92, voice="lead", gate_ratio=0.85)
        t_r += len(run) * 0.11

    # Grand Baroque D-minor / Picardy Tierce D-major Cadence (57.9s - 59.8s)
    add_chord(57.90, 0.45, [55, 58, 62, 67, 70], vel=0.94)
    add_chord(58.35, 0.45, [49, 57, 61, 64, 69], vel=0.95)
    add_chord(58.80, 1.05, [50, 57, 62, 65, 69], vel=0.98)

    # --------------------------------------------------------------------------
    # MOVEMENT III (60.0s - 90.0s): MOZART — SYMPHONY NO. 40 IN G MINOR, K. 550
    #                               + LIVE 33 1/3 <-> 45 RPM TURNTABLE LAYER
    # --------------------------------------------------------------------------
    # 60.0s - 62.2s: Classical spiccato warm-up chord while tonearm lowers onto spinning 180g LP
    add_chord(60.50, 0.35, [55, 58, 62, 67], vel=0.80, gate_ratio=0.75)
    add_chord(61.10, 0.35, [55, 58, 62, 67], vel=0.82, gate_ratio=0.75)

    # 62.2s - 73.8s: Mozart Symphony No. 40 Opening Theme in G Minor (at 33 1/3 RPM = 1.00x)
    # Iconic motif: Eb4 (63) - D4 (62) - D4 (62) | Eb4 - D4 - D4 | Eb4 - D4 - D4 - Bb4 (70) | Bb4 - A4 (69) - G4 (67) - F#4 (66) - Eb4 (63) - D4 (62) | C4 (60) - Bb3 (58) - A3 (57)
    mozart_p1 = [
        (62.20, 0.18, 63), (62.38, 0.34, 62), (62.72, 0.34, 62),
        (63.06, 0.18, 63), (63.24, 0.34, 62), (63.58, 0.34, 62),
        (63.92, 0.18, 63), (64.10, 0.34, 62), (64.44, 0.34, 62),
        (64.78, 0.68, 70),
        (65.46, 0.34, 70), (65.80, 0.18, 69), (65.98, 0.18, 67),
        (66.16, 0.34, 67), (66.50, 0.18, 66), (66.68, 0.18, 63),
        (66.86, 0.34, 62), (67.20, 0.34, 60), (67.54, 0.55, 58),
    ]
    for tm, dur, m in mozart_p1:
        add_note(tm, dur, m, vel=0.92, voice="lead", gate_ratio=0.86)

    # Divided viola pulsing accompaniment (G3-Bb3-D4) under Phrase 1
    for step in range(22):
        tb = 62.20 + step * 0.25
        add_note(tb, 0.22, 55 if step % 2 == 0 else 58, vel=0.68, voice="bass", gate_ratio=0.72)

    # Phrase 2 sequential response on F#dim7 / D7 -> Gm:
    # D4 (62) - C4 (60) - C4 (60) x3 -> A4 (69) -> A4-G4-F#4-Eb4-D4-C4-Bb3
    mozart_p2 = [
        (68.20, 0.18, 62), (68.38, 0.34, 60), (68.72, 0.34, 60),
        (69.06, 0.18, 62), (69.24, 0.34, 60), (69.58, 0.34, 60),
        (69.92, 0.18, 62), (70.10, 0.34, 60), (70.44, 0.34, 60),
        (70.78, 0.68, 69),
        (71.46, 0.34, 69), (71.80, 0.18, 67), (71.98, 0.18, 66),
        (72.16, 0.34, 66), (72.50, 0.18, 63), (72.68, 0.18, 62),
        (72.86, 0.34, 60), (73.20, 0.34, 58), (73.54, 0.50, 55),
    ]
    for tm, dur, m in mozart_p2:
        add_note(tm, dur, m, vel=0.92, voice="lead", gate_ratio=0.86)
    for step in range(22):
        tb = 68.20 + step * 0.25
        add_note(tb, 0.22, 50 if step % 2 == 0 else 54, vel=0.68, voice="bass", gate_ratio=0.72)

    # 74.0s - 84.0s: TURNTABLE SWITCHES TO 45 RPM (1.35x PITCH & SPEED!)
    # Notice: at 45 RPM, a native G-minor vinyl groove shifts up by 12*log2(1.35) = +5.19 semitones (~C minor)!
    # Our turntable generator synthesizes a dedicated symphonic groove so at 45 RPM (74.0-84.0s) it locks in C minor / Bb major!
    # Rapid high-energy Mozart Molto allegro storm in C minor / G minor bridge (1.35x tempo feel!)
    fast_q = 0.14
    mozart_45rpm_passage = [
        # Virtuosic Mannheim rocket arpeggios & sighing motifs at 45 RPM energy
        (60, 63, 67, 72), (71, 67, 62, 59), (60, 63, 67, 72), (71, 67, 62, 59),
        (60, 65, 68, 72), (70, 67, 63, 58), (56, 60, 63, 68), (67, 62, 59, 55),
        (63, 62, 62, 63), (62, 62, 70, 69), (67, 66, 67, 69), (70, 72, 70, 67),
        (68, 67, 65, 63), (62, 60, 59, 60), (62, 63, 65, 67), (68, 70, 71, 72),
        (72, 70, 68, 67), (65, 63, 62, 60), (59, 62, 67, 71), (72, 67, 63, 60),
    ]
    t_m45 = 74.15
    for n1, n2, n3, n4 in mozart_45rpm_passage:
        if t_m45 + 4 * fast_q > 83.9:
            break
        for i, m in enumerate([n1, n2, n3, n4]):
            add_note(t_m45 + i * fast_q, fast_q, m, vel=0.93, voice="lead", gate_ratio=0.82)
        add_note(t_m45, 4 * fast_q, clamp_to_manual(n1 - 12), vel=0.78, voice="bass", gate_ratio=0.85)
        t_m45 += 4 * fast_q

    # 84.0s - 90.0s: Switch back to 33 1/3 RPM (1.00x) for Mozart G-minor Recapitulation & Cadence
    mozart_coda = [
        (84.10, 0.18, 63, 55), (84.28, 0.30, 62, 55), (84.58, 0.30, 62, 58),
        (84.88, 0.18, 67, 58), (85.06, 0.30, 66, 54), (85.36, 0.30, 67, 55),
        (85.66, 0.18, 70, 58), (85.84, 0.30, 69, 57), (86.14, 0.30, 70, 58),
        (86.44, 0.45, 72, 60), (86.89, 0.45, 70, 58), (87.34, 0.45, 69, 54),
        (87.79, 0.35, 67, 55), (88.14, 0.35, 62, 50), (88.49, 0.35, 58, 55),
    ]
    for tc, dur, m_top, m_bot in mozart_coda:
        add_note(tc, dur, m_top, vel=0.92, voice="lead", gate_ratio=0.88)
        add_note(tc, dur, m_bot, vel=0.78, voice="bass", gate_ratio=0.88)
    add_chord(88.85, 1.00, [55, 58, 62, 67, 70], vel=0.96, gate_ratio=0.92)

    # --------------------------------------------------------------------------
    # MOVEMENT IV (90.0s - 120.0s): BEETHOVEN — SYMPHONY NO. 9 ("ODE TO JOY" FINALE)
    #                               FULL-RACK 6-CABLE MAXIMALIST PATCH
    # --------------------------------------------------------------------------
    # 90.0s - 93.6s: Opening D-major/A7 fanfare chords while all 6 braided cables snap into the rack
    add_chord(90.40, 0.70, [50, 57, 62, 66], vel=0.88)
    add_chord(91.30, 0.70, [49, 57, 61, 69], vel=0.90)
    add_chord(92.20, 1.10, [50, 57, 62, 66, 69], vel=0.94)

    # 93.6s - 101.6s: Statement 1 — Noble Low/Mid Register "Ode to Joy" Theme (D Major)
    # D3=50, E3=52, F#3=54, G3=55, A3=57 (doubled with F#4=66, G4=67, A4=69, D4=62, E4=64)
    q = 0.25  # Quarter note = 0.25s (240 BPM half-bar or brisk 120 BPM quarter)
    ode_phrase_A = [
        (66, 1), (66, 1), (67, 1), (69, 1),
        (69, 1), (67, 1), (66, 1), (64, 1),
        (62, 1), (62, 1), (64, 1), (66, 1),
        (66, 1.5), (64, 0.5), (64, 2.0),
        (66, 1), (66, 1), (67, 1), (69, 1),
        (69, 1), (67, 1), (66, 1), (64, 1),
        (62, 1), (62, 1), (64, 1), (66, 1),
        (64, 1.5), (62, 0.5), (62, 2.0),
    ]
    t_ode = 93.60
    bass_cycle = [50, 57, 50, 57, 50, 52, 54, 57]
    b_idx = 0
    for m_lead, beats in ode_phrase_A:
        dur = beats * q
        add_note(t_ode, dur, m_lead, vel=0.92, voice="lead", gate_ratio=0.90)
        add_note(t_ode, dur, m_lead - 12, vel=0.84, voice="bass", gate_ratio=0.90)
        if beats >= 1.0:
            add_note(t_ode, dur, bass_cycle[b_idx % len(bass_cycle)], vel=0.76, voice="harmony", gate_ratio=0.88)
            b_idx += 1
        t_ode += dur

    # 101.6s - 109.6s: Statement 2 — Contrapuntal Bridge ("Seid umschlungen" / Running 8th-Note Bass)
    ode_bridge = [
        (64, 1), (64, 1), (66, 1), (62, 1),
        (64, 1), (66, 0.5), (67, 0.5), (66, 1), (62, 1),
        (64, 1), (66, 0.5), (67, 0.5), (66, 1), (64, 1),
        (62, 1), (64, 1), (57, 2.0),
        # Return of main theme in glorious counterpoint
        (66, 1), (66, 1), (67, 1), (69, 1),
        (69, 1), (67, 1), (66, 1), (64, 1),
        (62, 1), (62, 1), (64, 1), (66, 1),
        (64, 1.5), (62, 0.5), (62, 2.0),
    ]
    running_bass = [57, 61, 57, 52, 57, 61, 50, 54, 57, 61, 56, 59, 57, 54, 52, 49,
                    50, 54, 57, 62, 55, 59, 62, 67, 50, 54, 59, 62, 57, 52, 50, 50]
    rb_i = 0
    for m_lead, beats in ode_bridge:
        dur = beats * q
        add_note(t_ode, dur, m_lead, vel=0.95, voice="lead", gate_ratio=0.90)
        # Running eighth-note bass counterpoint
        n_eighths = max(1, int(round(beats * 2)))
        for e_i in range(n_eighths):
            b_m = running_bass[rb_i % len(running_bass)]
            rb_i += 1
            add_note(t_ode + e_i * (dur / n_eighths), dur / n_eighths, b_m, vel=0.80, voice="bass", gate_ratio=0.85)
        t_ode += dur

    # 109.6s - 120.0s: Grand Polyphonic Finale Climax & Prestissimo Coda (Filter Blazing to 11.5 kHz!)
    finale_chords = [
        # Full harmonic Ode to Joy climax with high D5 (74 -> folded to 62 visually, 74 in audio)
        (109.60, 0.25, [50, 57, 62, 66]), (109.85, 0.25, [50, 57, 62, 66]),
        (110.10, 0.25, [52, 59, 64, 67]), (110.35, 0.25, [54, 62, 66, 69]),
        (110.60, 0.25, [54, 62, 66, 69]), (110.85, 0.25, [55, 62, 67, 71]),
        (111.10, 0.25, [50, 57, 62, 66]), (111.35, 0.25, [49, 57, 61, 64]),
        (111.60, 0.25, [50, 54, 59, 62]), (111.85, 0.25, [50, 54, 57, 62]),
        (112.10, 0.25, [49, 57, 61, 64]), (112.35, 0.25, [50, 57, 62, 66]),
        (112.60, 0.38, [49, 57, 61, 64]), (112.98, 0.14, [50, 54, 57, 62]),
        (113.12, 0.48, [50, 54, 57, 62]),
    ]
    for tf, dur, ch in finale_chords:
        add_chord(tf, dur, ch, vel=0.97, gate_ratio=0.92)

    # 113.6s - 120.0s: Beethoven Prestissimo Fanfare & Grand Final D-Major Symphonic Chord
    prestissimo_run = [50, 54, 57, 62, 66, 69, 71, 72, 69, 66, 62, 57, 50, 54, 57, 62, 66, 69, 71, 72]
    for i, m in enumerate(prestissimo_run):
        add_note(113.65 + i * 0.12, 0.12, m, vel=0.96, voice="lead", gate_ratio=0.88)
        if i % 2 == 0:
            add_note(113.65 + i * 0.12, 0.24, clamp_to_manual(m - 12), vel=0.84, voice="bass", gate_ratio=0.88)

    # Triumphant Tutte Fanfare Chords (116.1s - 119.8s)
    add_chord(116.10, 0.35, [50, 57, 62, 66, 69, 72], vel=0.98)
    add_chord(116.45, 0.35, [49, 57, 61, 64, 69], vel=0.96)
    add_chord(116.80, 0.35, [50, 57, 62, 66, 69], vel=0.98)
    add_chord(117.15, 0.35, [55, 59, 62, 67, 71], vel=0.96)
    add_chord(117.50, 0.35, [49, 57, 61, 64, 69], vel=0.98)
    add_chord(117.85, 1.95, [50, 57, 62, 66, 69], vel=1.00, gate_ratio=0.95)

    return notes


# ==============================================================================
# 2. BROADCAST SOCIAL MEDIA CAPTIONS (32 SEGMENTS ACROSS 0:00 - 2:00)
# ==============================================================================

def build_captions():
    return [
        # MOVEMENT I: BEETHOVEN 5TH (0:00 - 0:30)
        {
            "idx": 1, "t0": 0.0, "t1": 3.8,
            "movement": "MOVEMENT I OF IV · 00:00–00:30",
            "title": "BEETHOVEN — SYMPHONY NO. 5 IN C MINOR, OP. 67 (ALLEGRO CON BRIO)",
            "subtitle": "⚡ LIVE PATCH: VCO 1 + VCO 2 → LADDER VCF · PATCHING ENV CV OUT → VCF CUTOFF CV",
            "tag": "LIVE PATCHING"
        },
        {
            "idx": 2, "t0": 3.8, "t1": 8.0,
            "movement": "MOVEMENT I OF IV · BEETHOVEN SYMPHONY NO. 5",
            "title": "THE FATE MOTIF (G – G – G – Eb) ON DUAL DETUNED 1974 SAWTOOTH VCOs",
            "subtitle": "🎛️ DIALLING VCO 2 DETUNE (+14.0 ct) & SUB-OCTAVE MIX FOR MASSIVE ANALOGUE BRASS GROWL",
            "tag": "DUAL VCO UNISON"
        },
        {
            "idx": 3, "t0": 8.0, "t1": 14.0,
            "movement": "MOVEMENT I OF IV · BEETHOVEN SYMPHONY NO. 5",
            "title": "ALLEGRO CON BRIO — IMITATIVE STRETTO ACROSS THE 25-KEY MANUAL (C3–C5)",
            "subtitle": "🎛️ SWEEPING 24 dB/OCT LADDER FILTER CUTOFF (280 Hz → 4,800 Hz) & LADDER DRIVE (1.4x → 3.2x)",
            "tag": "FILTER SWEEP"
        },
        {
            "idx": 4, "t0": 14.0, "t1": 18.5,
            "movement": "MOVEMENT I OF IV · BEETHOVEN SYMPHONY NO. 5",
            "title": "HEROIC HORN CALL & SECOND SUBJECT IN Eb MAJOR",
            "subtitle": "🎛️ BOOSTING ENV MOD DEPTH (1,800 ct → 3,600 ct) ON 15° TILTED ANODISED CONSOLE",
            "tag": "ENVELOPE CONTOUR"
        },
        {
            "idx": 5, "t0": 18.5, "t1": 23.5,
            "movement": "MOVEMENT I OF IV · BEETHOVEN SYMPHONY NO. 5",
            "title": "CONTRAPUNTAL BASS PULSE & RESONANT LADDER HARMONICS",
            "subtitle": "🎹 HINGED 25-KEY PERFORMANCE WITH RESONANCE DIALLED TO 6.8 Q",
            "tag": "24 dB/OCT LADDER"
        },
        {
            "idx": 6, "t0": 23.5, "t1": 30.0,
            "movement": "MOVEMENT I OF IV · BEETHOVEN SYMPHONY NO. 5",
            "title": "STORMY C MINOR DEVELOPMENT & SEARING HARMONIC BLAZE CLIMAX",
            "subtitle": "🔥 OPENING CUTOFF FREQ TO 7,400 Hz AT 3.8x LADDER SATURATION DRIVE",
            "tag": "SYMPHONIC CLIMAX"
        },

        # MOVEMENT II: BACH / VIVALDI BAROQUE STORM (0:30 - 1:00)
        {
            "idx": 7, "t0": 30.0, "t1": 34.5,
            "movement": "MOVEMENT II OF IV · 00:30–01:00",
            "title": "BACH — TOCCATA & FUGUE IN D MINOR, BWV 565 / VIVALDI — WINTER ALLEGRO",
            "subtitle": "⚡ LIVE CABLE SWITCH: LFO CV OUT → VCO PITCH CV & VCF OUT → BBD DELAY IN",
            "tag": "LIVE RE-PATCHING"
        },
        {
            "idx": 8, "t0": 34.5, "t1": 38.5,
            "movement": "MOVEMENT II OF IV · BACH TOCCATA IN D MINOR, BWV 565",
            "title": "ICONIC MORDENT & DIMINISHED-7TH CATHEDRAL ARPEGGIO OVER D3 PEDAL",
            "subtitle": "🎛️ MORPHING VCO 1 WAVE TO REED/SQUARE (0.88) + BBD ANALOGUE DELAY (240 ms · 36% MIX)",
            "tag": "BAROQUE ORGAN VOICING"
        },
        {
            "idx": 9, "t0": 38.5, "t1": 44.0,
            "movement": "MOVEMENT II OF IV · BACH TOCCATA IN D MINOR, BWV 565",
            "title": "RAPID 16TH-NOTE BARIOLAGE ARPEGGIOS & PEDAL COUNTERPOINT",
            "subtitle": "🎹 VIRTUOSO 25-KEY ARTICULATION WITH SNAPPY ADSR CONTOUR & STEREO BBD ECHOES",
            "tag": "16TH-NOTE ARPEGGIOS"
        },
        {
            "idx": 10, "t0": 44.0, "t1": 48.0,
            "movement": "MOVEMENT II OF IV · BACH TOCCATA IN D MINOR, BWV 565",
            "title": "ASCENDING BAROQUE SEQUENCE & INTER-ROW CORRIDOR CABLE ROUTING",
            "subtitle": "🎛️ SWEEPING CUTOFF FREQ (1.2 kHz → 5.6 kHz) & LFO VIBRATO RATE (5.8 Hz)",
            "tag": "CORRIDOR PATCH BAY"
        },
        {
            "idx": 11, "t0": 48.0, "t1": 53.0,
            "movement": "MOVEMENT II OF IV · VIVALDI 'WINTER' (ALLEGRO NON MOLTO)",
            "title": "VIVALDI — THE FOUR SEASONS: 'WINTER' ICY TREMOLANDO CHORDS",
            "subtitle": "❄️ STACCATO BAROQUE HARMONIC STORM WITH RESONANT PEAK (6.2 Q) & BBD FEEDBACK",
            "tag": "VIVALDI WINTER STORM"
        },
        {
            "idx": 12, "t0": 53.0, "t1": 60.0,
            "movement": "MOVEMENT II OF IV · VIVALDI 'WINTER' (ALLEGRO NON MOLTO)",
            "title": "BLAZING SOLO VIOLIN LIGHTNING SCALES & D MINOR CADENCE",
            "subtitle": "🔥 DIALLING BBD DELAY MIX TO 48% & CUTOFF TO 6,500 Hz ACROSS C3–C5",
            "tag": "VIRTUOSO CASCADE"
        },

        # MOVEMENT III: MOZART SYMPHONY NO. 40 + TURNTABLE (1:00 - 1:30)
        {
            "idx": 13, "t0": 60.0, "t1": 64.5,
            "movement": "MOVEMENT III OF IV · 01:00–01:30",
            "title": "MOZART — SYMPHONY NO. 40 IN G MINOR, K. 550 (MOLTO ALLEGRO)",
            "subtitle": "💿 LIVE PATCH: PHONO OUT → VCF IN · LOWERING S-SHAPED TONEARM ONTO 180g LP (33⅓ RPM)",
            "tag": "VINYL + MODULAR"
        },
        {
            "idx": 14, "t0": 64.5, "t1": 69.5,
            "movement": "MOVEMENT III OF IV · MOZART SYMPHONY NO. 40 IN G MINOR",
            "title": "OPENING G MINOR SUBJECT (Eb – D – D) OVER SPINNING 33⅓ RPM VINYL GROOVE",
            "subtitle": "🎛️ SNAPPY SPICCATO ADSR (ATTACK 5 ms · DECAY 180 ms) + WARM SUB-OCTAVE MIX",
            "tag": "33⅓ RPM NATIVE LP"
        },
        {
            "idx": 15, "t0": 69.5, "t1": 74.0,
            "movement": "MOVEMENT III OF IV · MOZART SYMPHONY NO. 40 IN G MINOR",
            "title": "SEQUENTIAL CLASSICAL COUNTERPOINT & 240-SEGMENT STROBE PLATTER",
            "subtitle": "💿 ANISOTROPIC JET-BLACK 180g VINYL TRACKING UNDER NEON-AMBER STROBE PRISM",
            "tag": "DIRECT-DRIVE DECK"
        },
        {
            "idx": 16, "t0": 74.0, "t1": 79.5,
            "movement": "MOVEMENT III OF IV · MOZART SYMPHONY NO. 40 IN G MINOR",
            "title": "LIVE TURNTABLE SPEED SHIFT: 33⅓ RPM → 45 RPM (1.35x PITCH & TEMPO!)",
            "subtitle": "⚡ FLIPPING SPEED SWITCH TO 45 RPM — PLATTER ACCELERATES 1.35x FOR HIGH-ENERGY BRIDGE",
            "tag": "45 RPM SPEED SHIFT"
        },
        {
            "idx": 17, "t0": 79.5, "t1": 84.0,
            "movement": "MOVEMENT III OF IV · MOZART SYMPHONY NO. 40 IN G MINOR",
            "title": "MANNHEIM ROCKET ARPEGGIOS & FILTER SWEEP AT 45 RPM",
            "subtitle": "🎛️ SWEEPING LADDER CUTOFF (1.1 kHz → 6.4 kHz) SYNCHRONIZED WITH 45 RPM VINYL LAYER",
            "tag": "SYMPHONIC HYBRID"
        },
        {
            "idx": 18, "t0": 84.0, "t1": 90.0,
            "movement": "MOVEMENT III OF IV · MOZART SYMPHONY NO. 40 IN G MINOR",
            "title": "RETURN TO 33⅓ RPM (1.00x) FOR THE NOBLE G MINOR CLASSICAL CADENCE",
            "subtitle": "💿 POSITION-CONTINUOUS 45 → 33⅓ RPM TRANSITION & CADENTIAL TUTTI",
            "tag": "CLASSICAL CADENCE"
        },

        # MOVEMENT IV: BEETHOVEN 9TH ODE TO JOY FINALE (1:30 - 2:00)
        {
            "idx": 19, "t0": 90.0, "t1": 94.5,
            "movement": "MOVEMENT IV OF IV · 01:30–02:00",
            "title": "BEETHOVEN — SYMPHONY NO. 9 IN D MINOR, OP. 125 ('ODE TO JOY' FINALE)",
            "subtitle": "⚡ FULL-RACK MAXIMALIST PATCH: ALL 6 BRAIDED CABLES ACROSS ALL 4 BAYS + VINYL DECK",
            "tag": "6-CABLE MAXIMALIST"
        },
        {
            "idx": 20, "t0": 94.5, "t1": 101.6,
            "movement": "MOVEMENT IV OF IV · BEETHOVEN 9TH 'ODE TO JOY' FINALE",
            "title": "NOBLE CELLO & BARITONE STATEMENT OF THE 'ODE TO JOY' HYMN",
            "subtitle": "🎛️ WARM LADDER FILTER (850 Hz → 2,800 Hz) + PHONO OUT → VCA IN ORCHESTRAL PAD",
            "tag": "ODE TO JOY THEME"
        },
        {
            "idx": 21, "t0": 101.6, "t1": 109.6,
            "movement": "MOVEMENT IV OF IV · BEETHOVEN 9TH 'ODE TO JOY' FINALE",
            "title": "TWO-VOICE CONTRAPUNTAL VARIATION & RUNNING 8TH-NOTE BASSLINE",
            "subtitle": "🎛️ DIALLING RESONANCE (7.8 Q), ENV MOD DEPTH (3,800 ct) & LFO → VCA TREMOLO",
            "tag": "POLYPHONIC COUNTERPOINT"
        },
        {
            "idx": 22, "t0": 109.6, "t1": 115.0,
            "movement": "MOVEMENT IV OF IV · BEETHOVEN 9TH 'ODE TO JOY' FINALE",
            "title": "TRIUMPHANT FULL-STUDIO RECAPITULATION & PRESTISSIMO FANFARE",
            "subtitle": "🔥 SWEEPING CUTOFF FREQ TO 11,500 Hz · LADDER DRIVE 4.2x · BBD DELAY MIX 44%",
            "tag": "PRESTISSIMO CLIMAX"
        },
        {
            "idx": 23, "t0": 115.0, "t1": 120.0,
            "movement": "MOVEMENT IV OF IV · BEETHOVEN 9TH 'ODE TO JOY' FINALE",
            "title": "GRAND D MAJOR SYMPHONIC FINALE — CHRONO ANALOGUE // SYSTEM 1974",
            "subtitle": "✨ 4 SYMPHONIES · 6 BRAIDED PATCH CABLES · 16 BAKELITE KNOBS · 180g TURNTABLE · 1080p60",
            "tag": "SYSTEM 1974 MASTER"
        },
    ]


# ==============================================================================
# 3. LIVE CABLE PATCHING, KNOB SWEEPS, TURNTABLE & CAMERA CHOREOGRAPHY
# ==============================================================================

SOCKET_LABELS = {
    "socket_vco1_out": "VCO 1 OUT",
    "socket_vco2_out": "VCO 2 OUT",
    "socket_vcf_out": "VCF OUT",
    "socket_env_out": "ENV CV OUT",
    "socket_lfo_out": "LFO CV OUT",
    "socket_phono_out": "PHONO OUT",
    "socket_vco_pitch_cv": "VCO PITCH CV",
    "socket_vcf_in": "VCF AUDIO IN",
    "socket_vcf_cutoff_cv": "VCF CUTOFF CV",
    "socket_vca_in": "VCA AUDIO IN",
    "socket_vca_cv": "VCA GAIN CV",
    "socket_dly_in": "DELAY IN",
}

CABLE_COLORS = [
    ("#d95b26", "Burnt Orange"),
    ("#dba02b", "Ochre Gold"),
    ("#2a8f9d", "Teal Cyan"),
    ("#c8372d", "Crimson Red"),
    ("#6b934c", "Sage Olive"),
    ("#e8dec8", "Warm Cream"),
]


def get_cable_state_at(t: float):
    """
    Returns:
      active_cables: list of (from_id, to_id)
      preview_patch: None or { "from_id": str, "to_id": str, "progress": float (0..1) }
      status_text: str
    """
    # Base cable always present: VCO 1 OUT -> VCF AUDIO IN
    cables = [
        ("socket_vco1_out", "socket_vcf_in"),
    ]
    # VCF OUT -> VCA AUDIO IN is explicitly patched in Movements I-III; in Movement IV (t >= 90.1),
    # VCF OUT routes to DELAY IN while VCA AUDIO IN receives PHONO OUT (with VCF OUT normalled to VCA IN),
    # so all 6 [OUT] sockets across all 4 bays are occupied by the 6 braided patch cables!
    if t < 90.1:
        cables.append(("socket_vcf_out", "socket_vca_in"))

    preview = None
    status = "CHRONO ANALOGUE 1974 — Live Four-Symphony Modular & Turntable Performance"

    # Progressive 4-Movement Cable Choreography (4 -> 5 -> 5 -> 6 cables):
    # Mov 1 (0 - 30s, 4 cables):
    #   1.0 - 1.8s: Patch VCO 2 OUT -> VCF AUDIO IN
    #   2.5 - 3.3s: Patch ENV CV OUT -> VCF CUTOFF CV
    # Mov 2 (30 - 60s, 5 cables):
    #   30.1s: Unplug VCO 2 OUT -> VCF AUDIO IN to switch to Baroque reed organ + vibrato + BBD echo
    #   30.4 - 31.4s: Patch LFO CV OUT -> VCO PITCH CV
    #   31.6 - 32.6s: Patch VCF OUT -> DELAY IN
    # Mov 3 (60 - 90s, 5 cables):
    #   60.1s: Unplug LFO CV OUT -> VCO PITCH CV & VCF OUT -> DELAY IN for crisp Classical spiccato + vinyl filter
    #   60.3 - 61.0s: Patch VCO 2 OUT -> VCF AUDIO IN
    #   61.1 - 61.9s: Patch PHONO OUT -> VCF AUDIO IN (Turntable vinyl into 24 dB/oct ladder filter!)
    # Mov 4 (90 - 120s, 6 cables across all 6 [OUT] sockets & all 4 bays):
    #   90.1s: Unplug PHONO OUT -> VCF AUDIO IN & VCF OUT -> VCA AUDIO IN to configure 6-cable maximalist patch
    #   90.3 - 91.1s: Patch VCF OUT -> DELAY IN
    #   91.2 - 92.0s: Patch PHONO OUT -> VCA AUDIO IN
    #   92.1 - 92.9s: Patch LFO CV OUT -> VCA GAIN CV

    if (1.8 <= t < 30.1) or (t >= 61.0):
        cables.append(("socket_vco2_out", "socket_vcf_in"))
    if t >= 3.3:
        cables.append(("socket_env_out", "socket_vcf_cutoff_cv"))
    if 31.4 <= t < 60.1:
        cables.append(("socket_lfo_out", "socket_vco_pitch_cv"))
    if (32.6 <= t < 60.1) or (t >= 91.1):
        cables.append(("socket_vcf_out", "socket_dly_in"))
    if 61.9 <= t < 90.1:
        cables.append(("socket_phono_out", "socket_vcf_in"))
    if t >= 92.0:
        cables.append(("socket_phono_out", "socket_vca_in"))
    if t >= 92.9:
        cables.append(("socket_lfo_out", "socket_vca_cv"))

    # Check active animated preview cable windows
    patch_windows = [
        (1.0, 1.8, "socket_vco2_out", "socket_vcf_in"),
        (2.5, 3.3, "socket_env_out", "socket_vcf_cutoff_cv"),
        (30.4, 31.4, "socket_lfo_out", "socket_vco_pitch_cv"),
        (31.6, 32.6, "socket_vcf_out", "socket_dly_in"),
        (60.3, 61.0, "socket_vco2_out", "socket_vcf_in"),
        (61.1, 61.9, "socket_phono_out", "socket_vcf_in"),
        (90.3, 91.1, "socket_vcf_out", "socket_dly_in"),
        (91.2, 92.0, "socket_phono_out", "socket_vca_in"),
        (92.1, 92.9, "socket_lfo_out", "socket_vca_cv"),
    ]
    for p_t0, p_t1, s_id, d_id in patch_windows:
        if p_t0 <= t < p_t1:
            prog = (t - p_t0) / (p_t1 - p_t0)
            preview = {"from_id": s_id, "to_id": d_id, "progress": round(prog, 4)}
            status = f"LIVE PATCHING: {SOCKET_LABELS[s_id]} → {SOCKET_LABELS[d_id]} ({int(prog * 100)}%)"
            break

    return cables, preview, status


def interp_keyframes(t: float, keyframes: list) -> float:
    """Smooth cosine-eased interpolation between (time_s, val) keyframes."""
    if t <= keyframes[0][0]:
        return float(keyframes[0][1])
    if t >= keyframes[-1][0]:
        return float(keyframes[-1][1])
    for i in range(len(keyframes) - 1):
        t0, v0 = keyframes[i]
        t1, v1 = keyframes[i + 1]
        if t0 <= t <= t1:
            if t1 <= t0 + 1e-6:
                return float(v1)
            u = (t - t0) / (t1 - t0)
            s = 0.5 - 0.5 * math.cos(math.pi * u)
            return float(v0 + (v1 - v0) * s)
    return float(keyframes[-1][1])


KNOB_KEYFRAMES = {
    "knob_vco1_pitch": [
        (0.0, -0.4), (0.8, 0.0), (30.0, 0.0),
        (30.4, 12.0), (33.3, 0.0), (120.0, 0.0),
    ],
    "knob_vco1_wave": [
        (0.0, 0.67), (29.5, 0.67),       # Mov 1: Sawtooth brass
        (30.5, 0.88), (59.5, 0.86),      # Mov 2: Reed/Square pipe organ + harpsichord
        (60.5, 0.52), (89.5, 0.58),      # Mov 3: Warm Triangle/Saw classical strings
        (90.5, 0.72), (120.0, 0.78),     # Mov 4: Full rich Saw/Square brass choir
    ],
    "knob_vco2_detune": [
        (0.0, 6.0), (4.5, 14.0), (22.0, 18.0), (29.8, 12.0),
        (30.5, 7.0), (59.5, 9.0),
        (60.5, 6.5), (74.0, 11.0), (89.5, 8.0),
        (90.5, 12.0), (109.0, 19.0), (120.0, 16.0),
    ],
    "knob_vco2_mix": [
        (0.0, 0.35), (2.0, 0.75), (29.8, 0.80),
        (30.5, 0.70), (59.5, 0.72),
        (60.5, 0.58), (74.0, 0.72), (89.5, 0.65),
        (90.5, 0.82), (120.0, 0.90),
    ],
    "knob_vcf_cutoff": [
        # Mov 1: Beethoven 5th — dark brassy growl (280 Hz) sweeping to searing blaze (7400 Hz)
        (0.0, 380.0), (1.0, 950.0), (2.5, 420.0), (4.5, 280.0),
        (9.5, 2400.0), (13.8, 4800.0), (16.5, 1650.0), (21.5, 3600.0),
        (24.5, 5800.0), (28.2, 7400.0), (29.9, 2200.0),
        # Mov 2: Bach / Vivaldi — articulate baroque sweep (900 Hz -> 6500 Hz)
        (30.2, 1100.0), (33.5, 2800.0), (36.8, 1350.0), (42.5, 3900.0),
        (47.5, 5600.0), (49.0, 1800.0), (54.0, 4600.0), (58.5, 6500.0), (59.9, 1900.0),
        # Mov 3: Mozart 40 + Turntable — snappy spiccato filter (1100 Hz -> 6400 Hz)
        (60.2, 1200.0), (65.0, 2600.0), (70.0, 1850.0), (74.0, 1100.0),
        (78.5, 4400.0), (82.5, 6400.0), (86.0, 3200.0), (89.8, 2400.0),
        # Mov 4: Beethoven 9th Ode to Joy — warm cello (850 Hz) to grand finale (11500 Hz)
        (90.2, 850.0), (94.0, 1150.0), (98.5, 2400.0), (101.6, 2800.0),
        (106.0, 4800.0), (109.6, 6800.0), (114.5, 9600.0), (118.0, 11500.0), (120.0, 8200.0),
    ],
    "knob_vcf_resonance": [
        (0.0, 2.5), (8.0, 4.8), (18.0, 6.8), (28.0, 5.5),
        (30.5, 3.8), (40.0, 5.4), (50.0, 6.2), (59.5, 4.5),
        (60.5, 3.2), (74.5, 5.8), (85.0, 4.2),
        (90.5, 3.5), (103.0, 7.8), (112.0, 6.4), (120.0, 5.0),
    ],
    "knob_vcf_env_amt": [
        (0.0, 1600.0), (3.5, 2600.0), (15.0, 3600.0), (29.8, 2800.0),
        (30.5, 2200.0), (45.0, 3100.0), (59.8, 2500.0),
        (60.5, 2900.0), (76.0, 3500.0), (89.8, 2600.0),
        (90.5, 2000.0), (104.0, 3800.0), (115.0, 4200.0), (120.0, 3400.0),
    ],
    "knob_vcf_drive": [
        (0.0, 1.4), (6.0, 2.2), (13.5, 3.2), (27.5, 3.8), (29.9, 2.0),
        (30.5, 1.8), (48.0, 2.6), (58.0, 3.1), (59.9, 1.8),
        (60.5, 1.6), (75.0, 2.5), (88.0, 2.1),
        (90.5, 2.2), (105.0, 3.3), (114.0, 4.2), (120.0, 3.6),
    ],
    "knob_env_attack": [
        (0.0, 0.012), (29.9, 0.012),
        (30.2, 0.006), (59.9, 0.006),
        (60.2, 0.005), (89.9, 0.005),
        (90.2, 0.018), (109.0, 0.008), (120.0, 0.010),
    ],
    "knob_env_decay": [
        (0.0, 0.34), (29.9, 0.34),
        (30.2, 0.22), (59.9, 0.22),
        (60.2, 0.18), (89.9, 0.20),
        (90.2, 0.42), (109.0, 0.32), (120.0, 0.45),
    ],
    "knob_env_sustain": [
        (0.0, 0.68), (29.9, 0.72),
        (30.2, 0.52), (59.9, 0.55),
        (60.2, 0.28), (74.0, 0.42), (89.9, 0.35),
        (90.2, 0.74), (110.0, 0.85), (120.0, 0.82),
    ],
    "knob_env_release": [
        (0.0, 0.38), (29.9, 0.38),
        (30.2, 0.28), (59.9, 0.30),
        (60.2, 0.20), (89.9, 0.24),
        (90.2, 0.48), (116.0, 0.85), (120.0, 0.90),
    ],
    "knob_lfo_rate": [
        (0.0, 3.5), (30.0, 5.8), (48.0, 6.4), (60.0, 4.2), (90.0, 5.2), (112.0, 6.0), (120.0, 5.5),
    ],
    "knob_lfo_depth": [
        (0.0, 0.08), (30.0, 0.14), (48.0, 0.18), (60.0, 0.06), (90.0, 0.22), (112.0, 0.28), (120.0, 0.24),
    ],
    "knob_dly_time": [
        (0.0, 0.30), (30.0, 0.24), (48.0, 0.22), (60.0, 0.25), (90.0, 0.25), (120.0, 0.25),
    ],
    "knob_dly_mix": [
        (0.0, 0.18), (30.0, 0.36), (48.0, 0.44), (55.0, 0.48),
        (60.0, 0.22), (75.0, 0.30), (90.0, 0.34), (105.0, 0.42), (115.0, 0.46), (120.0, 0.44),
    ],
}


def get_knobs_and_highlight_at(t: float):
    vals = {k: round(interp_keyframes(t, kf), 4) for k, kf in KNOB_KEYFRAMES.items()}
    # Cycle featured/highlighted knob across all 16 knobs synchronized with each movement's caption & action
    if t < 1.0:
        hl = "knob_vco1_pitch"
    elif t < 5.5:
        hl = "knob_vco2_detune" if t < 3.8 else "knob_vco2_mix"
    elif t < 14.0:
        hl = "knob_vcf_cutoff" if int(t * 1.2) % 2 == 0 else "knob_vcf_drive"
    elif t < 18.5:
        hl = "knob_vcf_env_amt"
    elif t < 23.5:
        hl = "knob_vcf_resonance"
    elif t < 30.0:
        hl = "knob_vcf_cutoff" if t < 27.0 else "knob_vcf_drive"
    elif t < 36.5:
        hl = "knob_vco1_wave" if t < 34.5 else "knob_dly_time"
    elif t < 44.0:
        hl = "knob_env_attack" if t < 40.5 else "knob_dly_mix"
    elif t < 48.0:
        hl = "knob_vcf_cutoff" if t < 46.2 else "knob_lfo_rate"
    elif t < 53.0:
        hl = "knob_vcf_resonance" if t < 50.8 else "knob_lfo_depth"
    elif t < 60.0:
        hl = "knob_dly_mix" if t < 56.5 else "knob_vcf_cutoff"
    elif t < 69.5:
        hl = "knob_env_decay" if t < 66.8 else "knob_env_sustain"
    elif t < 74.0:
        hl = "knob_vco2_mix"
    elif t < 84.0:
        hl = "knob_vcf_cutoff"
    elif t < 90.0:
        hl = "knob_env_release"
    elif t < 101.6:
        hl = "knob_vcf_cutoff"
    elif t < 109.6:
        hl = "knob_vcf_resonance" if t < 105.5 else "knob_vcf_env_amt"
    else:
        hl = "knob_vcf_cutoff" if int(t * 1.5) % 2 == 0 else "knob_vcf_drive"
    return vals, hl


def get_turntable_state_at(t: float):
    """
    Turntable choreography:
      - 0.0 - 60.8s: Motor off, tonearm raised at rest (33.33 RPM selected)
      - 60.8 - 61.8s: Platter motor starts spinning (33.33 RPM), tonearm cues & lowers onto 180g LP!
      - 61.8 - 74.0s: Playing at 33 1/3 RPM (1.00x)
      - 74.0 - 84.0s: Speed switch flipped to 45 RPM (1.35x pitch/speed!)
      - 84.0 - 120.0s: Switched back to 33 1/3 RPM (1.00x), continuing through Movement IV maximalist finale!
    """
    motor_on = t >= 60.8
    tonearm_lowered = t >= 61.6
    rpm = 45.0 if (74.0 <= t < 84.0) else 33.333333
    rate = rpm / 33.333333
    if not motor_on:
        state = "stopped_rest"
    elif not tonearm_lowered:
        state = "cued_spinning"
    else:
        state = "playing_45" if rpm > 40.0 else "playing_33"
    return {
        "motorOn": motor_on,
        "tonearmLowered": tonearm_lowered,
        "rpm": round(rpm, 2),
        "playbackRate": round(rate, 3),
        "state": state,
    }


CAMERA_PRESETS = {
    "opening_studio": {
        "pos": [0.02, 0.52, 1.18],
        "target": [0.02, 0.15, 0.02],
        "fov": 40.0,
    },
    "synth_rack_closeup": {
        "pos": [-0.22, 0.34, 0.76],
        "target": [-0.22, 0.21, -0.04],
        "fov": 36.0,
    },
    "patch_and_keys": {
        "pos": [-0.22, 0.37, 0.90],
        "target": [-0.22, 0.16, 0.02],
        "fov": 38.5,
    },
    "turntable_closeup": {
        "pos": [0.44, 0.42, 0.58],
        "target": [0.44, 0.04, 0.02],
        "fov": 33.0,
    },
    "side_profile_tilt": {
        "pos": [-0.66, 0.35, 0.85],
        "target": [-0.15, 0.16, 0.02],
        "fov": 39.0,
    },
}

# Camera choreography keyframes: (time_s, preset_id, subtle_offset_pos, subtle_offset_target)
CAMERA_SHOT_KEYFRAMES = [
    # MOVEMENT I (0 - 30s): Beethoven 5th
    (0.0,  "synth_rack_closeup", [-0.03, 0.00, 0.02], [-0.03, 0.00, 0.00]),
    (4.2,  "synth_rack_closeup", [0.03, 0.00, 0.00],  [0.02, 0.00, 0.00]),
    (5.8,  "patch_and_keys",     [-0.03, 0.00, 0.01], [-0.02, 0.00, 0.00]),
    (13.2, "patch_and_keys",     [0.04, 0.00, 0.00],  [0.03, 0.00, 0.00]),
    (14.8, "side_profile_tilt",  [0.00, 0.01, 0.02],  [0.00, 0.00, 0.00]),
    (21.8, "side_profile_tilt",  [0.04, 0.00, -0.02], [0.01, 0.00, 0.00]),
    (23.5, "opening_studio",     [-0.05, 0.02, -0.04],[-0.02, 0.01, 0.00]),
    (29.2, "opening_studio",     [0.04, 0.00, 0.02],  [0.01, 0.00, 0.00]),

    # MOVEMENT II (30 - 60s): Bach / Vivaldi Baroque Storm
    (30.0, "synth_rack_closeup", [0.04, 0.01, 0.02],  [0.04, -0.01, 0.00]),
    (34.8, "synth_rack_closeup", [-0.02, 0.00, 0.00], [0.00, 0.00, 0.00]),
    (36.4, "patch_and_keys",     [-0.04, 0.00, 0.01], [-0.03, 0.00, 0.00]),
    (46.2, "patch_and_keys",     [0.04, 0.00, 0.00],  [0.03, 0.00, 0.00]),
    (47.8, "side_profile_tilt",  [0.01, 0.01, 0.02],  [0.00, 0.00, 0.00]),
    (53.8, "synth_rack_closeup", [0.05, 0.00, 0.04],  [0.03, -0.01, 0.00]),
    (59.2, "opening_studio",     [0.00, 0.01, -0.02], [0.00, 0.00, 0.00]),

    # MOVEMENT III (60 - 90s): Mozart 40 + Direct-Drive Turntable
    (60.0, "synth_rack_closeup", [0.04, -0.01, 0.02], [0.04, -0.01, 0.00]),
    (62.0, "synth_rack_closeup", [0.06, -0.01, 0.02], [0.05, -0.01, 0.00]),
    (63.2, "turntable_closeup",  [-0.03, 0.02, 0.03], [-0.02, 0.00, 0.00]),
    (66.5, "turntable_closeup",  [0.03, 0.00, -0.02], [0.01, 0.00, 0.00]),
    (68.0, "patch_and_keys",     [0.02, 0.00, 0.01],  [0.02, 0.00, 0.00]),
    (72.8, "turntable_closeup",  [-0.02, 0.01, 0.01], [0.00, 0.00, 0.00]),
    (79.0, "patch_and_keys",     [0.00, 0.00, 0.00],  [0.00, 0.00, 0.00]),
    (83.2, "turntable_closeup",  [0.02, 0.01, 0.00],  [0.00, 0.00, 0.00]),
    (85.5, "turntable_closeup",  [0.04, 0.02, -0.02], [0.01, 0.00, 0.00]),
    (87.0, "opening_studio",     [0.02, 0.00, -0.02], [0.01, 0.00, 0.00]),
    (89.2, "opening_studio",     [-0.02, 0.01, 0.00], [0.00, 0.00, 0.00]),

    # MOVEMENT IV (90 - 120s): Beethoven 9th Ode to Joy Finale
    (90.0, "synth_rack_closeup", [-0.02, 0.00, 0.03], [-0.01, -0.01, 0.00]),
    (94.2, "synth_rack_closeup", [0.05, 0.01, 0.01],  [0.04, 0.00, 0.00]),
    (95.8, "patch_and_keys",     [-0.03, 0.00, 0.01], [-0.02, 0.00, 0.00]),
    (103.5,"side_profile_tilt",  [0.00, 0.01, 0.02],  [0.00, 0.00, 0.00]),
    (109.2,"turntable_closeup",  [-0.04, 0.03, 0.05], [-0.02, 0.01, 0.00]),
    (112.5,"opening_studio",     [-0.04, 0.02, -0.06],[-0.01, 0.01, 0.00]),
    (120.0,"opening_studio",     [0.02, 0.04, 0.04],  [0.02, 0.00, 0.00]),
]


def get_camera_at(t: float):
    if t <= CAMERA_SHOT_KEYFRAMES[0][0]:
        _, p_id, off_p, off_t = CAMERA_SHOT_KEYFRAMES[0]
        base = CAMERA_PRESETS[p_id]
        return {
            "presetId": p_id,
            "pos": [round(base["pos"][j] + off_p[j], 4) for j in range(3)],
            "target": [round(base["target"][j] + off_t[j], 4) for j in range(3)],
            "fov": base["fov"],
        }
    for i in range(len(CAMERA_SHOT_KEYFRAMES) - 1):
        t0, p0, op0, ot0 = CAMERA_SHOT_KEYFRAMES[i]
        t1, p1, op1, ot1 = CAMERA_SHOT_KEYFRAMES[i + 1]
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, (t1 - t0))
            s = 0.5 - 0.5 * math.cos(math.pi * u)
            b0 = CAMERA_PRESETS[p0]
            b1 = CAMERA_PRESETS[p1]
            pos = [
                round((b0["pos"][j] + op0[j]) * (1.0 - s) + (b1["pos"][j] + op1[j]) * s, 4)
                for j in range(3)
            ]
            target = [
                round((b0["target"][j] + ot0[j]) * (1.0 - s) + (b1["target"][j] + ot1[j]) * s, 4)
                for j in range(3)
            ]
            fov = round(b0["fov"] * (1.0 - s) + b1["fov"] * s, 2)
            active_id = p0 if u < 0.5 else p1
            return {"presetId": active_id, "pos": pos, "target": target, "fov": fov}
    _, p_id, off_p, off_t = CAMERA_SHOT_KEYFRAMES[-1]
    base = CAMERA_PRESETS[p_id]
    return {
        "presetId": p_id,
        "pos": [round(base["pos"][j] + off_p[j], 4) for j in range(3)],
        "target": [round(base["target"][j] + off_t[j], 4) for j in range(3)],
        "fov": base["fov"],
    }


# ==============================================================================
# 4. SAMPLE-ACCURATE 48 kHz STEREO AUDIO SYNTHESISER (MOOG LADDER + BBD + VINYL)
# ==============================================================================

def synthesize_showcase_audio_48k(notes: list):
    """
    Synthesizes the full 120.0-second (5,760,000 samples @ 48,000 Hz) stereo master audio:
      - Dual VCO (morphing Sine/Tri/Saw/Square + detuned Saw + -1 oct Square sub)
      - 24 dB/oct 4-pole cascaded ladder low-pass filter with nonlinear tanh drive & resonance
      - ADSR contour generator modulating both VCA gate and VCF cutoff CV
      - LFO modulating VCO pitch CV (Movement II) and VCA tremolo/chorus CV (Movement IV)
      - Stereo BBD analogue delay with warm 2.6 kHz lowpass feedback loop
      - Direct-drive vinyl turntable accompaniment (1:01.6 - 2:00.0) with genuine 33 1/3 <-> 45 RPM
        continuous phase/speed resampling (1.00x <-> 1.35x) and dynamic VCF filtering!
    """
    print(f"Synthesizing {DURATION_S}s master showcase audio at {SAMPLE_RATE} Hz ({TOTAL_SAMPLES:,} stereo samples)...")
    synth_L = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
    synth_R = np.zeros(TOTAL_SAMPLES, dtype=np.float64)

    # Precompute 60 Hz cutoff & resonance curves so held notes and turntable filter sweeps are sample-accurate
    grid_t = np.linspace(0.0, DURATION_S, TOTAL_FRAMES + 1)
    grid_cutoff = np.array([interp_keyframes(float(gt), KNOB_KEYFRAMES["knob_vcf_cutoff"]) for gt in grid_t])
    grid_drive = np.array([interp_keyframes(float(gt), KNOB_KEYFRAMES["knob_vcf_drive"]) for gt in grid_t])

    # Render each note with bandlimited harmonic oscillators + dynamic ADSR & LFO
    for n_idx, note in enumerate(notes):
        t0 = note["t0"]
        t1 = note["t1"]
        midi = note["midi"]
        vel = note["vel"]
        voice = note["voice"]

        tm = 0.5 * (t0 + t1)
        knobs, _ = get_knobs_and_highlight_at(tm)
        cables, _, _ = get_cable_state_at(tm)
        cable_set = set(cables)

        atk = max(0.004, knobs["knob_env_attack"])
        dec = max(0.02, knobs["knob_env_decay"])
        sus = knobs["knob_env_sustain"]
        rel = max(0.02, knobs["knob_env_release"])

        s_start = max(0, int(t0 * SAMPLE_RATE))
        s_end = min(TOTAL_SAMPLES, int((t1 + rel * 1.6) * SAMPLE_RATE))
        if s_end <= s_start:
            continue

        n_len = s_end - s_start
        lt = np.arange(n_len, dtype=np.float64) / SAMPLE_RATE
        abs_t = t0 + lt
        note_dur = max(0.01, t1 - t0)

        # ADSR envelope
        env = np.empty(n_len, dtype=np.float64)
        atk_mask = lt < atk
        env[atk_mask] = lt[atk_mask] / atk
        sus_mask = (lt >= atk) & (lt < note_dur)
        env[sus_mask] = sus + (1.0 - sus) * np.exp(-(lt[sus_mask] - atk) / (dec * 0.45))
        rel_mask = lt >= note_dur
        val_at_rel = sus + (1.0 - sus) * math.exp(-max(0.0, note_dur - atk) / (dec * 0.45))
        env[rel_mask] = val_at_rel * np.exp(-(lt[rel_mask] - note_dur) / (rel * 0.35))

        # Base frequency & LFO pitch modulation (if LFO -> VCO PITCH CV is patched, or subtle organic warmth)
        f0 = midi_to_hz(midi)
        lfo_rate = knobs["knob_lfo_rate"]
        lfo_depth = knobs["knob_lfo_depth"] if ("socket_lfo_out", "socket_vco_pitch_cv") in cable_set else 0.03
        vib_cents = lfo_depth * 32.0 * np.sin(2.0 * math.pi * lfo_rate * lt) * (1.0 - np.exp(-lt / 0.12))
        f_inst = f0 * (2.0 ** (vib_cents / 1200.0))
        phase1 = 2.0 * math.pi * np.cumsum(f_inst) / SAMPLE_RATE

        # VCO 2 detune & sub-oscillator (if VCO 2 OUT -> VCF IN is patched)
        vco2_patched = ("socket_vco2_out", "socket_vcf_in") in cable_set
        detune_ct = knobs["knob_vco2_detune"]
        f2_inst = f_inst * (2.0 ** (detune_ct / 1200.0))
        phase2 = 2.0 * math.pi * np.cumsum(f2_inst) / SAMPLE_RATE
        phase_sub = 0.5 * phase2

        # Dynamic per-sample ladder filter cutoff + envelope modulation (ENV CV OUT -> VCF CUTOFF CV)
        env_cv_patched = ("socket_env_out", "socket_vcf_cutoff_cv") in cable_set
        base_cutoff_vec = np.interp(abs_t, grid_t, grid_cutoff)
        env_cents = knobs["knob_vcf_env_amt"] if env_cv_patched else 400.0
        inst_cutoff = np.clip(base_cutoff_vec * (2.0 ** ((env_cents * env) / 1200.0)), 60.0, 18000.0)
        res_q = knobs["knob_vcf_resonance"]
        wave_shape = knobs["knob_vco1_wave"]

        # Synthesize rich bandlimited VCO 1 + VCO 2 + Sub with 24 dB/oct 4-pole ladder response & resonance peak
        max_h = min(22, int(18000.0 / max(50.0, f0)))
        sig_L = np.zeros(n_len, dtype=np.float64)
        sig_R = np.zeros(n_len, dtype=np.float64)

        for h in range(1, max_h + 1):
            hf = f0 * h
            ratio = hf / inst_cutoff
            # 4-pole (24 dB/oct) Butterworth + resonant peak at ratio ~ 1.0
            lp_mag = 1.0 / np.sqrt(1.0 + (ratio ** 8))
            res_bump = 1.0 + (res_q / 6.0) * np.exp(-((ratio - 0.95) ** 2) / 0.08)
            h_gain = (1.0 / h) * lp_mag * res_bump

            # Morphing VCO 1 harmonic weights (Sawtooth + Square odd harmonics)
            w_saw = 1.0 - 0.45 * max(0.0, wave_shape - 0.67) * 3.0
            w_sq = (1.0 if h % 2 == 1 else 0.15) * max(0.0, (wave_shape - 0.5) * 2.0)
            amp1 = w_saw + 0.65 * w_sq

            osc1 = amp1 * np.sin(h * phase1)
            if vco2_patched:
                vco2_mix = knobs["knob_vco2_mix"]
                osc2 = vco2_mix * 0.85 * np.sin(h * phase2 + 0.35)
                sig_L += h_gain * (osc1 + osc2 * 0.92)
                sig_R += h_gain * (osc1 * 0.92 + osc2)
            else:
                sig_L += h_gain * osc1
                sig_R += h_gain * osc1

        # Add warm -1 octave square sub-oscillator (fundamental + 3rd harmonic) when VCO 2 is patched
        if vco2_patched and voice in ("lead", "bass"):
            sub_lvl = knobs["knob_vco2_mix"] * (0.48 if voice == "bass" else 0.28)
            sub_wave = np.sin(phase_sub) + 0.33 * np.sin(3.0 * phase_sub)
            sig_L += sub_lvl * sub_wave
            sig_R += sub_lvl * sub_wave

        # Apply Ladder Filter Drive saturation (tanh) and VCA ADSR envelope
        drive_vec = np.interp(abs_t, grid_t, grid_drive)
        voice_scale = 0.24 * vel * (1.15 if voice == "lead" else (0.95 if voice == "bass" else 0.72))
        pan_L = 1.04 if voice == "lead" else (0.96 if voice == "harmony" else 1.0)
        pan_R = 0.96 if voice == "lead" else (1.04 if voice == "harmony" else 1.0)

        norm_drive = 1.0 / np.tanh(np.maximum(0.5, drive_vec * 0.65))
        shaped_L = np.tanh(sig_L * drive_vec * 0.65) * norm_drive * env * voice_scale * pan_L
        shaped_R = np.tanh(sig_R * drive_vec * 0.65) * norm_drive * env * voice_scale * pan_R

        # If LFO CV OUT -> VCA GAIN CV is patched (Movement IV), apply subtle stereo VCA tremolo modulation
        if ("socket_lfo_out", "socket_vca_cv") in cable_set:
            vca_mod_L = 1.0 + 0.14 * knobs["knob_lfo_depth"] * np.sin(2.0 * math.pi * lfo_rate * abs_t)
            vca_mod_R = 1.0 - 0.14 * knobs["knob_lfo_depth"] * np.sin(2.0 * math.pi * lfo_rate * abs_t)
            shaped_L *= vca_mod_L
            shaped_R *= vca_mod_R

        synth_L[s_start:s_end] += shaped_L
        synth_R[s_start:s_end] += shaped_R

    # --------------------------------------------------------------------------
    # Synthesize Direct-Drive Vinyl Turntable Accompaniment (Active 61.6s - 120.0s)
    # Includes real-time 33 1/3 RPM (1.00x) <-> 45 RPM (1.35x) phase integration
    # and dynamic 24 dB/oct ladder filter sweep when PHONO OUT -> VCF IN is patched!
    # --------------------------------------------------------------------------
    tt_L = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
    tt_R = np.zeros(TOTAL_SAMPLES, dtype=np.float64)

    s_tt_start = int(61.6 * SAMPLE_RATE)
    n_tt = TOTAL_SAMPLES - s_tt_start
    t_abs = np.arange(s_tt_start, TOTAL_SAMPLES, dtype=np.float64) / SAMPLE_RATE

    # Instantaneous playback rate: 1.00x at 33 1/3 RPM, smoothly ramping to 1.35x at 45 RPM (74.0s - 84.0s)
    rate_vec = np.ones(n_tt, dtype=np.float64)
    in_45 = (t_abs >= 74.0) & (t_abs < 84.0)
    rate_vec[in_45] = 1.35
    # Smooth 80ms motor inertia ramp at 74.0s and 84.0s
    b_inert, a_inert = signal.butter(1, 8.0 / (0.5 * SAMPLE_RATE), btype="low")
    rate_smooth = signal.lfilter(b_inert, a_inert, rate_vec - 1.0) + 1.0
    # Cumulative vinyl groove time (position continuity preserved across speed changes!)
    vinyl_t = np.cumsum(rate_smooth) / SAMPLE_RATE

    mov3_mask = t_abs < 90.0
    mov4_mask = t_abs >= 90.0

    # Mov 3 vinyl groove (61.6s - 90.0s):
    # Follows Mozart K. 550 harmonic progression (Gm in Phrase 1 & Coda, D7 in Phrase 2,
    # and shifts up 1.35x to Cm / G7 when the turntable runs at 45 RPM during 74.0s - 84.0s!),
    # filtered through the live 24 dB/oct ladder filter cutoff (`PHONO OUT -> VCF AUDIO IN`).
    t3 = t_abs[mov3_mask]
    vt3 = vinyl_t[mov3_mask]
    cutoff3 = np.interp(t3, grid_t, grid_cutoff)
    pulse_8th = 0.5 + 0.5 * np.sin(2.0 * math.pi * 4.0 * vt3)

    # Smooth harmonic crossfade between G-minor (G2=98, D3=146.83, G3=196, Bb3=233.08, D4=293.66)
    # and D7/F#dim7 (D2=73.42, A2=110, D3=146.83, F#3=185.0, C4=261.63) during Phrase 2 (68.0 - 73.8s)
    d7_weight = np.where((t3 >= 68.0) & (t3 < 73.8), 1.0, 0.0)
    b_ch, a_ch = signal.butter(1, 3.0 / (0.5 * SAMPLE_RATE), btype="low")
    d7_w = np.clip(signal.lfilter(b_ch, a_ch, d7_weight), 0.0, 1.0)
    gm_w = 1.0 - d7_w

    gm_chord = np.zeros_like(vt3)
    for freq, amp in [(98.00, 0.36), (146.83, 0.28), (196.00, 0.24), (233.08, 0.20), (293.66, 0.15), (392.00, 0.10), (587.33, 0.07)]:
        lp = 1.0 / np.sqrt(1.0 + ((freq * rate_smooth[mov3_mask]) / cutoff3) ** 8)
        gm_chord += amp * lp * np.sin(2.0 * math.pi * freq * vt3)

    d7_chord = np.zeros_like(vt3)
    for freq, amp in [(73.42, 0.34), (110.00, 0.26), (146.83, 0.26), (185.00, 0.22), (261.63, 0.18), (369.99, 0.11), (523.25, 0.07)]:
        lp = 1.0 / np.sqrt(1.0 + ((freq * rate_smooth[mov3_mask]) / cutoff3) ** 8)
        d7_chord += amp * lp * np.sin(2.0 * math.pi * freq * vt3)

    gm_pad = (gm_w * gm_chord + d7_w * d7_chord) * (0.72 + 0.28 * pulse_8th)
    beat_phase = (vt3 * 4.0) % 1.0
    vinyl_kick = 0.24 * np.sin(2.0 * math.pi * (58.0 * vt3 + 1.8 * np.exp(-beat_phase / 0.08))) * np.exp(-beat_phase / 0.22)
    tt_L[s_tt_start:][mov3_mask] = 0.22 * (gm_pad * 1.05 + vinyl_kick)
    tt_R[s_tt_start:][mov3_mask] = 0.22 * (gm_pad * 0.95 + vinyl_kick)

    # Mov 4 vinyl groove (D major symphonic string/choir harmonic bed: D2=73.42, A2=110.0, D3=146.83, F#3=185.0, A3=220.0, D4=293.66)
    vt4 = vinyl_t[mov4_mask]
    lfo_trem_L = 0.82 + 0.18 * np.sin(2.0 * math.pi * 5.2 * t_abs[mov4_mask])
    lfo_trem_R = 0.82 - 0.18 * np.sin(2.0 * math.pi * 5.2 * t_abs[mov4_mask])
    dmaj_choir = (
        0.40 * np.sin(2.0 * math.pi * 73.42 * vt4)
        + 0.30 * np.sin(2.0 * math.pi * 110.00 * vt4)
        + 0.26 * np.sin(2.0 * math.pi * 146.83 * vt4)
        + 0.24 * np.sin(2.0 * math.pi * 185.00 * vt4)
        + 0.20 * np.sin(2.0 * math.pi * 220.00 * vt4)
        + 0.16 * np.sin(2.0 * math.pi * 293.66 * vt4)
    )
    tt_L[s_tt_start:][mov4_mask] = 0.24 * dmaj_choir * lfo_trem_L
    tt_R[s_tt_start:][mov4_mask] = 0.24 * dmaj_choir * lfo_trem_R

    # Subtle authentic 1974 vinyl surface warmth (-44 dB floor while stylus is on record)
    rng = np.random.default_rng(197404)
    vinyl_dust = 0.0025 * rng.standard_normal(n_tt)
    tt_L[s_tt_start:] += vinyl_dust
    tt_R[s_tt_start:] += vinyl_dust

    # Combine synth + turntable prior to BBD stereo delay
    dry_L = synth_L + tt_L
    dry_R = synth_R + tt_R

    # --------------------------------------------------------------------------
    # BBD Analogue Stereo Delay (Active when VCF OUT -> DELAY IN is patched: Mov II & Mov IV)
    # --------------------------------------------------------------------------
    wet_L = np.zeros(TOTAL_SAMPLES, dtype=np.float64)
    wet_R = np.zeros(TOTAL_SAMPLES, dtype=np.float64)

    dly_samples_L = int(0.24 * SAMPLE_RATE)  # 240 ms left tap
    dly_samples_R = int(0.255 * SAMPLE_RATE) # 255 ms right stereo spread tap

    # 3-tap BBD echo with 2.6 kHz warm bucket-brigade low-pass filter
    b_bbd, a_bbd = signal.butter(2, 2600.0 / (0.5 * SAMPLE_RATE), btype="low")
    filtered_src_L = signal.lfilter(b_bbd, a_bbd, dry_L)
    filtered_src_R = signal.lfilter(b_bbd, a_bbd, dry_R)

    for seg_t0, seg_t1 in [(32.6, 60.1), (91.1, 120.0)]:
        s0 = int(seg_t0 * SAMPLE_RATE)
        s1 = int(seg_t1 * SAMPLE_RATE)
        for tap, fb in [(1, 0.36), (2, 0.16), (3, 0.07)]:
            off_L = tap * dly_samples_L
            off_R = tap * dly_samples_R
            end_L = min(TOTAL_SAMPLES, s1 + off_L)
            end_R = min(TOTAL_SAMPLES, s1 + off_R)
            if s0 + off_L < end_L:
                wet_L[s0 + off_L : end_L] += fb * filtered_src_R[s0 : end_L - off_L]
            if s0 + off_R < end_R:
                wet_R[s0 + off_R : end_R] += fb * filtered_src_L[s0 : end_R - off_R]

    mix_L = dry_L + wet_L
    mix_R = dry_R + wet_R

    # Smooth 0.35s fade-in at 0.0s and 0.8s fade-out at 119.2-120.0s
    fade_in_n = int(0.20 * SAMPLE_RATE)
    mix_L[:fade_in_n] *= np.linspace(0.0, 1.0, fade_in_n)
    mix_R[:fade_in_n] *= np.linspace(0.0, 1.0, fade_in_n)
    fade_out_n = int(0.85 * SAMPLE_RATE)
    mix_L[-fade_out_n:] *= np.linspace(1.0, 0.0, fade_out_n)
    mix_R[-fade_out_n:] *= np.linspace(1.0, 0.0, fade_out_n)

    # Master console soft clipper & normalization to -1.1 dBFS peak (0.880, zero clipping)
    mix_L = np.tanh(mix_L * 1.25)
    mix_R = np.tanh(mix_R * 1.25)
    peak = max(float(np.max(np.abs(mix_L))), float(np.max(np.abs(mix_R))), 1e-6)
    scale = 0.880 / peak
    mix_L *= scale
    mix_R *= scale

    WAV_OUT.parent.mkdir(parents=True, exist_ok=True)
    pcm_L = np.clip(mix_L * 32767.0, -32767, 32767).astype(np.int16)
    pcm_R = np.clip(mix_R * 32767.0, -32767, 32767).astype(np.int16)
    interleaved = np.empty(TOTAL_SAMPLES * 2, dtype=np.int16)
    interleaved[0::2] = pcm_L
    interleaved[1::2] = pcm_R

    with wave.open(str(WAV_OUT), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(interleaved.tobytes())

    mono = 0.5 * (mix_L + mix_R)
    overall_rms = math.sqrt(float(np.mean(mono ** 2)))
    overall_peak = float(np.max(np.abs(mono)))
    print(f"Wrote {WAV_OUT} ({WAV_OUT.stat().st_size:,} bytes) | Peak={overall_peak:.4f} | RMS={overall_rms:.4f}")

    # Extract per-frame (7,200 frames @ 60fps = 800 samples/frame) waveform telemetry for the green phosphor oscilloscope!
    frames_wave = []
    samples_per_frame = SAMPLE_RATE // FPS  # 800
    win_len = 1600  # 33.3ms oscilloscope window
    for f in range(TOTAL_FRAMES):
        end_s = min(TOTAL_SAMPLES, (f + 1) * samples_per_frame)
        start_s = max(0, end_s - win_len)
        chunk = mono[start_s:end_s]
        if len(chunk) < 64:
            pts = [0.0] * 64
            f_peak = 0.0
            f_rms = 0.0
        else:
            idx = np.linspace(0, len(chunk) - 1, 64).astype(int)
            pts = [round(float(x), 3) for x in chunk[idx]]
            f_peak = round(float(np.max(np.abs(chunk))), 3)
            f_rms = round(math.sqrt(float(np.mean(chunk ** 2))), 3)
        frames_wave.append({"peak": f_peak, "rms": f_rms, "wave": pts})

    return frames_wave, {
        "sampleRateHz": SAMPLE_RATE,
        "durationSec": DURATION_S,
        "channels": 2,
        "totalSamplesPerChannel": TOTAL_SAMPLES,
        "peak": round(overall_peak, 4),
        "rms": round(overall_rms, 4),
    }


# ==============================================================================
# 5. EXPORT .SRT SUBTITLES & SOCIAL MEDIA POST COPY (.MD)
# ==============================================================================

def fmt_srt_time(sec: float) -> str:
    ms_total = int(round(sec * 1000.0))
    hrs = ms_total // 3600000
    rem = ms_total % 3600000
    mins = rem // 60000
    rem = rem % 60000
    secs = rem // 1000
    ms = rem % 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def write_srt_and_markdown(captions: list):
    srt_lines = []
    for cap in captions:
        srt_lines.append(str(cap["idx"]))
        srt_lines.append(f"{fmt_srt_time(cap['t0'])} --> {fmt_srt_time(cap['t1'])}")
        srt_lines.append(f"[{cap['movement']}] {cap['title']}")
        srt_lines.append(cap["subtitle"])
        srt_lines.append("")
    SRT_OUT.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"Wrote SRT subtitle file: {SRT_OUT} ({len(captions)} entries)")

    md_content = """# CHRONO ANALOGUE // SYSTEM 1974 — Four Symphonies on a 1974 Modular Synthesiser & Direct-Drive Turntable (1080p60 Showcase)

What happens when you patch Beethoven, Bach, Vivaldi, and Mozart through a 1974 American black walnut modular analogue synthesiser (with a 15° tilted anodised faceplate, 24 dB/oct ladder filter, and BBD stereo delay) alongside a spinning 180g direct-drive vinyl turntable?

Turn your studio monitors up. Every cable patch, filter sweep, 25-key manual passage, and 33⅓ ↔ 45 RPM vinyl transition in this 2-minute Full HD 60 fps performance is locked to the live signal path.

---

## Movement Timestamps & Live Patch Sheet

- **0:00 – 0:30 | Movement I: Beethoven — Symphony No. 5 in C Minor, Op. 67 (*Allegro con brio*)**
  - **Live Patching**: `VCO 1 OUT → VCF AUDIO IN` + `VCO 2 OUT → VCF AUDIO IN` + `ENV CV OUT → VCF CUTOFF CV`
  - **Performance**: Dual detuned sawtooth oscillators (`+14 ct`) + sub-octave square unison playing the iconic Fate motif (`G–G–G–Eb / F–F–F–D`), imitative *Allegro con brio* stretto, and Eb-major Horn Call while sweeping the 4-pole 24 dB/oct ladder filter from a dark `280 Hz` brassy growl to a searing `7,400 Hz` harmonic blaze (`3.8x` drive).

- **0:30 – 1:00 | Movement II: Bach — *Toccata & Fugue in D Minor, BWV 565* / Vivaldi — *Winter (Allegro non molto)***
  - **Live Cable Switching**: `LFO CV OUT → VCO PITCH CV` (baroque vibrato) & `VCF OUT → DELAY IN` (corridor-routed BBD stereo echo)
  - **Performance**: Reed/square organ & harpsichord registration (`VCO 1 WAVE = 0.88`), Bach's opening mordent and diminished-7th pedal arpeggio, rapid 16th-note bariolage counterpoint across `C3–C5`, and Vivaldi's *Winter* tremolando chords & blazing violin lightning runs with stereo Bucket-Brigade delay (`240 ms`, `48%` wet mix).

- **1:00 – 1:30 | Movement III: Mozart — Symphony No. 40 in G Minor, K. 550 (*Molto allegro*) + Live 180g Vinyl Turntable**
  - **Live Patch & Deck Cueing**: `PHONO OUT → VCF AUDIO IN` + lowering the S-shaped chrome tonearm onto the spinning 240-segment strobe platter (`33⅓ RPM`)
  - **Performance**: Snappy Classical spiccato ADSR plucks (`Attack 5 ms`, `Decay 180 ms`) playing Mozart's `Eb–D–D` G-minor subject over the spinning vinyl accompaniment, followed by a live on-camera **33⅓ RPM → 45 RPM (`1.35x` pitch & tempo)** speed switch for the Mannheim rocket modulational bridge before returning to `33⅓ RPM` for the cadence.

- **1:30 – 2:00 | Movement IV: Beethoven — Symphony No. 9 in D Minor / D Major, Op. 125 (*"Ode to Joy" Finale*)**
  - **Full-Rack Maximalist Patch (All 6 Braided Cables)**:
    1. `VCO 1 OUT → VCF AUDIO IN` (Burnt Orange)
    2. `VCO 2 OUT → VCF AUDIO IN` (Ochre Gold)
    3. `ENV CV OUT → VCF CUTOFF CV` (Teal Cyan)
    4. `VCF OUT → DELAY IN` (Crimson Red)
    5. `PHONO OUT → VCA AUDIO IN` (Sage Olive — symphonic vinyl choir/string bed)
    6. `LFO CV OUT → VCA GAIN CV` (Warm Cream — stereo tremolo modulation)
  - **Performance**: Noble low cello statement of the *Ode to Joy* hymn, two-voice contrapuntal variation with running 8th-note bass, and a triumphant *Prestissimo* full-studio finale sweeping the ladder filter open to `11,500 Hz` at `4.2x` drive.

---

## Technical Delivery Specs

- **Video Master**: `evidence/social_showcase_1974_symphonies_1080p60.mp4` (`1920x1080` Full HD, locked `60.0 fps`, `7,200` frames, `120.00s`, H.264 High Profile + AAC-LC 320 kbps)
- **Audio Master**: `evidence/social_showcase_1974_symphonies_48k.wav` (`48,000 Hz`, 16-bit PCM Stereo, `-1.1 dBFS` peak, zero clipping)
- **Subtitles**: `evidence/social_showcase_1974_symphonies.srt` (burned-in broadcast lower-third captions + companion SRT)

#ModularSynth #AnalogueSynthesis #1974Studio #Beethoven #Bach #Vivaldi #Mozart #SwitchedOnClassics #VinylTurntable #ThreeJS #WebAudio #SoundDesign #Synthesizer
"""
    MD_OUT.write_text(md_content, encoding="utf-8")
    print(f"Wrote social media post copy: {MD_OUT}")


def main():
    notes = build_symphony_notes()
    captions = build_captions()
    write_srt_and_markdown(captions)
    frames_wave, audio_stats = synthesize_showcase_audio_48k(notes)

    # Precompute compact per-frame state for all 7,200 frames so parallel Chrome workers can step at maximum speed
    frames_data = []
    for f in range(TOTAL_FRAMES):
        t = round(f / float(FPS), 4)
        cables, preview, status = get_cable_state_at(t)
        knobs, hl_knob = get_knobs_and_highlight_at(t)
        tt = get_turntable_state_at(t)
        cam = get_camera_at(t)

        # Active visual keys at time t
        pressed_keys = sorted(list({
            n["visual_midi"] for n in notes if n["t0"] <= t <= n["t1"]
        }))

        # Active caption at time t
        cap = captions[-1]
        for c in captions:
            if c["t0"] <= t < c["t1"]:
                cap = c
                break

        frames_data.append({
            "f": f,
            "t": t,
            "cables": cables,
            "preview": preview,
            "status": status,
            "knobs": knobs,
            "hlKnob": hl_knob,
            "tt": tt,
            "cam": cam,
            "keys": pressed_keys,
            "capIdx": cap["idx"] - 1,
            "wave": frames_wave[f],
        })

    timeline_payload = {
        "durationSec": DURATION_S,
        "fps": FPS,
        "totalFrames": TOTAL_FRAMES,
        "audioStats": audio_stats,
        "captions": captions,
        "frames": frames_data,
    }
    TIMELINE_JSON.write_text(json.dumps(timeline_payload), encoding="utf-8")
    print(f"Wrote master timeline JSON: {TIMELINE_JSON} ({TIMELINE_JSON.stat().st_size:,} bytes, {len(frames_data)} frames)")


if __name__ == "__main__":
    main()
