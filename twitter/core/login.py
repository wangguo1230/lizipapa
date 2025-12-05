# twitter/core/login.py
import asyncio
import json
import os
import random
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth
from loguru import logger

async def human_type(page: Page, selector: str, text: str):
    """模拟人类打字行为，包含随机延迟"""
    # 模拟鼠标移动到元素
    box = await page.locator(selector).bounding_box()
    if box:
        await page.mouse.move(
            box['x'] + box['width'] / 2 + random.uniform(-10, 10),
            box['y'] + box['height'] / 2 + random.uniform(-5, 5),
            steps=10
        )
    
    await page.click(selector)
    
    # 随机打字延迟
    for char in text:
        await page.keyboard.type(char, delay=random.randint(50, 150))
        # 偶尔停顿更长时间
        if random.random() < 0.1:
            await asyncio.sleep(random.uniform(0.1, 0.5))

async def login(username: str, password: str, email: Optional[str] = None, two_factor_secret: Optional[str] = None, proxy: Optional[str] = None) -> List[Dict]:
    """
    使用 Playwright 模拟浏览器登录 Twitter 并获取 Cookie。
    """
    async with async_playwright() as p:
        # 启动浏览器
        launch_args = {
            "headless": False,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ]
        }
        if proxy:
            launch_args["proxy"] = {"server": proxy}
            
        browser = await p.chromium.launch(**launch_args)
        
        # 配置指纹参数
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.59 Safari/537.36"
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=[],
            geolocation=None,
            color_scheme="dark",
        )
        
        # 注入 stealth 脚本
        page = await context.new_page()
        
        # 使用 CDP 设置 User-Agent Metadata (解决 new_context 参数报错问题)
        try:
            cdp = await context.new_cdp_session(page)
            await cdp.send("Network.setUserAgentOverride", {
                "userAgent": user_agent,
                "userAgentMetadata": {
                    "brands": [
                        {"brand": "Chromium", "version": "142"},
                        {"brand": "Google Chrome", "version": "142"},
                        {"brand": "Not=A?Brand", "version": "99"}
                    ],
                    "fullVersion": "142.0.7444.59",
                    "platform": "Windows",
                    "platformVersion": "15.0.0",
                    "architecture": "x86",
                    "model": "",
                    "mobile": False
                }
            })
            logger.info("已通过 CDP 设置 User-Agent Metadata")
        except Exception as e:
            logger.warning(f"CDP 设置 User-Agent 失败: {e}")

        await Stealth().apply_stealth_async(page)
        
        # 注入额外的 WebGL 指纹模拟脚本 (模拟 GTX 1660 Ti)
        await page.add_init_script("""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Google Inc. (NVIDIA)';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11-31.0.15.3770)';
                }
                return getParameter.apply(this, arguments);
            };
        """)

        try:
            logger.info(f"正在前往登录页面: {username}...")
            await page.goto("https://x.com/i/flow/login")
            await asyncio.sleep(random.uniform(2, 4)) # 等待页面加载
            
            # 输入用户名
            logger.info("输入用户名...")
            # Debug: Screenshot before interaction
            await page.screenshot(path="debug_login_page.png")
            
            try:
                # 尝试多种选择器
                username_selector = 'input[autocomplete="username"]'
                fallback_selector = 'input[name="text"]'
                
                try:
                    await page.wait_for_selector(username_selector, timeout=5000)
                    await human_type(page, username_selector, username)
                    logger.info(f"已填充用户名 (使用选择器: {username_selector})")
                except:
                    logger.warning(f"首选选择器 {username_selector} 失败，尝试备用选择器...")
                    await page.wait_for_selector(fallback_selector, timeout=5000)
                    await human_type(page, fallback_selector, username)
                    logger.info(f"已填充用户名 (使用选择器: {fallback_selector})")
                    
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # 尝试点击 "下一步" 按钮
                try:
                    next_button_selector = 'div[role="button"]:has-text("Next"), div[role="button"]:has-text("下一步")'
                    await page.wait_for_selector(next_button_selector, timeout=5000)
                    await page.click(next_button_selector)
                    logger.info("已点击 '下一步' 按钮")
                except Exception as e:
                    logger.warning(f"未找到 '下一步' 按钮，尝试回车: {e}")
                    await page.keyboard.press('Enter')

            except Exception as e:
                logger.error(f"Failed to find or fill username input: {e}")
                await page.screenshot(path="debug_login_fail_username.png")
                # Dump HTML for debugging
                html_content = await page.content()
                with open("debug_login_fail.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                raise e

            # 检查是否需要额外的身份验证 (如输入邮箱或手机号)
            try:
                # 尝试等待密码框出现，超时时间设短一点
                await page.wait_for_selector('input[autocomplete="current-password"]', timeout=5000)
            except:
                logger.info("密码框未立即出现，检查是否需要邮箱验证...")
                # 如果密码框没出现，可能是触发了风控，要求输入邮箱
                if email:
                    input_selector = 'input[data-testid="ocfEnterTextTextInput"]'
                    if await page.is_visible(input_selector):
                        logger.info("输入邮箱进行验证...")
                        await human_type(page, input_selector, email)
                        await page.keyboard.press('Enter')
                        # 再次等待密码框
                        await page.wait_for_selector('input[autocomplete="current-password"]')
                else:
                    logger.warning("可能需要邮箱验证，但未提供邮箱配置。")

            # 输入密码
            logger.info("输入密码...")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await human_type(page, 'input[autocomplete="current-password"]', password)
            await page.keyboard.press('Enter')

            # 检查是否需要 2FA (双重验证)
            try:
                await page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
                if two_factor_secret:
                    import pyotp
                    logger.info("输入 2FA 验证码...")
                    totp = pyotp.TOTP(two_factor_secret)
                    code = totp.now()
                    await human_type(page, 'input[data-testid="ocfEnterTextTextInput"]', code)
                    await page.keyboard.press('Enter')
                else:
                    logger.warning("检测到 2FA 页面，但未提供 2FA 密钥。")
            except:
                pass # 没有 2FA，继续

            # 等待登录完成 (检测 URL 跳转到主页)
            logger.info("等待跳转至主页...")
            await page.wait_for_url("https://x.com/home", timeout=30000)
            
            # 获取所有 Cookie
            cookies = await context.cookies()
            logger.info("登录成功，已获取 Cookie。")
            return cookies

        except Exception as e:
            logger.error(f"自动登录失败: {e}")
            await page.screenshot(path="login_error.png")
            
            # Manual Login Fallback
            logger.warning("自动登录遇到问题。请在弹出的浏览器窗口中手动完成登录。")
            logger.warning("登录成功并进入主页后，请在控制台按回车键继续...")
            
            print(">>> 请在浏览器中手动登录，登录成功后在此处按回车键 <<<")
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            # Check if we are actually logged in by checking URL or Cookies
            try:
                cookies = await context.cookies()
                # Simple check: do we have auth_token?
                auth_token = next((c for c in cookies if c['name'] == 'auth_token'), None)
                if auth_token:
                    logger.info("检测到 auth_token，手动登录成功！")
                    return cookies
                else:
                    logger.warning("未检测到 auth_token，可能登录未完成。")
                    # Still return cookies, maybe they are enough or user wants to retry
                    return cookies
            except Exception as inner_e:
                logger.error(f"获取 Cookie 失败: {inner_e}")
                raise e
        finally:
            await browser.close()

def save_cookies(cookies: List[Dict], filepath: str = "cookies.json"):
    """保存 Cookie 到文件"""
    with open(filepath, "w") as f:
        json.dump(cookies, f)

def load_cookies(filepath: str = "cookies.json") -> List[Dict]:
    """从文件加载 Cookie"""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []
