import os
from calm_core import Mix, mtof, PENTA
from timeline import TL
m = Mix(TL['dur']); m.bed()
P = lambda i: mtof(PENTA[i % len(PENTA)])
# 1) chaos: tiny rising blips, a slow gentle swell, then a soft exhale
for i, s in enumerate(TL['spawn']): m.tick(s, P(i // 3) , .02 + .0004 * i, pan=-.4 + .8 * (i % 5) / 4)
m.swell(.4, 3.0, 180, 420, .05)
m.thump(TL['cut'], .12); m.swell(TL['cut'], 1.2, 520, 260, .05)
# 2) title
m.chord(TL['title'], [72, 76, 79, 83], .07); m.note(TL['title'] + .5, mtof(88), .05)
for i, s in enumerate(TL['arp']): m.note(s, mtof([72, 76, 79][i]), .08, 2.2)
m.swell(7.5, 1.0, 260, 520, .04)
# 3) blocking: a soft thump and a gentle falling pair (never harsh)
for i, p in enumerate(TL['press']):
    m.tick(p, 392, .04); m.tick(p + .13, 330, .03); m.note(p + .1, mtof(64), .035, .9)
    S = TL['stamps'][i]; m.thump(S, .13); m.note(S, mtof(67), .06, 1.2); m.note(S + .18, mtof(60), .05, 1.4)
# 4) features
for i, s in enumerate(TL['feats']): m.note(s + .05, P(i + 1), .08, 1.8, pan=-.3 + .2 * i); m.swell(s - .1, .45, 300 + 40 * i, 500 + 40 * i, .025)
m.swell(15.0, .8, 300, 600, .04); m.swell(20.7, .8, 600, 300, .035)
# 5) outro
O = TL['outro']; m.thump(O, .12); m.chord(O, [60, 64, 67, 72, 76, 79], .06, 3.0, .06)
for i, s in enumerate(TL['pills']): m.tick(s, P(i + 2), .035, pan=-.4 + .27 * i)
m.note(TL['url'], mtof(84), .06, 1.8); m.note(TL['url'] + .2, mtof(88), .045, 2.0)
m.render(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'audio_calm_raw.wav'))
print('ok')
