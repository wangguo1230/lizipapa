# twitter/modules/tweet.py
import json
from typing import Dict, Any, List
from core.client import TwitterClient
from core.constants import GRAPHQL_ENDPOINTS, GQL_FEATURES, BASE_URL
from core.utils import gather_legacy_from_data

class TweetModule:
    """
    推文模块
    负责获取单条推文的详细信息。
    """
    def __init__(self, client: TwitterClient):
        self.client = client

    async def get_tweet_detail(self, tweet_id: str) -> List[Dict[str, Any]]:
        """
        获取推文详情。
        注意：返回的是一个列表，可能包含主推文及其回复/上下文。
        """
        endpoint = 'TweetDetail'
        url = BASE_URL + GRAPHQL_ENDPOINTS[endpoint]
        
        variables = {
            "focalTweetId": tweet_id,
            "with_rux_injections": False,
            "includePromotedContent": True,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withBirdwatchNotes": True,
            "withVoice": True,
            "withV2Timeline": True
        }
        
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(GQL_FEATURES[endpoint]),
            "fieldToggles": json.dumps({"withArticleRichContentState": False})
        }
        
        data = await self.client.request("GET", url, params=params)
        
        # 解析指令
        instructions = data.get("data", {}).get("threaded_conversation_with_injections_v2", {}).get("instructions", [])
        
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries.extend(instruction.get("entries", []))
        
        # 过滤掉不需要的嵌套会话，只提取相关推文
        return gather_legacy_from_data(entries, filter_nested=['homeConversation-', 'conversationthread-'])
