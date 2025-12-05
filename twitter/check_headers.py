import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        ua = await page.evaluate("navigator.userAgent")
        ua_data = await page.evaluate("navigator.userAgentData ? navigator.userAgentData.brands : 'Not Supported'")
        
        print(f"Default User-Agent: {ua}")
        print(f"Default sec-ch-ua: {ua_data}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
