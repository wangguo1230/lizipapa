# twitter/modules/user.py
import json
from typing import Dict, Any, List, Optional
from ..core.client import TwitterClient
from ..core.constants import GRAPHQL_ENDPOINTS, GQL_FEATURES, BASE_URL
from ..core.utils import gather_legacy_from_data

class UserModule:
    def __init__(self, client: TwitterClient):
        self.client = client

    async def get_user_by_screen_name(self, screen_name: str) -> Dict[str, Any]:
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
        
        # Extract user result
        user_result = data.get("data", {}).get("user", {}).get("result", {})
        return user_result

    async def get_user_tweets(self, user_id: str, count: int = 20, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
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
        
        # Parse instructions to get entries
        instructions = data.get("data", {}).get("user", {}).get("result", {}).get("timeline_v2", {}).get("timeline", {}).get("instructions", [])
        
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries.extend(instruction.get("entries", []))
            elif instruction.get("type") == "TimelineAddToModule":
                entries.extend(instruction.get("moduleItems", []))
                
        return gather_legacy_from_data(entries, user_id=user_id)

