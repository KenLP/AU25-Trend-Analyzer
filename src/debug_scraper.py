import asyncio
from playwright.async_api import async_playwright
import os

async def debug_search_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        logger_info = []
        
        # Enable console logging
        page.on("console", lambda msg: logger_info.append(f"CONSOLE: {msg.text}"))
        
        url = "https://www.autodesk.com/autodesk-university/search?fields.year=2025"
        print(f"Navigating to {url}")
        await page.goto(url, timeout=60000)
        
        # Wait a bit
        await asyncio.sleep(5)
        
        # Take screenshot
        os.makedirs("debug_output", exist_ok=True)
        await page.screenshot(path="debug_output/search_page.png", full_page=True)
        print("Saved screenshot to debug_output/search_page.png")
        
        # Save HTML
        content = await page.content()
        with open("debug_output/search_page.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved HTML to debug_output/search_page.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_search_page())
