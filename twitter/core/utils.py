# twitter/core/utils.py
from typing import List, Dict, Any, Optional

def gather_legacy_from_data(entries: List[Dict[str, Any]], filter_nested: Optional[List[str]] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Extracts tweet data from the nested GraphQL response, similar to gatherLegacyFromData in reference.
    """
    tweets = []
    filtered_entries = []

    for entry in entries:
        entry_id = entry.get('entryId', '')
        if entry_id:
            if entry_id.startswith('tweet-'):
                filtered_entries.append(entry)
            elif entry_id.startswith('profile-grid-0-tweet-'):
                filtered_entries.append(entry)
            
            if filter_nested:
                for f in filter_nested:
                    if entry_id.startswith(f):
                        # Handle nested items if present
                        content = entry.get('content', {})
                        items = content.get('items', [])
                        filtered_entries.extend(items)

    for entry in filtered_entries:
        entry_id = entry.get('entryId', '')
        if entry_id:
            content = entry.get('content') or entry.get('item')
            if not content:
                continue
                
            tweet_result = content.get('content', {}).get('tweetResult', {}).get('result') or \
                           content.get('itemContent', {}).get('tweet_results', {}).get('result')
            
            if tweet_result and 'tweet' in tweet_result:
                tweet_result = tweet_result['tweet']
            
            if tweet_result:
                # Handle Retweet
                retweet = tweet_result.get('legacy', {}).get('retweeted_status_result', {}).get('result')
                
                targets = [tweet_result]
                if retweet:
                    targets.append(retweet)
                
                for t in targets:
                    if 'legacy' not in t:
                        continue
                    
                    # Inject user info into legacy
                    core_user = t.get('core', {}).get('user_result', {}).get('result') or \
                                t.get('core', {}).get('user_results', {}).get('result')
                    
                    if core_user and 'legacy' in core_user:
                        t['legacy']['user'] = core_user['legacy']
                        # Add name and screen_name from core to maintain compatibility
                        if 'core' in core_user:
                             # Sometimes core user info is nested differently, simplified here
                             pass

                    t['legacy']['id_str'] = t.get('rest_id')
                    
                    # Handle Quoted Status
                    quoted = t.get('quoted_status_result', {}).get('result')
                    if quoted:
                        if 'tweet' in quoted:
                            quoted = quoted['tweet']
                        if 'legacy' in quoted:
                            t['legacy']['quoted_status'] = quoted['legacy']
                            quoted_user = quoted.get('core', {}).get('user_result', {}).get('result')
                            if quoted_user and 'legacy' in quoted_user:
                                t['legacy']['quoted_status']['user'] = quoted_user['legacy']

                legacy = tweet_result.get('legacy')
                if legacy:
                    if retweet:
                        legacy['retweeted_status'] = retweet.get('legacy')
                    
                    if user_id is None or legacy.get('user_id_str') == str(user_id):
                        tweets.append(legacy)

    return tweets
