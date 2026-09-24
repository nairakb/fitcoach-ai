import numpy as np
import scipy.io.wavfile as wav
import os

sample_rate = 44100
duration = 38.0  # seconds
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# 1. Warm Lo-Fi Chord Progression (Cmaj7 -> Am7 -> Dm7 -> G7)
chords = [
    [261.63, 329.63, 392.00, 493.88],  # Cmaj7 (C4, E4, G4, B4)
    [220.00, 261.63, 329.63, 392.00],  # Am7   (A3, C4, E4, G4)
    [293.66, 349.23, 440.00, 523.25],  # Dm7   (D4, F4, A4, C5)
    [196.00, 246.94, 293.66, 349.23]   # G7    (G3, B3, D4, F4)
]

bpm = 85
beat_duration = 60.0 / bpm
bar_duration = beat_duration * 4

chord_signal = np.zeros_like(t)

for i in range(int(duration / bar_duration) + 1):
    bar_start = i * bar_duration
    chord = chords[i % len(chords)]
    for freq in chord:
        # Warm sine wave with subtle 2nd harmonic
        note_wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
        # Envelope per bar with soft attack and decay
        bar_mask = (t >= bar_start) & (t < bar_start + bar_duration)
        t_rel = t[bar_mask] - bar_start
        env = np.minimum(t_rel / 0.08, 1.0) * np.exp(-t_rel / (bar_duration * 0.85))
        chord_signal[bar_mask] += note_wave[bar_mask] * env * 0.15

# Low-pass filter effect for lo-fi warmth (moving average)
window_size = 12
chord_signal = np.convolve(chord_signal, np.ones(window_size)/window_size, mode='same')

# 2. Upbeat Lo-Fi Drum Pattern (Kick, Snare/Rim, Hi-Hat)
drum_signal = np.zeros_like(t)
total_beats = int(duration / (beat_duration / 2)) # 8th notes

for b in range(total_beats):
    beat_time = b * (beat_duration / 2)
    sample_idx = int(beat_time * sample_rate)
    
    # Kick on beat 1 and 3.5
    if (b % 8 == 0) or (b % 8 == 5):
        k_len = int(0.12 * sample_rate)
        if sample_idx + k_len < len(drum_signal):
            t_k = np.linspace(0, 0.12, k_len)
            freq_sweep = 120 * np.exp(-t_k * 35) + 45
            kick = np.sin(2 * np.pi * freq_sweep * t_k) * np.exp(-t_k * 20) * 0.45
            drum_signal[sample_idx:sample_idx+k_len] += kick

    # Snare/Rimshot on beat 2 and 4
    if b % 8 == 4:
        s_len = int(0.1 * sample_rate)
        if sample_idx + s_len < len(drum_signal):
            t_s = np.linspace(0, 0.1, s_len)
            noise = (np.random.rand(s_len) * 2 - 1) * np.exp(-t_s * 30) * 0.25
            pop = np.sin(2 * np.pi * 220 * t_s) * np.exp(-t_s * 40) * 0.2
            snare = noise + pop
            drum_signal[sample_idx:sample_idx+s_len] += snare

    # Hi-Hat on every 8th note
    h_len = int(0.04 * sample_rate)
    if sample_idx + h_len < len(drum_signal):
        t_h = np.linspace(0, 0.04, h_len)
        hat = (np.random.rand(h_len) * 2 - 1) * np.exp(-t_h * 70) * 0.08
        drum_signal[sample_idx:sample_idx+h_len] += hat

# 3. Subtle Vinyl Texture / Warm Crackle
vinyl = (np.random.rand(len(t)) * 2 - 1) * 0.015
# Occasional clicks
clicks = (np.random.rand(len(t)) > 0.9997).astype(float) * 0.04
vinyl += clicks

# Combine tracks
audio_mix = chord_signal + drum_signal + vinyl

# Normalize to avoid clipping
max_val = np.max(np.abs(audio_mix))
if max_val > 0:
    audio_mix = (audio_mix / max_val * 0.85 * 32767).astype(np.int16)

output_wav = "/tmp/lofi_background.wav"
wav.write(output_wav, sample_rate, audio_mix)
print(f"Generated upbeat lo-fi track at {output_wav}")
