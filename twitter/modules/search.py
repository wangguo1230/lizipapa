# twitter/modules/search.py
import json
from typing import Dict, Any, List, Optional
from core.client import TwitterClient
from core.constants import GRAPHQL_ENDPOINTS, GQL_FEATURES, BASE_URL
from core.utils import gather_legacy_from_data

class SearchModule:
    """
    搜索模块
    负责执行关键词搜索。
    """
    def __init__(self, client: TwitterClient):
        self.client = client

    async def search(self, keywords: str, count: int = 20, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索推文。
        
        Args:
            keywords: 搜索关键词
            count: 获取数量
            cursor: 分页游标
        """
        endpoint = 'SearchTimeline'
        url = BASE_URL + GRAPHQL_ENDPOINTS[endpoint]
        
        variables = {
            "rawQuery": keywords,
            "count": count,
            "querySource": "typed_query",
            "product": "Latest" # 搜索最新推文
        }
        
        if cursor:
            variables["cursor"] = cursor
            
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(GQL_FEATURES[endpoint])
        }
        
        data = await self.client.request("GET", url, params=params)
        
        # 解析搜索结果指令
        instructions = data.get("data", {}).get("search_by_raw_query", {}).get("search_timeline", {}).get("timeline", {}).get("instructions", [])
        
        entries = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries.extend(instruction.get("entries", []))
            elif instruction.get("type") == "TimelineAddToModule":
                entries.extend(instruction.get("moduleItems", []))
        
        # 提取推文
        return gather_legacy_from_data(entries, filter_nested=['search_by_raw_query', 'search_timeline', 'timeline'])
