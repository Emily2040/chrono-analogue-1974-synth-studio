import math
import struct
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
WAV_OUT = ROOT / "public" / "assets" / "audio" / "chrono_analogue_side_a_33rpm.wav"

def synthesize_1974_record(duration_s=16.0, sr=44100):
    """
    Synthesizes an original 1974 Kosmische / Analogue Studio LP recording at native 33 1/3 RPM:
    - Warm Rhodes-like electric piano progression (Dm9 -> G13 -> Cmaj9 -> A7alt)
    - Moog-style ladder-filtered octave bassline (112.5 BPM -> 8 bars in 16.0s)
    - Crisp vintage analogue drum machine pulse (kick, snare, closed/open hat)
    - Expressive analogue lead melody in upper register
    - Subtle vinyl surface warmth, head-amp saturation, and mastering to -1.5 dBFS peak (no clipping)
    """
    n_samples = int(duration_s * sr)
    t = np.linspace(0.0, duration_s, n_samples, endpoint=False)

    # 8 bars in 16 seconds -> 2.0 seconds per bar (120 BPM, 0.5s per beat, 0.125s per 16th note)
    beat_dur = 0.5
    sixteenth_dur = 0.125

    # 1. Chord progression (2 bars per chord: Dm9, G13, Cmaj9, A7b13)
    chords = [
        [146.83, 220.00, 261.63, 329.63, 392.00],  # Dm9 (D3, A3, C4, E4, G4)
        [196.00, 246.94, 293.66, 349.23, 440.00],  # G13 (G3, B3, D4, F4, A4)
        [130.81, 196.00, 246.94, 293.66, 329.63],  # Cmaj9 (C3, G3, B3, D4, E4)
        [110.00, 207.65, 246.94, 329.63, 349.23],  # A7b13 (A2, G#3/G3, B3,C#4, F4)
    ]
    chords[3] = [110.00, 196.00, 220.00, 277.18, 349.23]  # A7b13 (A2, G3, A3, C#4, F4)

    pad_L = np.zeros(n_samples, dtype=np.float64)
    pad_R = np.zeros(n_samples, dtype=np.float64)

    for c_idx, freqs in enumerate(chords):
        t_start = c_idx * 4.0
        t_end = (c_idx + 1) * 4.0
        mask = (t >= t_start) & (t < t_end)
        local_t = t[mask] - t_start
        env = (1.0 - np.exp(-local_t / 0.04)) * np.exp(-local_t / 3.2)
        # Tremolo / stereo pan for vintage electric piano
        trem_L = 0.75 + 0.25 * np.sin(2.0 * math.pi * 3.5 * local_t)
        trem_R = 0.75 - 0.25 * np.sin(2.0 * math.pi * 3.5 * local_t)
        voice = np.zeros_like(local_t)
        for v_i, f in enumerate(freqs):
            # Electric piano tine + fundamental
            fm_mod = 0.8 * np.exp(-local_t / 0.25) * np.sin(2.0 * math.pi * (f * 2.0) * local_t)
            voice += (0.22 / len(freqs)) * np.sin(2.0 * math.pi * f * local_t + fm_mod)
            voice += (0.06 / len(freqs)) * np.sin(2.0 * math.pi * (f * 3.0) * local_t) * np.exp(-local_t / 0.4)
        pad_L[mask] += voice * env * trem_L
        pad_R[mask] += voice * env * trem_R

    # 2. Moog-style octave bassline (16th-note groove)
    bass_roots = [73.42, 98.00, 65.41, 55.00]  # D2, G2, C2, A1
    bass_sig = np.zeros(n_samples, dtype=np.float64)
    total_sixteenths = int(duration_s / sixteenth_dur)
    for step in range(total_sixteenths):
        t0 = step * sixteenth_dur
        t1 = (step + 1) * sixteenth_dur
        mask = (t >= t0) & (t < t1)
        lt = t[mask] - t0
        chord_idx = (step // 32) % 4
        base_f = bass_roots[chord_idx]
        # Octave bounce pattern
        mult = 2.0 if (step % 2 == 1) else 1.0
        if step % 8 == 6:
            mult = 1.5  # Fifth passing note
        f = base_f * mult
        # Rich bandlimited sawtooth approx (first 10 harmonics with dynamic filter envelope)
        f_env = np.exp(-lt / 0.055)
        note_sig = np.zeros_like(lt)
        for h in range(1, 11):
            cutoff_atten = 1.0 / (1.0 + (h / (2.2 + 6.5 * f_env)) ** 2)
            note_sig += ((-1) ** (h + 1)) * (1.0 / h) * cutoff_atten * np.sin(2.0 * math.pi * (f * h) * lt)
        amp_env = (1.0 - np.exp(-lt / 0.004)) * np.exp(-lt / 0.095)
        bass_sig[mask] += 0.34 * note_sig * amp_env

    # 3. Expressive 1970s Analogue Lead Melody
    # Phrase over 16 seconds
    melody_events = [
        # (start_s, dur_s, freq_hz)
        (0.5, 0.75, 587.33), (1.25, 0.5, 523.25), (1.75, 0.75, 440.00), (2.5, 1.25, 392.00),
        (4.5, 0.75, 659.25), (5.25, 0.5, 587.33), (5.75, 0.75, 493.88), (6.5, 1.25, 440.00),
        (8.5, 0.75, 523.25), (9.25, 0.5, 493.88), (9.75, 0.75, 392.00), (10.5, 1.25, 329.63),
        (12.25, 0.5, 440.00), (12.75, 0.5, 523.25), (13.25, 0.75, 554.37), (14.0, 1.75, 440.00),
    ]
    lead_L = np.zeros(n_samples, dtype=np.float64)
    lead_R = np.zeros(n_samples, dtype=np.float64)
    for t0, dur, f in melody_events:
        mask = (t >= t0) & (t < t0 + dur)
        lt = t[mask] - t0
        vib = 1.0 + 0.0045 * np.sin(2.0 * math.pi * 5.8 * lt) * (1.0 - np.exp(-lt / 0.2))
        phase = 2.0 * math.pi * f * np.cumsum(vib) / sr
        sig = 0.6 * np.sin(phase) + 0.3 * np.sin(2.0 * phase) + 0.15 * np.sin(3.0 * phase)
        env = (1.0 - np.exp(-lt / 0.018)) * np.exp(-np.maximum(0.0, lt - dur * 0.65) / 0.12)
        lead_L[mask] += 0.20 * sig * env
        lead_R[mask] += 0.18 * sig * env

    # 4. Crisp Vintage Analogue Drum Groove
    drums_L = np.zeros(n_samples, dtype=np.float64)
    drums_R = np.zeros(n_samples, dtype=np.float64)
    rng = np.random.default_rng(1974)
    noise_full = rng.standard_normal(n_samples)

    for step in range(total_sixteenths):
        t0 = step * sixteenth_dur
        t1 = min(duration_s, t0 + 0.25)
        mask = (t >= t0) & (t < t1)
        lt = t[mask] - t0
        step_in_bar = step % 16

        # Kick on 0, 6, 8, 10
        if step_in_bar in (0, 6, 8, 10):
            k_freq = 52.0 + 95.0 * np.exp(-lt / 0.018)
            k_phase = 2.0 * math.pi * np.cumsum(k_freq) / sr
            kick = 0.32 * np.sin(k_phase) * np.exp(-lt / 0.11)
            drums_L[mask] += kick
            drums_R[mask] += kick

        # Snare on 4, 12
        if step_in_bar in (4, 12):
            s_tone = 0.14 * np.sin(2.0 * math.pi * 185.0 * lt) * np.exp(-lt / 0.045)
            s_noise = 0.16 * noise_full[mask] * np.exp(-lt / 0.085)
            drums_L[mask] += (s_tone + s_noise) * 1.05
            drums_R[mask] += (s_tone + s_noise) * 0.95

        # Hi-hat on every 8th/16th
        hat_decay = 0.09 if (step_in_bar in (2, 14)) else 0.022
        hat_amp = 0.065 if (step_in_bar % 2 == 0) else 0.035
        # High-frequency metallic shimmer + noise
        hat = hat_amp * (0.6 * noise_full[mask] + 0.4 * np.sin(2.0 * math.pi * 6400.0 * lt)) * np.exp(-lt / hat_decay)
        drums_L[mask] += hat * 0.85
        drums_R[mask] += hat * 1.15

    # 5. Subtle Vinyl Dust Warmth (gentle, realistic -42dB floor)
    vinyl_floor = 0.003 * noise_full

    mix_L = pad_L + bass_sig + lead_L + drums_L + vinyl_floor
    mix_R = pad_R + bass_sig + lead_R + drums_R + vinyl_floor

    # Soft analogue tape saturation & normalization to 0.84 peak (-1.5 dBFS, zero clipping)
    mix_L = np.tanh(mix_L * 1.15)
    mix_R = np.tanh(mix_R * 1.15)
    peak = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)), 1e-6)
    scale = 0.84 / peak
    mix_L *= scale
    mix_R *= scale

    WAV_OUT.parent.mkdir(parents=True, exist_ok=True)
    pcm_L = np.clip(mix_L * 32767.0, -32767, 32767).astype(np.int16)
    pcm_R = np.clip(mix_R * 32767.0, -32767, 32767).astype(np.int16)
    interleaved = np.empty(n_samples * 2, dtype=np.int16)
    interleaved[0::2] = pcm_L
    interleaved[1::2] = pcm_R

    with wave.open(str(WAV_OUT), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(interleaved.tobytes())

    rms = math.sqrt(float(np.mean(0.5 * (mix_L ** 2 + mix_R ** 2))))
    final_peak = float(max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R))))
    print(f"GENERATED RECORD AUDIO: {WAV_OUT} | duration={duration_s}s | sr={sr}Hz | peak={final_peak:.4f} | rms={rms:.4f}")

if __name__ == "__main__":
    synthesize_1974_record()
