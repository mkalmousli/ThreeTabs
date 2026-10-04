"""Sound engine for the ad videos: warm electric piano, extended jazz chords, soft bass, glassy bell arps.
Everything is synthesized (no samples). Effects are played in the same instruments, in the key of the current chord."""
import wave, numpy as np
from scipy.signal import butter, lfilter, fftconvolve
SR = 48000
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
T = lambda d: np.arange(int(d * SR)) / SR
def lp(x, f, o=2): b, a = butter(o, f, btype='low', fs=SR); return lfilter(b, a, x)
def hp(x, f, o=1): b, a = butter(o, f, btype='high', fs=SR); return lfilter(b, a, x)

VOICING = {'Cmaj9': [48, 55, 59, 62, 64], 'Am9': [45, 52, 55, 60, 71], 'Dm9': [50, 57, 60, 64, 65], 'G13': [43, 53, 59, 62, 64],
           'Fmaj7#11': [41, 52, 57, 60, 71], 'Em7': [40, 50, 55, 59, 62], 'Fmaj9': [41, 52, 57, 60, 67]}
TONES = {'Cmaj9': [60, 62, 64, 67, 71, 72, 74, 76], 'Am9': [57, 60, 64, 67, 71, 72, 74, 76], 'Dm9': [62, 64, 65, 69, 72, 74, 76, 77],
         'G13': [59, 62, 64, 65, 67, 71, 74, 76], 'Fmaj7#11': [60, 64, 65, 69, 71, 72, 76, 77], 'Em7': [59, 62, 64, 67, 71, 74, 76, 79],
         'Fmaj9': [60, 64, 65, 67, 69, 72, 76, 77]}
ROOT = {'Cmaj9': 36, 'Am9': 45, 'Dm9': 38, 'G13': 43, 'Fmaj7#11': 41, 'Em7': 40, 'Fmaj9': 41}
PROG = [(4, 'Cmaj9'), (6, 'Am9'), (8, 'Dm9'), (10, 'G13'), (12, 'Cmaj9'), (14, 'Fmaj7#11'), (16, 'Em7'), (18, 'Dm9'), (20, 'G13'),
        (21.5, 'Cmaj9'), (24, 'Fmaj9'), (26, 'Cmaj9'), (28, 'Cmaj9')]
SWING = 2 / 3   # swung eighth: the "and" lands two thirds of the way through the beat

def rhodes(f, dur, vel=1.0):
    t = T(dur); idx = (1.1 * vel) * np.exp(-t / .3) + .12
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t) * 2.0)
    tine = .10 * vel * np.sin(2 * np.pi * f * 7.07 * t) * np.exp(-t / .035)
    env = (1 - np.exp(-t / .006)) * np.exp(-t / (.7 + 1.3 * (220 / max(f, 110))))
    return (car + tine) * env * (1 + .05 * np.sin(2 * np.pi * 4.6 * t) * (t > .25))

