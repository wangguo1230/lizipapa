# twitter/core/client.py
import httpx
import json
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
from .login import login, load_cookies, save_cookies
from .constants import BEARER_TOKEN

class TwitterClient:
    """
    Twitter API 客户端封装
    负责处理 HTTP 请求、自动登录、Cookie 管理以及请求头生成。
    """
    def __init__(self, config_path: str = "config.json", cookies_path: str = "cookies.json"):
        self.config_path = config_path
        self.cookies_path = cookies_path
        self.client: Optional[httpx.AsyncClient] = None
        self.cookies: List[Dict] = []
        self.headers: Dict[str, str] = {}
        
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    async def initialize(self):
        """
        初始化客户端。
        如果本地没有有效的 Cookie，会自动触发登录流程。
        """
        self.cookies = load_cookies(self.cookies_path)
        
        if not self.cookies:
            logger.info("未找到 Cookie，尝试登录...")
            if not self.config.get("username") or not self.config.get("password"):
                raise ValueError("config.json 中必须配置用户名和密码才能进行登录。")
            
            # 调用 Playwright 进行模拟登录
            self.cookies = await login(
                username=self.config["username"],
                password=self.config["password"],
                email=self.config.get("email"),
                two_factor_secret=self.config.get("2fa_secret"),
                proxy=self.config.get("proxy") # 传递代理配置
            )
            save_cookies(self.cookies, self.cookies_path)
        
        # 将 Cookie 列表转换为 httpx 需要的字典格式
        cookie_dict = {c['name']: c['value'] for c in self.cookies}
        
        # 从 Cookie 中提取 CSRF Token (ct0)
        # 这是通过 Twitter 验证的关键
        csrf_token = cookie_dict.get("ct0")
        if not csrf_token:
            logger.warning("Cookie 中未找到 CSRF token (ct0)。登录可能无效。")
        
        # 构造请求头
        # x-csrf-token 必须与 Cookie 中的 ct0 一致
        self.headers = {
            "authorization": BEARER_TOKEN,
            "x-csrf-token": csrf_token or "",
            "x-twitter-auth-type": "OAuth2Session" if csrf_token else "",
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": "en",
            "content-type": "application/json"
        }

        # 初始化异步 HTTP 客户端
        self.client = httpx.AsyncClient(
            cookies=cookie_dict,
            headers=self.headers,
            follow_redirects=True,
            timeout=30.0,
            proxy=self.config.get("proxy") # 添加代理配置
        )
        logger.info("TwitterClient 初始化完成。")

    async def request(self, method: str, url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, retry: int = 1) -> Dict[str, Any]:
        """
        发送 HTTP 请求，包含自动重试和重新登录逻辑。
        
        Args:
            method: HTTP 方法 (GET, POST)
            url: 请求 URL
            params: URL 参数
            json_data: JSON 请求体
            retry: 重试次数
        """
        if not self.client:
            await self.initialize()
        
        try:
            response = await self.client.request(method, url, params=params, json=json_data)
            
            # 检查限流响应头
            remaining = response.headers.get('x-rate-limit-remaining')
            reset = response.headers.get('x-rate-limit-reset')
            
            # 如果剩余请求次数不足 2 次，等待直到重置时间
            if remaining and int(remaining) < 2 and reset:
                reset_time = datetime.fromtimestamp(int(reset))
                delay = (reset_time - datetime.now()).total_seconds()
                if delay > 0:
                    logger.warning(f"触发限流保护。等待 {delay:.2f} 秒...")
                    await asyncio.sleep(delay + 1)
                    # 递归重试
                    return await self.request(method, url, params, json_data, retry)

            # 处理认证失败 (401/403)
            if response.status_code in (401, 403):
                if retry > 0:
                    logger.warning(f"认证失败 ({response.status_code})。正在清除 Cookie 并重新登录...")
                    # 删除旧的 Cookie 文件
                    if os.path.exists(self.cookies_path):
                        os.remove(self.cookies_path)
                    
                    # 关闭旧客户端并重新初始化 (这将触发重新登录)
                    await self.client.aclose()
                    self.client = None
                    await self.initialize()
                    
                    # 重试请求
                    return await self.request(method, url, params, json_data, retry - 1)
                else:
                    response.raise_for_status()

            response.raise_for_status()
            data = response.json()
            
            # 检查空的 User 对象 (Twitter 特有的软失效，通常意味着 Session 无效)
            if data.get("data") == {"user": {}}:
                 if retry > 0:
                    logger.warning("收到空的用户对象。Session 可能已失效。正在重新登录...")
                    if os.path.exists(self.cookies_path):
                        os.remove(self.cookies_path)
                    await self.client.aclose()
                    self.client = None
                    await self.initialize()
                    return await self.request(method, url, params, json_data, retry - 1)

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"请求失败: {e}")
            raise

    async def close(self):
        """关闭客户端连接"""
        if self.client:
            await self.client.aclose()
