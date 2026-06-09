"""Dev-only: capture review screenshots of web/index.html with Playwright.
Desktop (1440) + true mobile (375, 2x). Element-level shots for readability."""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("/Users/tantra-artem/projects/hojoki")
URL = "file://" + str(ROOT / "web/index.html")
OUT = ROOT / "build/web-shots"
OUT.mkdir(exist_ok=True)

SECTIONS = {
    "cover": ".cover", "support": ".support", "toc": "#contents",
    "foreword": "#peredmova", "renunciation": "#zrechennia",
    "title": ".title-page", "figure": ".illus",
    "prolog": "#proloh", "pozhezha": "#pozhezha-v-epokhu-angen",
    "notes": "#notes",
}

def shoot(tag, vw, vh):
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(400)
        for name, sel in SECTIONS.items():
            try:
                pg.locator(sel).first.screenshot(path=str(OUT / f"{tag}-{name}.png"))
            except Exception as e:
                print("skip", tag, name, repr(e)[:80])
        # desktop marginalia: open note 1 and clip around it
        if tag == "D":
            ref = pg.locator(".fnref").first
            ref.click()
            pg.wait_for_timeout(250)
            box = pg.locator("#margin-box")
            rb = box.bounding_box(); fb = ref.bounding_box()
            if rb:
                top = min(fb["y"], rb["y"]) - 30
                bottom = max(fb["y"] + fb["height"], rb["y"] + rb["height"]) + 30
                pg.screenshot(path=str(OUT / "D-marginalia.png"),
                              clip={"x": 0, "y": top, "width": vw, "height": min(bottom - top, 1400)})
        b.close()
    print(tag, "done")

shoot("D", 1440, 1000)
shoot("M", 375, 800)
