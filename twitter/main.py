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
    """
    将数据保存为 JSON 文件。
    文件名格式: data/{prefix}_{identifier}_{timestamp}.json
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DATA_DIR}/{prefix}_{identifier}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"数据已保存至 {filename}")

async def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Twitter 爬虫 (Python 版)")
    subparsers = parser.add_subparsers(dest="command", help="要执行的命令")

    # User 命令: 获取用户信息和推文
    user_parser = subparsers.add_parser("user", help="获取用户信息及推文")
    user_parser.add_argument("screen_name", help="Twitter 用户名 (例如 elonmusk)")
    user_parser.add_argument("--count", type=int, default=20, help="获取推文数量")

    # Tweet 命令: 获取单条推文详情
    tweet_parser = subparsers.add_parser("tweet", help="获取推文详情")
    tweet_parser.add_argument("tweet_id", help="推文 ID")

    # Search 命令: 搜索推文
    search_parser = subparsers.add_parser("search", help="搜索推文")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument("--count", type=int, default=20, help="获取推文数量")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 初始化客户端
    client = TwitterClient()
    
    try:
        await client.initialize()
        
        if args.command == "user":
            user_module = UserModule(client)
            logger.info(f"正在获取用户 {args.screen_name} 的信息...")
            user_info = await user_module.get_user_by_screen_name(args.screen_name)
            save_json(user_info, "user_info", args.screen_name)
            
            if user_info and 'rest_id' in user_info:
                user_id = user_info['rest_id']
                logger.info(f"正在获取用户 ID {user_id} 的推文...")
                tweets = await user_module.get_user_tweets(user_id, count=args.count)
                save_json(tweets, "user_tweets", args.screen_name)
            else:
                logger.error("未找到用户或用户受限。")

        elif args.command == "tweet":
            tweet_module = TweetModule(client)
            logger.info(f"正在获取推文 {args.tweet_id}...")
            tweet_detail = await tweet_module.get_tweet_detail(args.tweet_id)
            save_json(tweet_detail, "tweet_detail", args.tweet_id)

        elif args.command == "search":
            search_module = SearchModule(client)
            logger.info(f"正在搜索 '{args.keyword}'...")
            tweets = await search_module.search(args.keyword, count=args.count)
            save_json(tweets, "search_results", args.keyword.replace(" ", "_"))

    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
