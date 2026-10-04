import os, sys, json, subprocess
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import TL
here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, 'out')
FPS = 60
def run(times=None, outfile=None):
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = b.new_page(viewport={'width':1920,'height':1080})
        pg.add_init_script('window.TL=' + json.dumps(TL))
        pg.goto(f'file://{here}/video.html'); pg.wait_for_timeout(800)
        if times:
            for t in times:
                pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(out, f'prev-{t}.png'))
        else:
            n = int(TL['dur'] * FPS)
            ff = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-i',os.path.join(out,'audio.wav'),
                '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-b:a','224k','-shortest','-movflags','+faststart',outfile], stdin=subprocess.PIPE)
            for i in range(n):
                pg.evaluate(f'render({i/FPS})')
                ff.stdin.write(pg.screenshot(type='jpeg', quality=95))
                if i % 120 == 0: print(i, n, flush=True)
            ff.stdin.close(); ff.wait()
        b.close()
if __name__ == '__main__':
    if sys.argv[1] == 'preview': run(times=[float(x) for x in sys.argv[2:]])
    else: run(outfile=sys.argv[1])
