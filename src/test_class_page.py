import asyncio
from playwright.async_api import async_playwright

async def test_class():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        url = "https://www.autodesk.com/autodesk-university/class/AECO-Roadmap-Digital-Workplaces-2025"
        print(f"Going to {url}")
        await page.goto(url)
        
        # Check title
        title = await page.title()
        print(f"Page Title: {title}")
        
        content = await page.content()
        if "Access Denied" in content:
            print("Access Denied detected")
        else:
            print("Page loaded successfully (content length: {})".format(len(content)))
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_class())
