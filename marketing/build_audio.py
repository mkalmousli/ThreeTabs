"""Synthesizes the ad's music + sound effects from timeline.py (no samples, no copyright)."""
import os, numpy as np, wave
from scipy.signal import butter, lfilter, fftconvolve
from timeline import TL
SR = 48000; N = int(TL['dur'] * SR) + SR
rng = np.random.default_rng(7)
dry = np.zeros((2, N)); wet = np.zeros((2, N))
T = lambda d: np.arange(int(d * SR)) / SR
SFX = 0.4   # calm: overall effects level
def add(bus, t, sig, g=1.0, pan=0.0, send=0.0):
    g = g * SFX if bus is dry else g
    i = int(t * SR); sig = sig[:max(0, N - i)]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[0, i:i+len(sig)] += sig * g * l * 1.414; bus[1, i:i+len(sig)] += sig * g * r * 1.414
    if send: wet[0, i:i+len(sig)] += sig * g * send * l; wet[1, i:i+len(sig)] += sig * g * send * r
def bp(x, lo, hi, o=2): b, a = butter(o, [lo, hi], btype='band', fs=SR); return lfilter(b, a, x)
def lp(x, f, o=2): b, a = butter(o, f, btype='low', fs=SR); return lfilter(b, a, x)
def hp(x, f, o=2): b, a = butter(o, f, btype='high', fs=SR); return lfilter(b, a, x)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def sweep_noise(dur, f0, f1, K=14):
    t = T(dur); out = np.zeros_like(t); w = rng.standard_normal(len(t))
    for k in range(K):
        fc = f0 * (f1 / f0) ** (k / (K - 1)); c = dur * k / (K - 1)
        band = bp(w, max(40, fc * .7), min(SR / 2 - 100, fc * 1.4)); out += band * np.exp(-((t - c) / (dur / 5)) ** 2)
    return out / np.max(np.abs(out) + 1e-9)
def whoosh(t0, dur, up=True, g=.5):
    s = sweep_noise(dur, 250, 7000) if up else sweep_noise(dur, 7000, 250)[:]
    s = lp(s, 2500) * np.sin(np.pi * np.linspace(0, 1, len(s))) ** 2; add(dry, t0, s, g * .6, send=.4)
def pop(t0, f, g=.5, pan=0):
    t = T(.2); ff = f * (1 + .7 * np.exp(-t / .018)); s = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / .045) * (1 - np.exp(-t / .002))
    add(dry, t0, s, g, pan, send=.12)
def boom(t0, g=.9, dur=1.2):
    t = T(dur); f = 38 + 90 * np.exp(-t / .1); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .5)
    n = lp(rng.standard_normal(len(t)), 220) * np.exp(-t / .25) * 1.5
    add(dry, t0, s + n * .5, g, send=.25)
def crack(t0, g=.5): t = T(.25); add(dry, t0, bp(rng.standard_normal(len(t)), 800, 2500) * np.exp(-t / .06), g * .3, send=.3)
def ping(t0, f, g=.2, dec=.5, send=.5):
    t = T(2.5); s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dec / r ** .5)) for r, a in [(1, 1), (2.76, .5), (5.4, .25), (8.93, .12)])
    add(dry, t0, s * (1 - np.exp(-t / .002)), g, send=send)
def pluck(t0, f, g=.25, dec=.3, pan=0, send=.4):
    t = T(1.2); s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t / (dec / k ** .5)) for k in range(1, 7))
    add(dry, t0, s * (1 - np.exp(-t / .003)), g, pan, send=send)
def click(t0, g=.4):
    t = T(.1); add(dry, t0, lp(hp(rng.standard_normal(len(t)), 1500), 3500) * np.exp(-t / .01) * .4 + np.sin(2 * np.pi * 170 * t) * np.exp(-t / .04), g * .6, send=.15)
def buzz(t0, g=.35):
    t = T(.4); f = 105 - 25 * t / .4; sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)); am = .6 + .4 * np.sign(np.sin(2 * np.pi * 38 * t))
    add(dry, t0, lp(sq * am, 450) * np.sin(np.pi * np.clip(t / .4, 0, 1)) ** .5 * np.exp(-t / .3), g, send=.1)
def kick(t0, g=.7): t = T(.35); f = 48 + 120 * np.exp(-t / .03); add(dry, t0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .13), g)
def hat(t0, g=.12): t = T(.08); add(dry, t0, hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / .02), g, pan=.3)
def snare(t0, g=.3): t = T(.3); add(dry, t0, bp(rng.standard_normal(len(t)), 1200, 5000) * np.exp(-t / .09) + np.sin(2 * np.pi * 190 * t) * np.exp(-t / .05) * .6, g, send=.2)
def riser(t0, t1, g=.55):
    d = t1 - t0; t = T(d); u = t / d
    n = sweep_noise(d, 200, 9000) * u ** 2.2
    f = 180 + 1800 * u ** 2; tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (.6 + .4 * np.sin(2 * np.pi * np.cumsum(6 + 30 * u) / SR)) * u ** 2.5
    add(dry, t0, lp(n, 3000) * .7 + tone * .12, g * .6, send=.3)
