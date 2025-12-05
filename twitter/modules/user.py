# twitter/modules/user.py
import json
from typing import Dict, Any, List, Optional
from core.client import TwitterClient
from core.constants import GRAPHQL_ENDPOINTS, GQL_FEATURES, BASE_URL
from core.utils import gather_legacy_from_data

class UserModule:
    """
    用户模块
    负责获取用户信息、用户推文列表等。
    """
    def __init__(self, client: TwitterClient):
        self.client = client

    async def get_user_by_screen_name(self, screen_name: str) -> Dict[str, Any]:
        """
        根据 Screen Name (如 elonmusk) 获取用户信息。
        """
        endpoint = 'UserByScreenName'
        url = BASE_URL + GRAPHQL_ENDPOINTS[endpoint]
        
        variables = {
            "screen_name": screen_name,
            "withSafetyModeUserFields": True
        }
        
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(GQL_FEATURES[endpoint]),
            "fieldToggles": json.dumps({"withAuxiliaryUserLabels": False})
        }
        
        data = await self.client.request("GET", url, params=params)
        
        # 提取用户结果对象
        user_result = data.get("data", {}).get("user", {}).get("result", {})
        return user_result

    async def get_user_tweets(self, user_id: str, count: int = 20, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取用户的推文列表。
        
        Args:
            user_id: 用户的 Rest ID (数字 ID)
            count: 获取数量
            cursor: 分页游标 (用于翻页)
        """
        endpoint = 'UserTweets'
        url = BASE_URL + GRAPHQL_ENDPOINTS[endpoint]
        
        variables = {
            "userId": user_id,
            "count": count,
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True
        }
        
        if cursor:
            variables["cursor"] = cursor
            
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(GQL_FEATURES[endpoint])
        }
        
        data = await self.client.request("GET", url, params=params)
        
        # 解析 Timeline 指令，提取 entries
        instructions = data.get("data", {}).get("user", {}).get("result", {}).get("timeline_v2", {}).get("timeline", {}).get("instructions", [])
        
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries.extend(instruction.get("entries", []))
            elif instruction.get("type") == "TimelineAddToModule":
                entries.extend(instruction.get("moduleItems", []))
                
        # 使用工具函数解析并返回干净的推文数据
        return gather_legacy_from_data(entries, user_id=user_id)
