# Boniu Crawler

一个基于Python的高性能爬虫项目，支持多种爬取方式和数据存储格式。

## 🚀 功能特性

- **多种爬取方式**: 支持Requests、Selenium、Scrapy、Playwright等
- **高性能异步爬取**: 基于asyncio的异步并发爬取
- **灵活数据存储**: 支持JSON、CSV、Excel、TXT等多种存储格式
- **可配置性强**: 支持代理、请求头、延迟等配置
- **详细日志记录**: 使用Loguru进行日志管理
- **反爬虫策略**: 内置多种反爬虫绕过策略
- **代码质量**: 使用Black、Flake8、MyPy等工具保证代码质量

## 📦 技术栈

- **Python**: 3.8+
- **Requests**: HTTP客户端
- **BeautifulSoup4**: HTML解析
- **Selenium**: 浏览器自动化
- **Scrapy**: 爬虫框架
- **Playwright**: 现代浏览器自动化
- **Pandas**: 数据处理
- **Loguru**: 日志管理
- **Pydantic**: 数据验证
- **aiohttp**: 异步HTTP客户端

## 🏗️ 项目结构

```
boniu-crawler/
├── main.py                 # 主程序入口
├── config.py               # 配置管理
├── logger.py               # 日志管理
├── utils.py                # 工具函数
├── crawler.py              # 基础爬虫类
├── requests_crawler.py     # Requests爬虫
├── requirements.txt        # 依赖文件
├── pyproject.toml          # 项目配置
├── .env.example            # 环境变量示例
├── data/                   # 数据存储目录
├── logs/                   # 日志文件目录
├── tests/                  # 测试文件
└── README.md
```

## 🚀 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑配置文件
# 根据需要修改 .env 文件中的配置
```

### 运行示例

```bash
# 爬取新闻网站
python main.py news

# 爬取API数据
python main.py api

# 批量爬取
python main.py batch

# 分页爬取
python main.py paginated

# 异步爬取
python main.py async

# 运行所有示例
python main.py all
```

## 📖 使用示例

### 基础爬虫使用

```python
from requests_crawler import RequestsCrawler

# 创建爬虫实例
crawler = RequestsCrawler("my_crawler")

# 爬取单个URL
result = crawler.crawl_url("https://example.com")
print(result.data)

# 爬取HTML页面
selectors = {
    "title": "h1",
    "content": ".content",
    "links": "a",
}
result = crawler.crawl_html("https://example.com", selectors)
print(result.data)

# 爬取API数据
result = crawler.crawl_api("https://api.example.com/data")
print(result.data)
```

### 批量爬取

```python
urls = [
    "https://api.example.com/data1",
    "https://api.example.com/data2",
    "https://api.example.com/data3",
]

crawler = RequestsCrawler()
results = crawler.batch_crawl(urls)

for result in results:
    if not result.error:
        print(f"成功: {result.url}")
    else:
        print(f"失败: {result.url} - {result.error}")
```

### 分页爬取

```python
crawler = RequestsCrawler()

page_config = {
    "start_page": 1,
    "max_pages": 10,
    "page_param": "page",
    "data_selector": ".item",
}

data = crawler.crawl_paginated("https://example.com/list", page_config)
print(f"获取到 {len(data)} 页数据")
```

### 异步爬取

```python
import asyncio
from requests_crawler import AsyncRequestsCrawler

async def main():
    crawler = AsyncRequestsCrawler()
    
    urls = [
        "https://api.example.com/data1",
        "https://api.example.com/data2",
    ]
    
    results = await crawler.batch_crawl(urls)
    
    for result in results:
        if not result.error:
            print(f"成功: {result.url}")

# 运行异步爬虫
asyncio.run(main())
```

### 自定义爬虫

```python
from crawler import BaseCrawler
from requests_crawler import RequestsCrawler

class MyCrawler(RequestsCrawler):
    def __init__(self):
        super().__init__("my_crawler")
    
    def run(self):
        """实现具体的爬取逻辑"""
        url = "https://example.com"
        result = self.crawl_url(url)
        
        if not result.error:
            # 处理数据
            processed_data = self.process_data(result.data)
            # 保存数据
            self.save_data(processed_data, "my_data.json")
    
    def process_data(self, data):
        """处理爬取到的数据"""
        # 在这里添加数据处理逻辑
        return data

# 运行自定义爬虫
crawler = MyCrawler()
crawler.start()
```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下参数：

```bash
# 应用配置
APP_NAME=Boniu Crawler
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=false

# 爬虫配置
CRAWLER__TIMEOUT=30
CRAWLER__RETRIES=3
CRAWLER__RETRY_DELAY=1
CRAWLER__MAX_CONCURRENT=5

# 代理配置
PROXY__ENABLED=false
PROXY__HOST=127.0.0.1
PROXY__PORT=8080
PROXY__USERNAME=
PROXY__PASSWORD=

# 日志配置
LOGGING__LEVEL=INFO
LOGGING__FILE=./logs/crawler.log
LOGGING__ROTATION=1 day
LOGGING__RETENTION=30 days

# 存储配置
STORAGE__OUTPUT_DIR=./data
STORAGE__FORMAT=json
STORAGE__FILENAME=crawled_data

# 反爬虫配置
ANTI_CRAWLER__ENABLED=true
ANTI_CRAWLER__RANDOM_DELAY=true
ANTI_CRAWLER__DELAY_RANGE=1,3
ANTI_CRAWLER__ROTATE_USER_AGENTS=true
```

### 基础配置

- `timeout`: 请求超时时间（秒）
- `retries`: 重试次数
- `retry_delay`: 重试延迟时间（秒）
- `max_concurrent`: 最大并发数

### 反爬虫配置

- `random_delay`: 是否启用随机延迟
- `delay_range`: 延迟时间范围（秒）
- `rotate_user_agents`: 是否轮换User-Agent
- `use_proxy_pool`: 是否使用代理池

## 📊 数据存储

支持多种数据存储格式：

- **JSON**: 适合结构化数据
- **CSV**: 适合表格数据
- **Excel**: 适合复杂表格数据
- **TXT**: 适合纯文本数据

## 📝 日志管理

使用Loguru进行日志管理，支持：

- 控制台输出
- 文件记录
- 错误追踪
- 性能监控
- 日志轮转

## 🧪 测试

项目包含完整的单元测试和集成测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_crawler.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 🔧 开发工具

### 代码格式化

```bash
# 格式化代码
black .

# 排序导入
isort .

# 类型检查
mypy .
```

### 代码检查

```bash
# 代码风格检查
flake8 .

# 运行测试
pytest
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 注意事项

- 请遵守网站的 robots.txt 规则
- 合理设置爬取频率，避免对目标网站造成压力
- 注意数据使用的法律合规性
- 建议使用代理池避免IP被封
- 遵守目标网站的使用条款

## 🔧 开发环境

- **Python**: 3.8+
- **IDE**: 推荐使用 PyCharm 或 VS Code
- **版本控制**: Git
- **包管理**: pip

## 📚 相关文档

- [Python 官方文档](https://docs.python.org/)
- [Requests 文档](https://requests.readthedocs.io/)
- [BeautifulSoup4 文档](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium 文档](https://selenium-python.readthedocs.io/)
- [Scrapy 文档](https://docs.scrapy.org/)
- [Loguru 文档](https://loguru.readthedocs.io/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)
