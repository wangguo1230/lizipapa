import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Testing Stealth().apply_stealth_async(page)...")
        try:
            await Stealth().apply_stealth_async(page)
            print("Success: Stealth().apply_stealth_async(page)")
        except Exception as e:
            print(f"Failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
