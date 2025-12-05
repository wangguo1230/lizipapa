# twitter/main.py
import asyncio
import argparse
import json
import os
import time
from datetime import datetime
from loguru import logger
from core.client import TwitterClient
from modules.user import UserModule
from modules.tweet import TweetModule
from modules.search import SearchModule

DATA_DIR = "data"

def save_json(data, prefix, identifier):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DATA_DIR}/{prefix}_{identifier}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"Data saved to {filename}")

async def main():
    parser = argparse.ArgumentParser(description="Twitter Crawler (Python)")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # User command
    user_parser = subparsers.add_parser("user", help="Fetch user info and tweets")
    user_parser.add_argument("screen_name", help="Twitter screen name (e.g. elonmusk)")
    user_parser.add_argument("--count", type=int, default=20, help="Number of tweets to fetch")

    # Tweet command
    tweet_parser = subparsers.add_parser("tweet", help="Fetch tweet detail")
    tweet_parser.add_argument("tweet_id", help="Tweet ID")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search tweets")
    search_parser.add_argument("keyword", help="Search keyword")
    search_parser.add_argument("--count", type=int, default=20, help="Number of tweets to fetch")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    client = TwitterClient()
    
    try:
        await client.initialize()
        
        if args.command == "user":
            user_module = UserModule(client)
            logger.info(f"Fetching user info for {args.screen_name}...")
            user_info = await user_module.get_user_by_screen_name(args.screen_name)
            save_json(user_info, "user_info", args.screen_name)
            
            if user_info and 'rest_id' in user_info:
                user_id = user_info['rest_id']
                logger.info(f"Fetching tweets for user ID {user_id}...")
                tweets = await user_module.get_user_tweets(user_id, count=args.count)
                save_json(tweets, "user_tweets", args.screen_name)
            else:
                logger.error("User not found or restricted.")

        elif args.command == "tweet":
            tweet_module = TweetModule(client)
            logger.info(f"Fetching tweet {args.tweet_id}...")
            tweet_detail = await tweet_module.get_tweet_detail(args.tweet_id)
            save_json(tweet_detail, "tweet_detail", args.tweet_id)

        elif args.command == "search":
            search_module = SearchModule(client)
            logger.info(f"Searching for '{args.keyword}'...")
            tweets = await search_module.search(args.keyword, count=args.count)
            save_json(tweets, "search_results", args.keyword.replace(" ", "_"))

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
