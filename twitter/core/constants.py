# twitter/core/constants.py

BASE_URL = 'https://x.com/i/api'

# GraphQL 端点和 Query ID 映射
# 这些 ID 可能会随 Twitter 更新而变化，需要定期维护
GRAPHQL_ENDPOINTS = {
    'UserTweets': '/graphql/E3opETHurmVJflFsUBVuUQ/UserTweets',
    'UserByScreenName': '/graphql/Yka-W8dz7RaEuQNkroPkYw/UserByScreenName',
    'HomeTimeline': '/graphql/HJFjzBgCs16TqxewQOeLNg/HomeTimeline',
    'HomeLatestTimeline': '/graphql/DiTkXJgLqBBxCs7zaYsbtA/HomeLatestTimeline',
    'UserTweetsAndReplies': '/graphql/bt4TKuFz4T7Ckk-VvQVSow/UserTweetsAndReplies',
    'UserMedia': '/graphql/dexO_2tohK86JDudXXG3Yw/UserMedia',
    'UserByRestId': '/graphql/Qw77dDjp9xCpUY-AXwt-yQ/UserByRestId',
    'SearchTimeline': '/graphql/UN1i3zUiCWa-6r-Uaho4fw/SearchTimeline',
    'ListLatestTweetsTimeline': '/graphql/Pa45JvqZuKcW1plybfgBlQ/ListLatestTweetsTimeline',
    'TweetDetail': '/graphql/QuBlQ6SxNAQCt6-kBiCXCQ/TweetDetail',
    'Likes': '/graphql/k5XapwcSikNsEsRLWkdFvA/Likes',
}

# 用户查询相关的功能开关 (Features)
GQL_FEATURE_USER = {
    "hidden_profile_subscriptions_enabled": True,
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "subscriptions_verification_info_is_identity_verified_enabled": True,
    "subscriptions_verification_info_verified_since_enabled": True,
    "highlights_tweets_tab_ui_enabled": True,
    "responsive_web_twitter_article_notes_tab_enabled": True,
    "subscriptions_feature_can_gift_premium": True,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
}

# 时间线/推文列表相关的功能开关
GQL_FEATURE_FEED = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}

# 推文详情页的功能开关
TWEET_DETAIL_FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}

# 功能开关映射表
GQL_FEATURES = {
    "UserByScreenName": GQL_FEATURE_USER,
    "UserByRestId": GQL_FEATURE_USER,
    "UserTweets": GQL_FEATURE_FEED,
    "UserTweetsAndReplies": GQL_FEATURE_FEED,
    "UserMedia": GQL_FEATURE_FEED,
    "SearchTimeline": GQL_FEATURE_FEED,
    "ListLatestTweetsTimeline": GQL_FEATURE_FEED,
    "HomeTimeline": GQL_FEATURE_FEED,
    "HomeLatestTimeline": TWEET_DETAIL_FEATURES,
    "TweetDetail": TWEET_DETAIL_FEATURES,
    "Likes": GQL_FEATURE_FEED,
}

# 固定 Bearer Token (Twitter Web App 通用)
BEARER_TOKEN = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
