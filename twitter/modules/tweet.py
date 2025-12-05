# twitter/modules/tweet.py
import json
from typing import Dict, Any, List
from ..core.client import TwitterClient
from ..core.constants import GRAPHQL_ENDPOINTS, GQL_FEATURES, BASE_URL
from ..core.utils import gather_legacy_from_data

class TweetModule:
    def __init__(self, client: TwitterClient):
        self.client = client

    async def get_tweet_detail(self, tweet_id: str) -> List[Dict[str, Any]]:
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
        
        # Parse instructions
        instructions = data.get("data", {}).get("threaded_conversation_with_injections_v2", {}).get("instructions", [])
        
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries.extend(instruction.get("entries", []))
                
        return gather_legacy_from_data(entries, filter_nested=['homeConversation-', 'conversationthread-'])
