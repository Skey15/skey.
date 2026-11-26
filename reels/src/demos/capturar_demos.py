from playwright.sync_api import sync_playwright
TONE={"restaurante":"radial-gradient(circle at 60% 40%,#6b3a1f,#2a170c 60%,#120a06)",
      "peluqueria":"linear-gradient(160deg,#dfe7e0,#cdbfa9)",
      "tienda":"linear-gradient(160deg,#ead9c8,#c9a888)"}
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--lang=es-ES"])
    pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=3,locale="es-ES")
    for n,t in TONE.items():
        pg.goto("file:///home/claude/skey./demos/%s.html"%n,wait_until="networkidle")
        pg.add_style_tag(content="img{color:transparent!important;background:%s!important;object-fit:cover}"%t); pg.evaluate("document.querySelectorAll('img').forEach(i=>i.src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')")
        if n=="restaurante": pg.evaluate("document.querySelector('input[type=date]').value='2026-12-12'")
        pg.wait_for_timeout(500)
        offs=pg.evaluate("[...document.querySelectorAll('section[id],form[id],header')].map(e=>[e.id||e.tagName,Math.round(e.getBoundingClientRect().top+scrollY)])")
        print(n,offs)
        pg.screenshot(path="reel/%s.jpg"%n,full_page=True,type="jpeg",quality=92)
    b.close()
