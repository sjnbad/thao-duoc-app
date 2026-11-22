import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        await pg.goto("http://localhost:8765/index.html")
        await pg.wait_for_function("!document.getElementById('go').disabled")
        await pg.fill("#q","ho, sốt, gừng"); await pg.click("#go"); await pg.wait_for_timeout(900)
        await pg.evaluate("document.getElementById('libres').scrollIntoView()")
        await pg.screenshot(path="l1.png")
        await pg.click(".libtoggle >> nth=0"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="l2.png")
        await pg.click("#tabs button[data-t=lib]"); await pg.wait_for_timeout(500)
        await pg.screenshot(path="l3.png")
        await pg.fill("#lq","com chay"); await pg.wait_for_timeout(500)
        await pg.click(".titem >> nth=0"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="l4.png")
        n = await pg.evaluate("document.querySelectorAll('#liblist .lib').length")
        print("libcards", n, "errors:", errs)
        await b.close()
asyncio.run(main())
