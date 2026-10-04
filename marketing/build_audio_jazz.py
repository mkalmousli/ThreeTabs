import os
from jazz_core import Mix
from timeline import TL
m = Mix(TL['dur']); m.bed()
# 1) the pile-up: tiny rising blips climbing the scale, a slow swell, then a soft exhale at the cut
for i, s in enumerate(TL['spawn']): m.blip(s, 55 + 12 + (i // 2) % 9 * 1 + [0, 2, 4, 7, 9][i % 5], .03 + .0005 * i, pan=-.4 + .8 * (i % 5) / 4)
m.thump(TL['cut'], .1); m.swell(TL['cut'], 1.4, 76, 64, .035)
# 2) title: a lush Cmaj9 with a floating top note, then a three-note rise
m.strum(TL['title'], [60, 64, 67, 71, 74], .09, 3.6, .8, .05); m.bell(TL['title'] + .55, 79, .06, pan=.3)
for i, s in enumerate(TL['arp']): m.bell(s, [72, 76, 79][i] , .055, pan=-.3 + .3 * i)
m.swell(7.4, 1.1, 60, 72, .03)
# 3) blocking: keyboard tap, then a soft round thump and a gentle falling pair (never harsh)
for i, p in enumerate(TL['press']):
    m.blip(p, 67, .035); m.blip(p + .13, 62, .03)
    S = TL['stamps'][i]; m.thump(S, .1); m.fall(S + .02, .075)
# 4) features: bells climbing the current scale
for i, s in enumerate(TL['feats']): m.bell(s + .05, m.pick(s, 3 + i), .06, pan=-.3 + .2 * i); m.swell(s - .1, .5, 62 + 2 * i, 74 + 2 * i, .02)
m.swell(15.0, .9, 60, 72, .03); m.swell(20.6, .9, 72, 60, .028)
# 5) outro: a warm, wide Cmaj9, then tiny blips for the browsers and two bells for the URL
O = TL['outro']; m.thump(O, .1); m.strum(O, [48, 55, 60, 64, 67, 71, 74], .085, 4.0, .85, .06)
for i, s in enumerate(TL['pills']): m.blip(s, [67, 71, 72, 76][i], .04, pan=-.4 + .27 * i)
m.bell(TL['url'], 79, .06); m.bell(TL['url'] + .25, 83, .045, pan=.3)
m.render(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'audio_jazz_raw.wav'))
print('ok')
