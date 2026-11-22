import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        await pg.goto("http://localhost:8765/index.html")
        await pg.wait_for_function("!document.getElementById(\"go\").disabled"); await pg.screenshot(path="s0.png")
        for w in ["Ho","Sốt","Chảy mũi","Nghẹt mũi"]:
            await pg.click(f'#quick .chip[data-w="{w}"]')
        await pg.click("#go"); await pg.wait_for_timeout(600)
        await pg.screenshot(path="s1.png", full_page=False)
        await pg.evaluate("window.scrollTo(0, document.querySelector('#herbs').offsetTop-80)")
        await pg.screenshot(path="s2.png")
        await pg.click(".herb >> nth=0"); await pg.wait_for_timeout(500)
        await pg.click(".res .expand >> nth=0")
        await pg.evaluate("document.querySelector('#list').scrollIntoView()")
        await pg.screenshot(path="s3.png")
        await pg.click(".jump >> nth=0"); await pg.wait_for_timeout(600)
        await pg.screenshot(path="s4.png")
        print("errors:", errs)
        await b.close()
asyncio.run(main())
