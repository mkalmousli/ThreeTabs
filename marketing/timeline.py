"""Single source of truth for video timing (seconds). Used by audio synthesis and the renderer."""
import json
DUR = 28.0
N_TABS = 30
SPAWN = [round(0.4 + 2.8 * (i / (N_TABS - 1)) ** 1.15, 3) for i in range(N_TABS)]
STAMPS = [10.0, 11.5, 12.5]            # BLOCKED slams (on the beat)
PRESS = [round(s - 0.85, 3) for s in STAMPS]   # Ctrl+T presses
TL = dict(dur=DUR, spawn=SPAWN, cut=3.5, title=4.0, scene3=8.5, stamps=STAMPS, press=PRESS,
          feats=[15.5, 16.5, 17.5, 18.5], outro=21.5, arp=[6.0, 6.5, 7.0], pills=[23.0, 23.15, 23.3, 23.45], url=24.0)
if __name__ == '__main__':
    print(json.dumps(TL))
