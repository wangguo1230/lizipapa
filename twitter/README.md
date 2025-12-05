# Twitter 爬虫 (Python 版)

这是一个基于 Python 的 Twitter (X) 数据抓取工具。它参考了 TypeScript 版本的逻辑，使用 `httpx` 进行高效的异步请求，并利用 `playwright` 模拟浏览器登录以获取稳定的 Cookie。

## ✨ 功能特性

- **自动登录**: 使用 Playwright 模拟真实浏览器登录，支持 2FA (双重验证)。
- **Cookie 复用**: 登录成功后自动保存 Cookie，后续请求直接复用，无需重复登录。
- **自动重试**: 遇到限流 (Rate Limit) 或 Token 过期时，自动等待或重新登录。
- **数据结构化**: 自动解析 GraphQL 复杂的嵌套响应，返回干净的 JSON 数据。
- **多功能支持**:
  - 获取用户信息
  - 获取用户推文列表
  - 获取单条推文详情
  - 关键词搜索

## 🛠️ 安装指南

### 1. 环境要求

- Python 3.8+

### 2. 安装依赖

在 `twitter` 目录下运行：

```bash
pip install -r requirements.txt
```

### 3. 安装浏览器内核

用于模拟登录：

```bash
playwright install chromium
```

## ⚙️ 配置说明

通过 `main.py` 脚本执行各种抓取任务。

### 1. 获取用户信息及推文

获取指定用户的资料及其最新推文。

```bash
# 格式: python main.py user [用户名] --count [数量]
python main.py user elonmusk --count 20
```

- 结果将保存至 `data/` 目录，文件名为 `user_info_...` 和 `user_tweets_...`。

### 2. 搜索推文

根据关键词搜索最新推文。

```bash
# 格式: python main.py search [关键词] --count [数量]
python main.py search "Python programming" --count 50
```

- 结果将保存至 `data/search_results_...`。

### 3. 获取推文详情

获取指定 ID 的推文详细内容（包含回复等上下文）。

```bash
# 格式: python main.py tweet [推文ID]
python main.py tweet 1864512345678901234
```

- 结果将保存至 `data/tweet_detail_...`。

## 📂 项目结构

- `core/`: 核心逻辑
  - `client.py`: HTTP 客户端，处理请求、Header 生成、自动重试。
  - `login.py`: 登录模块，使用 Playwright。
  - `utils.py`: 数据解析工具，提取 GraphQL 数据。
  - `constants.py`: API 端点和常量定义。
- `modules/`: 功能模块
  - `user.py`: 用户相关接口。
  - `tweet.py`: 推文详情接口。
  - `search.py`: 搜索接口。
- `data/`: 数据存储目录 (自动生成)。
- `cookies.json`: Cookie 存储文件 (自动生成)。