# ---- music
CH = {'Am': [57, 60, 64], 'F': [53, 57, 60], 'C': [48, 52, 55], 'G': [55, 59, 62]}
ROOT = {'Am': 33, 'F': 29, 'C': 36, 'G': 31}
PROG = [(4, 'Am'), (6, 'F'), (8, 'C'), (10, 'G'), (12, 'Am'), (14, 'F'), (16, 'C'), (18, 'G'), (20, 'F'), (21.5, 'C'), (24, 'F'), (26, 'C'), (28, 'C')]
kicks = [x * .5 for x in range(int(8.5 / .5), int(21.0 / .5))]
pad = np.zeros((2, N))
for (s, c), (e, _) in zip(PROG, PROG[1:]):
    d = e - s + 1.0; t = T(d)
    env = np.minimum(t / .8, 1) * np.exp(-np.maximum(t - (e - s), 0) / .5)
    for m in CH[c] + [CH[c][0] + 12]:
        for det in (-.07, 0, .07):
            f = mtof(m + det); w = sum(np.sin(2 * np.pi * f * k * t + k) / k ** 1.4 for k in range(1, 5))
            i = int(s * SR); sg = w * env * .05
            pad[0, i:i+len(sg)] += sg[:N - i] * (1 if det < 0 else .7); pad[1, i:i+len(sg)] += sg[:N - i] * (1 if det > 0 else .7)
sc = np.ones(N)
for k in []:
    i = int(k * SR); L = int(.35 * SR); sc[i:i+L] *= 1 - .55 * np.exp(-np.arange(min(L, N - i)) / SR / .09)
padmix = lp(pad, 1800)
dry += padmix * 1.3; wet += padmix * .5
# intro drone
t = T(3.5); dr = (np.sin(2 * np.pi * 55 * t) + .5 * np.sin(2 * np.pi * 82.5 * t)) * (t / 3.5) ** 1.5 * .12; add(dry, 0, dr, 1, send=.2)
# bass
for (s, c), (e, _) in zip(PROG, PROG[1:]):
    for q in np.arange(max(s, 8.5), min(e, 21.0), .5):
        i = int(round((q % 2) / .25))
        if i in (0, 4):
            m = ROOT[c] + (12 if i == 6 else 0); t = T(.28); s_ = np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t / .16) + .3 * np.sin(4 * np.pi * mtof(m) * t) * np.exp(-t / .08)
            add(dry, q, lp(s_, 400), .22 * (sc[int(q * SR)] if int(q * SR) < N else 1) ** .5)
# arpeggio
for (s, c), (e, _) in zip(PROG, PROG[1:]):
    if s < 15.5 or s >= 21.0: continue
    notes = [m + 24 for m in CH[c]] + [CH[c][1] + 36]
    for j, q in enumerate(np.arange(s, min(e, 21.0), .25)): pluck(q, mtof(notes[[0, 1, 2, 3, 2, 1, 3, 2][j % 8]]), .05, .35, pan=(-.4 if j % 2 else .4), send=.5)
# outro arp (calm)
for q in np.arange(21.5, 27.0, .5):
    c = [x for x in PROG if x[0] <= q][-1][1]; pluck(q, mtof(CH[c][int(q * 2) % 3] + 24), .07, .5, pan=np.sin(q), send=.6)
# ---- SFX on the timeline
for i, s in enumerate(TL['spawn']): pop(s, 260 * 2 ** (i / 9) * (1 + .05 * (i % 3)), .09 + .002 * i, pan=rng.uniform(-.5, .5))
riser(.4, 3.42, .6)
boom(TL['cut'], .5); whoosh(TL['cut'] + .02, .9, False, .5)
for k, f in enumerate([523.25, 659.25, 783.99, 1174.66]): ping(TL['title'] + k * .02, f, .16)
whoosh(TL['title'] - .05, .7, True, .3); ping(TL['title'] + .5, 1046.5, .1)
for i, s in enumerate(TL['arp']): pluck(s, [523.25, 659.25, 783.99][i], .3, .5, send=.6); ping(s, [1046.5, 1318.5, 1568][i], .06)
whoosh(8.2, .5, True, .45); riser(7.4, 8.45, .25)
for i, p in enumerate(TL['press']):
    click(p, .45); click(p + .13, .3); pop(p + .08, 330 - 30 * i, .3)
    buzz(p + .45, .16); S = TL['stamps'][i]
    boom(S, .45, .9); crack(S, .5); ping(S, 880, .1, .5, .5); whoosh(S + .25, .3, False, .22)
for i, s in enumerate(TL['feats']): pluck(s + .05, [1046.5, 1174.66, 1318.5, 1567.98][i], .22, .6, send=.7); whoosh(s - .05, .35, True, .22); ping(s + .08, [523.25, 587.33, 659.25, 783.99][i], .08)
whoosh(15.0, .6, True, .35); whoosh(20.95, .6, False, .3)
riser(20.4, 21.48, .4)
O = TL['outro']; boom(O, .5, 1.8)
for k, f in enumerate([261.63, 329.63, 392, 523.25, 587.33, 783.99, 1046.5]): ping(O + k * .03, f, .13, 1.2, .8)
whoosh(O + .02, 1.2, True, .3)
for i, s in enumerate(TL['pills']): pop(s, 600 + 120 * i, .22, pan=-.4 + .27 * i)
pluck(TL['url'], 1318.5, .25, .6); pluck(TL['url'] + .12, 1760, .22, .8)
# ---- master
ir_t = T(2.2); ir = np.stack([rng.standard_normal(len(ir_t)) * np.exp(-ir_t / .55) for _ in range(2)]); ir = lp(ir, 5500) * .12
rev = np.stack([fftconvolve(wet[c], ir[c])[:N] for c in range(2)])
mix = dry + rev * 1.0
mix = mix / np.max(np.abs(mix)) * 1.1; mix = np.tanh(mix) / np.tanh(1.1)
fade = np.ones(N); fi = int(.25 * SR); fade[:fi] = np.linspace(0, 1, fi)
end = int(TL['dur'] * SR); fo = int(1.2 * SR); fade[end - fo:end] = np.linspace(1, 0, fo); fade[end:] = 0
mix = hp(mix * fade, 25, 1)
mix = mix[:, :end]; mix *= .89 / np.max(np.abs(mix))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'audio.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', out, mix.shape[1] / SR, 's')
