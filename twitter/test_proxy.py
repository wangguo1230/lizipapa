import asyncio
import json
import os
from playwright.async_api import async_playwright
import httpx

async def test_httpx(proxy_url):
    print(f"Testing httpx with proxy: {proxy_url}", flush=True)
    try:
        async with httpx.AsyncClient(proxies=proxy_url, timeout=10.0) as client:
            resp = await client.get("https://x.com")
            print(f"httpx success: {resp.status_code}", flush=True)
            return True
    except Exception as e:
        print(f"httpx failed: {e}", flush=True)
        return False

async def test_playwright(proxy_url):
    print(f"Testing playwright with proxy: {proxy_url}")
    async with async_playwright() as p:
        try:
            # Use headless=False to match the app behavior
            browser = await p.chromium.launch(headless=False, proxy={"server": proxy_url})
            page = await browser.new_page()
            try:
                await page.goto("https://x.com/i/flow/login", timeout=60000)
                print("playwright success: Page loaded")
                
                # Debug: Screenshot
                await page.screenshot(path="test_login_page.png")
                
                print("Attempting to find username input...")
                await page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                print("Found username input")
                await page.fill('input[autocomplete="username"]', "test_user")
                print("Filled username")
                return True
            except Exception as e:
                print(f"playwright navigation/interaction failed: {e}")
                await page.screenshot(path="test_login_fail.png")
                return False
            finally:
                await browser.close()
        except Exception as e:
            print(f"playwright launch failed: {e}")
            return False

async def main():
    # Load current config
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
        current_proxy = config.get("proxy")
    else:
        current_proxy = "https://127.0.0.1:10808" # Default fallback
        
    print(f"Current configured proxy: {current_proxy}")
    
    # Test 1: Current Configuration
    print("\n--- Test 1: Current Configuration ---")
    await test_httpx(current_proxy)
    await test_playwright(current_proxy)
    
    # Test 2: HTTP Scheme (Force check)
    if "127.0.0.1" in current_proxy or "localhost" in current_proxy:
        # Extract port and assume http
        port = current_proxy.split(":")[-1]
        http_proxy = f"http://127.0.0.1:{port}"
        if http_proxy != current_proxy:
            print(f"\n--- Test 2: HTTP Scheme ({http_proxy}) ---")
            await test_httpx(http_proxy)
            await test_playwright(http_proxy)

if __name__ == "__main__":
    asyncio.run(main())
