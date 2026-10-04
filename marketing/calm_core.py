"""Calm sound engine: warm pad, soft bell notes, gentle swells. No noise bursts, no drums, no clicks."""
import os, wave, numpy as np
from scipy.signal import butter, lfilter, fftconvolve
SR = 48000
PROG = [(4, 'Am'), (6, 'F'), (8, 'C'), (10, 'G'), (12, 'Am'), (14, 'F'), (16, 'C'), (18, 'G'), (20, 'F'), (21.5, 'C'), (24, 'F'), (26, 'C'), (28, 'C')]
CH = {'Am': [57, 60, 64], 'F': [53, 57, 60], 'C': [48, 52, 55], 'G': [55, 59, 62]}
PENTA = [72, 74, 76, 79, 81, 84]          # C major pentatonic, bell register
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, f, o=2): b, a = butter(o, f, btype='low', fs=SR); return lfilter(b, a, x)
def hp(x, f, o=1): b, a = butter(o, f, btype='high', fs=SR); return lfilter(b, a, x)
T = lambda d: np.arange(int(d * SR)) / SR

class Mix:
    def __init__(s, dur):
        s.dur = dur; s.N = int(dur * SR) + SR * 4
        s.dry = np.zeros((2, s.N)); s.wet = np.zeros((2, s.N))
    def add(s, t0, sig, g=1., pan=0., send=.5):
        i = int(t0 * SR); sig = sig[:max(0, s.N - i)]
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        s.dry[0, i:i+len(sig)] += sig * g * l; s.dry[1, i:i+len(sig)] += sig * g * r
        s.wet[0, i:i+len(sig)] += sig * g * l * send; s.wet[1, i:i+len(sig)] += sig * g * r * send
    # --- voices
    def note(s, t0, f, g=.08, dec=1.8, pan=0., send=.7):          # soft bell
        t = T(dec * 3.5); env = (1 - np.exp(-t / .03)) * np.exp(-t / dec)
        sig = (np.sin(2 * np.pi * f * t) + .22 * np.sin(4 * np.pi * f * t) * np.exp(-t / .6) + .08 * np.sin(6 * np.pi * f * t) * np.exp(-t / .3)) * env
        s.add(t0, lp(sig, 3500), g, pan, send)
    def tick(s, t0, f=880, g=.035, pan=0.):                        # tiny soft blip (no noise)
        t = T(.35); sig = np.sin(2 * np.pi * f * t) * (1 - np.exp(-t / .006)) * np.exp(-t / .07)
        s.add(t0, lp(sig, 2500), g, pan, .5)
    def thump(s, t0, g=.12):                                        # round, quiet low impact
        t = T(1.2); f = 52 + 28 * np.exp(-t / .12)
        sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / .02)) * np.exp(-t / .45)
        s.add(t0, lp(sig, 300), g, 0, .3)
    def swell(s, t0, dur, f0=220, f1=440, g=.05, pan=0.):          # slow airy tone glide
        t = T(dur); u = t / dur; f = f0 * (f1 / f0) ** u; ph = 2 * np.pi * np.cumsum(f) / SR
        sig = (np.sin(ph) + .35 * np.sin(2 * ph) + .2 * np.sin(1.003 * ph)) * np.sin(np.pi * u) ** 2
        s.add(t0, lp(sig, 1800), g, pan, .8)
    def chord(s, t0, midis, g=.06, dec=2.4, spread=.045):
        for k, m in enumerate(midis): s.note(t0 + k * spread, mtof(m), g, dec, pan=-.4 + .8 * k / max(1, len(midis) - 1))
    # --- music bed
    def bed(s, melody=(8.5, 21.0)):
        pad = np.zeros((2, s.N))
        for (a, c), (b, _) in zip(PROG, PROG[1:]):
            d = b - a + 2.4; t = T(d); env = np.minimum(t / 1.4, 1) * np.exp(-np.maximum(t - (b - a), 0) / .9)
            for m in CH[c] + [CH[c][0] + 12]:
                for det in (-.08, 0, .08):
                    f = mtof(m + det); sg = (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t + 1) + .1 * np.sin(6 * np.pi * f * t)) * env * (1 + .06 * np.sin(2 * np.pi * .17 * t + m))
                    i = int(a * SR); sg = sg[:s.N - i] * .03
                    pad[0, i:i+len(sg)] += sg * (1 if det <= 0 else .7); pad[1, i:i+len(sg)] += sg * (1 if det >= 0 else .7)
        pad = lp(pad, 1500)
        s.dry += pad; s.wet += pad * .5
        # sparse bell melody: two soft notes per chord
        for (a, c), (b, _) in zip(PROG, PROG[1:]):
            if a < melody[0] or a >= melody[1]: continue
            r = CH[c]; s.note(a + .05, mtof(r[2] + 24), .05, 2.4, pan=-.3, send=.9); s.note(a + 1.0, mtof(r[1] + 24), .04, 2.4, pan=.3, send=.9)
        for (a, c), (b, _) in zip(PROG, PROG[1:]):
            if a < 21.5 or a >= 27: continue
            r = CH[c]; s.note(a + .5, mtof(r[2] + 24), .04, 2.6, pan=.2, send=.9)
    # --- master
    def render(s, path):
        rng = np.random.default_rng(3); t = T(3.2)
        ir = np.stack([rng.standard_normal(len(t)) * np.exp(-t / .95) for _ in range(2)]); ir = lp(ir, 4500) * .09
        rev = np.stack([fftconvolve(s.wet[c], ir[c])[:s.N] for c in range(2)])
        mix = s.dry + rev * 1.1
        mix = lp(mix, 7000, 1)
        end = int(s.dur * SR); fade = np.ones(s.N); fi = int(.8 * SR); fo = int(1.6 * SR)
        fade[:fi] = np.linspace(0, 1, fi); fade[end - fo:end] = np.linspace(1, 0, fo); fade[end:] = 0
        mix = hp(mix * fade, 30)[:, :end]; mix = np.tanh(mix / np.max(np.abs(mix)) * .9)
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767 * .89).astype('<i2').tobytes())
