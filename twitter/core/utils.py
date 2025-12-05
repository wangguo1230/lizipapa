# twitter/core/utils.py
from typing import List, Dict, Any, Optional

def gather_legacy_from_data(entries: List[Dict[str, Any]], filter_nested: Optional[List[str]] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从嵌套的 GraphQL 响应数据中提取干净的推文数据。
    对应参考代码中的 gatherLegacyFromData 函数。
    
    Args:
        entries: GraphQL 响应中的 entries 列表
        filter_nested: 需要递归查找的嵌套条目 ID 前缀列表
        user_id: (可选) 仅保留该 User ID 的推文
        
    Returns:
        List[Dict[str, Any]]: 处理后的推文数据列表
    """
    tweets = []
    filtered_entries = []

    # 第一步：筛选出包含推文的 entries
    for entry in entries:
        entry_id = entry.get('entryId', '')
        if entry_id:
            # 普通推文条目
            if entry_id.startswith('tweet-'):
                filtered_entries.append(entry)
            # 个人主页网格中的推文
            elif entry_id.startswith('profile-grid-0-tweet-'):
                filtered_entries.append(entry)
            
            # 处理嵌套条目 (如会话线程、搜索结果)
            if filter_nested:
                for f in filter_nested:
                    if entry_id.startswith(f):
                        content = entry.get('content', {})
                        items = content.get('items', [])
                        filtered_entries.extend(items)

    # 第二步：解析每个条目，提取 legacy 数据
    for entry in filtered_entries:
        entry_id = entry.get('entryId', '')
        if entry_id:
            content = entry.get('content') or entry.get('item')
            if not content:
                continue
                
            # 尝试获取 tweetResult
            tweet_result = content.get('content', {}).get('tweetResult', {}).get('result') or \
                           content.get('itemContent', {}).get('tweet_results', {}).get('result')
            
            if tweet_result and 'tweet' in tweet_result:
                tweet_result = tweet_result['tweet']
            
            if tweet_result:
                # 处理转推 (Retweet)
                retweet = tweet_result.get('legacy', {}).get('retweeted_status_result', {}).get('result')
                
                targets = [tweet_result]
                if retweet:
                    targets.append(retweet)
                
                # 遍历推文和转推，注入用户信息
                for t in targets:
                    if 'legacy' not in t:
                        continue
                    
                    # 从 core.user_result 中提取用户信息并注入到 legacy.user
                    core_user = t.get('core', {}).get('user_result', {}).get('result') or \
                                t.get('core', {}).get('user_results', {}).get('result')
                    
                    if core_user and 'legacy' in core_user:
                        t['legacy']['user'] = core_user['legacy']
                        # 为了兼容性，将 core 中的 name/screen_name 确保写入
                        if 'core' in core_user:
                             pass

                    # 确保 id_str 存在
                    t['legacy']['id_str'] = t.get('rest_id')
                    
                    # 处理引用推文 (Quoted Status)
                    quoted = t.get('quoted_status_result', {}).get('result')
                    if quoted:
                        if 'tweet' in quoted:
                            quoted = quoted['tweet']
                        if 'legacy' in quoted:
                            t['legacy']['quoted_status'] = quoted['legacy']
                            quoted_user = quoted.get('core', {}).get('user_result', {}).get('result')
                            if quoted_user and 'legacy' in quoted_user:
                                t['legacy']['quoted_status']['user'] = quoted_user['legacy']

                # 最终提取 legacy 对象
                legacy = tweet_result.get('legacy')
                if legacy:
                    if retweet:
                        legacy['retweeted_status'] = retweet.get('legacy')
                    
                    # 如果指定了 user_id，进行过滤
                    if user_id is None or legacy.get('user_id_str') == str(user_id):
                        tweets.append(legacy)

    return tweets
