# twitter/core/client.py
import httpx
import json
import os
from typing import Optional, Dict, Any
from loguru import logger
from .login import login, load_cookies, save_cookies
from .constants import BEARER_TOKEN

class TwitterClient:
    def __init__(self, config_path: str = "config.json", cookies_path: str = "cookies.json"):
        self.config_path = config_path
        self.cookies_path = cookies_path
        self.client: Optional[httpx.AsyncClient] = None
        self.cookies: List[Dict] = []
        self.headers: Dict[str, str] = {}
        
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    async def initialize(self):
        """
        Initializes the client, logging in if necessary.
        """
        self.cookies = load_cookies(self.cookies_path)
        
        if not self.cookies:
            logger.info("No cookies found, attempting login...")
            if not self.config.get("username") or not self.config.get("password"):
                raise ValueError("Username and password are required in config.json for login.")
            
            self.cookies = await login(
                username=self.config["username"],
                password=self.config["password"],
                email=self.config.get("email"),
                two_factor_secret=self.config.get("2fa_secret")
            )
            save_cookies(self.cookies, self.cookies_path)
        
        # Convert cookies list to dict for httpx
        cookie_dict = {c['name']: c['value'] for c in self.cookies}
        
        # Extract CSRF token
        csrf_token = cookie_dict.get("ct0")
        if not csrf_token:
            logger.warning("CSRF token (ct0) not found in cookies. Login might be invalid.")
        
        self.headers = {
            "authorization": BEARER_TOKEN,
            "x-csrf-token": csrf_token or "",
            "x-twitter-auth-type": "OAuth2Session" if csrf_token else "",
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": "en",
            "content-type": "application/json"
        }

        self.client = httpx.AsyncClient(
            cookies=cookie_dict,
            headers=self.headers,
            follow_redirects=True,
            timeout=30.0
        )
        logger.info("TwitterClient initialized.")

    async def request(self, method: str, url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.client:
            await self.initialize()
        
        try:
            response = await self.client.request(method, url, params=params, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 403 or e.response.status_code == 401:
                logger.warning("Token might be expired. Clearing cookies and retrying...")
                # Logic to clear cookies and re-login could go here
                # For now, just raise
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    async def close(self):
        if self.client:
            await self.client.aclose()
