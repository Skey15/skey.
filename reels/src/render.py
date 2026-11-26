"""Renderiza reel.html a MP4 1080x1920 30fps.
Uso: python3 render.py reel.html salida.mp4 [--stills 1.5,5,9,...]
"""
import os, subprocess, sys
from playwright.sync_api import sync_playwright

FPS = 30
html, out = os.path.abspath(sys.argv[1]), sys.argv[2]
stills = []
if "--stills" in sys.argv:
    stills = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + html)
    pg.wait_for_timeout(300)
    if stills:
        for t in stills:
            pg.evaluate(f"setT({t})")
            pg.screenshot(path=f"{out}_{t:05.2f}.jpg", type="jpeg", quality=85)
        sys.exit(0)
    scenes = pg.evaluate("S")
    parts = []
    for i, (a, z) in enumerate(scenes):
        tmp, final = f"{out}.s{i}.tmp.mp4", f"{out}.s{i}.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS),
                               "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                               "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        n = round((z - a) * FPS)
        for f in range(n):
            pg.evaluate(f"setT({a + f / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        ff.stdin.close()
        if ff.wait() != 0:
            sys.exit(f"ffmpeg falló en escena {i}")
        os.replace(tmp, final)
        parts.append(final)
    b.close()

lst = out + ".txt"
open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in parts))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart", out], check=True)
for x in parts + [lst]:
    os.remove(x)
print("ok", out)