class Mix:
    MG, FG = .35, 1.7   # music bus / effects bus gain: effects sit clearly on top of a quieter bed
    def __init__(s, dur):
        s.dur = dur; s.N = int(dur * SR) + SR * 4
        s.buses = {k: (np.zeros((2, s.N)), np.zeros((2, s.N))) for k in 'mf'}; s.t = 'm'   # 'm' = music, 'f' = effects
    def add(s, t0, sig, g=1., pan=0., send=.5):
        i = int(t0 * SR); sig = sig[:max(0, s.N - i)]; dry, wet = s.buses[s.t]
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        dry[0, i:i+len(sig)] += sig * g * l; dry[1, i:i+len(sig)] += sig * g * r
        wet[0, i:i+len(sig)] += sig * g * l * send; wet[1, i:i+len(sig)] += sig * g * r * send
    # ---- harmony helpers
    def chord_at(s, t): return [c for a, c in PROG if a <= t][-1] if t >= PROG[0][0] else 'Cmaj9'
    def pick(s, t, k): tn = TONES[s.chord_at(t)]; return tn[k % len(tn)] + 12 * (k // len(tn))
    # ---- voices
    def ep(s, t0, midi, g=.08, dur=2.6, vel=1., pan=0., send=.55):          # electric piano note
        s.add(t0, lp(rhodes(mtof(midi), dur, vel), 3200), g, pan, send)
    def strum(s, t0, midis, g=.07, dur=3.2, vel=.8, spread=.03, send=.6):   # rolled chord
        for k, m in enumerate(midis): s.ep(t0 + k * spread, m, g, dur, vel, pan=-.35 + .7 * k / max(1, len(midis) - 1), send=send)
    def bass(s, t0, midi, g=.1, dur=.9):
        t = T(dur); f = mtof(midi); sig = (np.sin(2 * np.pi * f * t) + .28 * np.sin(4 * np.pi * f * t)) * (1 - np.exp(-t / .012)) * np.exp(-t / .38)
        s.add(t0, lp(sig, 520), g, 0, .1)
    def blip(s, t0, midi, g=.04, pan=0.):                                   # soft marimba-like tick
        t = T(.5); f = mtof(midi); sig = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t / .02) + .3 * np.sin(2 * np.pi * f * 6 * t) * np.exp(-t / .008)) * (1 - np.exp(-t / .002)) * np.exp(-t / .12)
        s.add(t0, lp(sig, 3200), g * 1.4, pan, .2)
    def bell(s, t0, midi, g=.045, pan=0., echo=True):                       # glassy pluck with a soft ping-pong echo
        t = T(1.4); f = mtof(midi); sig = (np.sin(2 * np.pi * f * t + .6 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .12)) * np.exp(-t / .45)) * (1 - np.exp(-t / .004))
        sig = lp(sig, 2600)
        s.add(t0, sig, g * 1.2, pan, .35)
        if echo:
            for k in (1, 2, 3): s.add(t0 + .375 * k, sig, g * .38 ** k, -pan if k % 2 else pan, .5)
    def thump(s, t0, g=.1):
        t = T(1.2); f = 50 + 26 * np.exp(-t / .1); ph = 2 * np.pi * np.cumsum(f) / SR; s.add(t0, lp((np.sin(ph) + .6 * np.sin(2 * ph) * np.exp(-t / .15)) * (1 - np.exp(-t / .008)) * np.exp(-t / .4), 400, 3), g * 1.3, 0, .15)
    def swell(s, t0, dur, m0, m1, g=.04, pan=0.):                           # pitched pad glide, no noise
        t = T(dur); u = t / dur; f = mtof(m0) * (mtof(m1) / mtof(m0)) ** u; ph = 2 * np.pi * np.cumsum(f) / SR
        sig = (np.sin(ph) + .3 * np.sin(2 * ph) + .25 * np.sin(1.004 * ph)) * np.sin(np.pi * u) ** 2 * (1 + .08 * np.sin(2 * np.pi * 4.2 * t))
        s.add(t0, lp(sig, 1500, 3), g * 1.3, pan, .5)
    def fall(s, t0, g=.07):                                                  # gentle "not now": two soft falling notes
        s.ep(t0, 67, g * 1.3, 1.4, .9, send=.25); s.ep(t0 + .2, 60, g * 1.2, 1.8, .8, send=.25)
    def run(s, t0, t1, n, g=.045):                                           # rising bell run through the current scale
        for k in range(n): s.bell(t0 + (t1 - t0) * k / max(1, n - 1), s.pick(t0 + (t1 - t0) * k / max(1, n - 1), k // 2 + 2), g * (.6 + .4 * k / n), pan=-.3 + .6 * (k % 2), echo=k > n - 4)
    # ---- music bed
    def bed(s):
        s.t = 'm'; pad = np.zeros((2, s.N))
        for (a, c), (b, _) in zip(PROG, PROG[1:]):
            d = b - a + 2.0; t = T(d); env = np.minimum(t / 1.1, 1) * np.exp(-np.maximum(t - (b - a), 0) / .8)
            for m in VOICING[c][1:] + [VOICING[c][-1] + 12]:
                for det in (-.1, .1):
                    f = mtof(m + det); sg = sum(np.sin(2 * np.pi * f * k * t + k) / k ** 1.5 for k in range(1, 6)) * env * .012
                    i = int(a * SR); sg = sg[:s.N - i]; pad[0 if det < 0 else 1, i:i+len(sg)] += sg
        duck = np.ones(s.N)
        for a in np.arange(4, 27.5, 2.0):
            i = int(a * SR); L = int(.5 * SR); duck[i:i+L] *= 1 - .22 * np.exp(-np.arange(min(L, s.N - i)) / SR / .16)
        pad = lp(pad, 1500, 3) * duck; s.buses['m'][0][:] += pad; s.buses['m'][1][:] += pad * .4
        # intro: a slow rising Cmaj9 pedal before the title
        for m, g in zip([36, 48, 55, 59, 62], [.5, .5, .4, .3, .25]): s.swell(.3, 3.3, m - 5, m, .028 * g * 2)
        for (a, c), (b, _) in zip(PROG, PROG[1:]):
            v = VOICING[c]
            if a < 8.5:                                       # title: one soft, long chord per bar
                if a < 8.0: s.strum(a, v, .05, 3.6, .55, .04)
            elif a < 21.0 or (a == 20):                       # groove: swung comping + soft walking bass + bell arps
                for hit, vel in ((0, .8), (.5 + .5 * SWING, .6), (1.5, .45)):
                    tt = a + hit
                    if 8.5 <= tt < 21.0 and tt < b: s.strum(tt, v[1:], .055 * (.7 + vel * .4), 2.0 if hit == 0 else 1.1, vel, .022)
                for hit, m in ((0, ROOT[c]), (1.0, ROOT[c] + 7), (1.5, ROOT[c] + 2)):
                    tt = a + hit
                    if 8.5 <= tt < 21.0 and tt < b: s.bass(tt, m, .12 if hit == 0 else .08)
                if a >= 15.5 and a < 21.0:
                    seq = TONES[c]
                    for j, hit in enumerate((0, .5 * SWING + .0, .5, .5 + .5 * SWING, 1.0, 1.0 + .5 * SWING, 1.5, 1.5 + .5 * SWING)):
                        tt = a + hit
                        if tt < b and tt < 21.0: s.bell(tt, seq[[2, 4, 3, 5, 2, 6, 4, 5][j]] + (12 if j % 3 == 2 else 0), .028, pan=-.5 if j % 2 else .5, echo=False)
        for (a, c), (b, _) in zip(PROG, PROG[1:]):            # outro: slow chords with a floating top note
            if 21.5 <= a < 27.5:
                s.strum(a, VOICING[c], .05, 3.8, .6, .05); s.bell(a + .75, TONES[c][5], .04, pan=.3, echo=True)
        s.t = 'f'                                              # everything after the bed is an effect
    # ---- master (level is set afterwards from a measured loudness target)
    def render(s, path):
        rng = np.random.default_rng(5); t = T(3.0)
        ir = np.stack([rng.standard_normal(len(t)) * np.exp(-t / .9) for _ in range(2)]); ir = lp(ir, 4200, 3) * .08
        rev_m, rev_f = [np.stack([fftconvolve(s.buses[k][1][c], ir[c])[:s.N] for c in range(2)]) for k in 'mf']
        MG, FG = s.MG, s.FG
        m_rms = np.sqrt(np.mean(s.buses['m'][0][:, int(4 * SR):int(27 * SR)] ** 2)) * MG
        w = int(.4 * SR); f0 = s.buses['f'][0].mean(0) * FG; env = np.sqrt(np.convolve(f0 ** 2, np.ones(w) / w, 'same'))
        db = 20 * np.log10(np.maximum(env, 1e-9) / m_rms); act = db[db > -25]
        print('effects vs music RMS (dB): loudest %+.1f | median %+.1f | 20th pct %+.1f' % (db.max(), np.median(act), np.percentile(act, 20)))
        mix = lp(MG * (s.buses['m'][0] + rev_m) + FG * (s.buses['f'][0] + rev_f * .6), 5500, 2)
        end = int(s.dur * SR); fade = np.ones(s.N); fi = int(.8 * SR); fo = int(1.6 * SR)
        fade[:fi] = np.linspace(0, 1, fi); fade[end - fo:end] = np.linspace(1, 0, fo); fade[end:] = 0
        mix = hp(mix * fade, 35)[:, :end]; mix = mix / np.max(np.abs(mix)) * .5
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
