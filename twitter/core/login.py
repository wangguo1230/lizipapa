# twitter/core/login.py
import asyncio
import json
import os
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Page
from loguru import logger

async def login(username: str, password: str, email: Optional[str] = None, two_factor_secret: Optional[str] = None) -> List[Dict]:
    """
    Logs into Twitter using Playwright and returns the cookies.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless=False to see what's happening, can be changed later
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"Navigating to login page for {username}...")
            await page.goto("https://x.com/i/flow/login")
            
            # Enter Username
            logger.info("Entering username...")
            await page.wait_for_selector('input[autocomplete="username"]')
            await page.fill('input[autocomplete="username"]', username)
            await page.keyboard.press('Enter')

            # Check for unusual activity / email verification
            try:
                # Sometimes it asks for phone or email
                await page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
            except:
                logger.info("Password field not found immediately, checking for email verification...")
                # If password field didn't appear, it might be asking for email/phone
                if email:
                    input_selector = 'input[data-testid="ocfEnterTextTextInput"]'
                    if await page.is_visible(input_selector):
                        logger.info("Entering email for verification...")
                        await page.fill(input_selector, email)
                        await page.keyboard.press('Enter')
                        await page.wait_for_selector('input[autocomplete="current-password"]')
                else:
                    logger.warning("Email verification might be required but email not provided.")

            # Enter Password
            logger.info("Entering password...")
            await page.fill('input[autocomplete="current-password"]', password)
            await page.keyboard.press('Enter')

            # Check for 2FA
            try:
                await page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
                if two_factor_secret:
                    import pyotp
                    logger.info("Entering 2FA code...")
                    totp = pyotp.TOTP(two_factor_secret)
                    code = totp.now()
                    await page.fill('input[data-testid="ocfEnterTextTextInput"]', code)
                    await page.keyboard.press('Enter')
                else:
                    logger.warning("2FA might be required but secret not provided.")
            except:
                pass

            # Wait for login to complete (check for home timeline)
            logger.info("Waiting for home timeline...")
            await page.wait_for_url("https://x.com/home", timeout=30000)
            
            cookies = await context.cookies()
            logger.info("Login successful, cookies retrieved.")
            return cookies

        except Exception as e:
            logger.error(f"Login failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="login_error.png")
            raise e
        finally:
            await browser.close()

def save_cookies(cookies: List[Dict], filepath: str = "cookies.json"):
    with open(filepath, "w") as f:
        json.dump(cookies, f)

def load_cookies(filepath: str = "cookies.json") -> List[Dict]:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []
