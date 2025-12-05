import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            # Minimal metadata to test argument acceptance
            context = await browser.new_context(user_agent_metadata={
                "brands": [], 
                "fullVersion": "100", 
                "platform": "Windows", 
                "platformVersion": "10", 
                "architecture": "x86", 
                "model": "", 
                "mobile": False
            })
            print("Success: user_agent_metadata supported")
        except TypeError as e:
            print(f"Failed: {e}")
        except Exception as e:
            print(f"Error: {e}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
