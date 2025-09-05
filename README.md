# Boniu Crawler

一个专门用于爬取博牛社区论坛的Python爬虫项目，支持获取帖子标题、图片、用户信息、发表时间等完整数据。

## 🚀 功能特性

### 🎯 博牛社区专门爬虫
- **论坛帖子爬取**: 专门爬取博牛社区论坛 (https://bbs.boniu123.cc/forum-89-1.html)
- **完整帖子信息**: 获取标题、URL、ID、用户名、头像、发帖时间、回复数、浏览数
- **图片提取**: 自动提取帖子中的图片链接
- **分类识别**: 自动识别帖子分类（游戏包网、游戏API、支付渠道等）
- **特殊标识**: 识别置顶帖子和精华帖子

### 🛠️ 技术特性
- **模块化设计**: 基于包结构的可扩展架构
- **多种爬取方式**: 支持Requests、Selenium、Scrapy等
- **高性能爬取**: 支持异步并发爬取
- **灵活数据存储**: 支持JSON、CSV、Excel等多种存储格式
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
├── main.py                     # 主程序入口（CLI）
├── boniu_crawler.py            # 博牛社区爬虫（正式版）
├── crawler.py                  # 基础爬虫类
├── requests_crawler.py          # Requests爬虫实现
├── config.py                   # 配置管理
├── logger.py                   # 日志管理
├── utils.py                    # 工具函数
├── crawler_pkg/                # 爬虫包
│   ├── __init__.py             # 包入口
│   ├── core/                   # 核心模块
│   │   ├── base.py             # 基础爬虫类
│   │   └── requests_impl.py    # Requests实现
│   └── site_boniu/             # 博牛站点爬虫
│       └── crawler.py          # 博牛爬虫实现
├── data/                       # 数据存储目录
│   ├── boniu_forum_posts.json  # 论坛帖子数据
│   ├── boniu_enhanced_posts.json # 增强版帖子数据
│   └── test_posts.json         # 测试数据
├── logs/                       # 日志文件目录
├── tests/                      # 测试文件目录
├── test_boniu_crawler.py       # 博牛爬虫测试
├── test_fixed_crawler.py       # 修复版爬虫测试
├── test_website.py             # 网站测试
├── requirements.txt            # 依赖文件
├── pyproject.toml              # 项目配置
├── env.example                 # 环境变量示例
├── BONIU_CRAWLER_README.md     # 博牛爬虫详细说明
├── PROJECT_SUMMARY.md          # 项目总结
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 一键运行

```bash
# 克隆项目
git clone <repository-url>
cd boniu-crawler

# 安装依赖
pip install -r requirements.txt

# 立即开始爬取
python main.py
```

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
# 使用CLI运行博牛爬虫（推荐）
python main.py

# 指定输出文件
python main.py --output data/my_posts.json

# 运行博牛爬虫（直接运行）
python boniu_crawler.py

# 运行测试脚本
python test_boniu_crawler.py

# 运行网站测试
python test_website.py
```

## 📖 使用示例

### 博牛爬虫使用

```python
from crawler_pkg import BoniuCrawler

# 创建博牛爬虫实例
crawler = BoniuCrawler()

# 爬取论坛帖子列表
posts = crawler.crawl_forum_posts()
print(f"获取到 {len(posts)} 个帖子")

# 查看帖子信息
for post in posts[:3]:  # 显示前3个帖子
    print(f"标题: {post['title']}")
    print(f"用户: {post['username']}")
    print(f"发布时间: {post['publish_time']}")
    print(f"回复数: {post['reply_count']}")
    print(f"浏览数: {post['view_count']}")
    print(f"分类: {post['category']}")
    print(f"是否置顶: {post['is_sticky']}")
    print(f"是否精华: {post['is_essence']}")
    print("---")
```

### 数据保存

```python
from crawler_pkg import BoniuCrawler
from utils import save_data

# 创建爬虫并爬取数据
crawler = BoniuCrawler()
posts = crawler.crawl_forum_posts()

# 保存数据到文件
if posts:
    file_path = save_data(posts, "boniu_posts", output_dir="data")
    print(f"数据已保存到: {file_path}")
    
    # 也可以使用爬虫内置的保存方法
    crawler.save_data(posts, "my_posts.json")
```

### 命令行使用

```bash
# 使用main.py作为CLI工具
python main.py --help

# 默认输出到data/boniu_forum_posts.json
python main.py

# 指定输出文件
python main.py --output data/my_custom_posts.json

# 查看输出
python main.py --output data/test_output.json
```

### 测试和调试

```python
# 运行测试脚本
python test_boniu_crawler.py

# 运行网站连接测试
python test_website.py

# 在代码中进行测试
from crawler_pkg import BoniuCrawler

crawler = BoniuCrawler()

# 测试单个帖子解析
test_html = "<html>...</html>"  # 示例HTML
# 可以在这里添加测试逻辑

# 查看日志
import logging
logging.basicConfig(level=logging.INFO)
```

### 扩展爬虫

```python
from crawler_pkg.site_boniu.crawler import BoniuCrawler

class EnhancedBoniuCrawler(BoniuCrawler):
    def __init__(self):
        super().__init__()
        # 添加自定义配置
        self.custom_headers = {
            'Custom-Header': 'MyValue'
        }
    
    def crawl_forum_posts(self):
        """重写爬取方法，添加自定义逻辑"""
        posts = super().crawl_forum_posts()
        
        # 添加自定义处理
        for post in posts:
            post['custom_field'] = self.process_custom_data(post)
        
        return posts
    
    def process_custom_data(self, post):
        """自定义数据处理"""
        # 在这里添加自定义逻辑
        return f"processed_{post.get('id', 'unknown')}"

# 使用扩展爬虫
crawler = EnhancedBoniuCrawler()
posts = crawler.crawl_forum_posts()
```

## ⚙️ 配置说明

### 环境变量配置

复制 `env.example` 文件为 `.env` 并配置以下参数：

```bash
# 应用配置
APP_NAME=Boniu Crawler
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=false

# 博牛爬虫配置
BONIU__BASE_URL=https://bbs.boniu123.cc
BONIU__FORUM_URL=https://bbs.boniu123.cc/forum-89-1.html
BONIU__TIMEOUT=30
BONIU__RETRIES=3
BONIU__RETRY_DELAY=1

# 爬虫通用配置
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
STORAGE__FILENAME=boniu_forum_posts

# 反爬虫配置
ANTI_CRAWLER__ENABLED=true
ANTI_CRAWLER__RANDOM_DELAY=true
ANTI_CRAWLER__DELAY_RANGE=1,3
ANTI_CRAWLER__ROTATE_USER_AGENTS=true
ANTI_CRAWLER__USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

### 博牛爬虫配置

- `BONIU__BASE_URL`: 博牛社区基础URL
- `BONIU__FORUM_URL`: 论坛页面URL
- `BONIU__TIMEOUT`: 请求超时时间（秒）
- `BONIU__RETRIES`: 重试次数
- `BONIU__RETRY_DELAY`: 重试延迟时间（秒）

### 通用爬虫配置

- `CRAWLER__TIMEOUT`: 请求超时时间（秒）
- `CRAWLER__RETRIES`: 重试次数
- `CRAWLER__RETRY_DELAY`: 重试延迟时间（秒）
- `CRAWLER__MAX_CONCURRENT`: 最大并发数

### 反爬虫配置

- `ANTI_CRAWLER__ENABLED`: 是否启用反爬虫策略
- `ANTI_CRAWLER__RANDOM_DELAY`: 是否启用随机延迟
- `ANTI_CRAWLER__DELAY_RANGE`: 延迟时间范围（秒）
- `ANTI_CRAWLER__ROTATE_USER_AGENTS`: 是否轮换User-Agent
- `ANTI_CRAWLER__USER_AGENT`: 自定义User-Agent

## 📊 数据存储

### 支持的数据格式

- **JSON**: 适合结构化数据（默认格式）
- **CSV**: 适合表格数据
- **Excel**: 适合复杂表格数据
- **TXT**: 适合纯文本数据

### 博牛爬虫数据字段

爬虫获取的每个帖子包含以下字段：

```json
{
  "id": "帖子ID",
  "title": "帖子标题",
  "url": "帖子链接",
  "username": "发帖用户名",
  "avatar_url": "用户头像链接",
  "publish_time": "发布时间",
  "reply_count": 回复数,
  "view_count": 浏览数,
  "images": ["帖子图片链接列表"],
  "category": "帖子分类",
  "is_sticky": 是否置顶,
  "is_essence": 是否精华,
  "crawl_time": "爬取时间"
}
```

### 输出文件

- `data/boniu_forum_posts.json`: 默认输出文件
- `data/boniu_enhanced_posts.json`: 增强版数据
- `data/test_posts.json`: 测试数据

## 📝 日志管理

使用Loguru进行日志管理，支持：

- 控制台输出
- 文件记录
- 错误追踪
- 性能监控
- 日志轮转

## 🧪 测试

项目包含完整的测试脚本：

```bash
# 运行博牛爬虫测试
python test_boniu_crawler.py

# 运行修复版爬虫测试
python test_fixed_crawler.py

# 运行网站连接测试
python test_website.py

# 使用pytest运行测试（如果配置了pytest）
pytest tests/

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

### 法律合规性
- 请遵守博牛社区的使用条款和robots.txt规则
- 注意数据使用的法律合规性，仅用于学习和研究目的
- 不要将爬取的数据用于商业用途

### 技术注意事项
- 合理设置爬取频率，避免对博牛社区服务器造成压力
- 建议使用代理池避免IP被封
- 定期检查网站结构变化，及时更新爬虫代码
- 建议在非高峰时段进行爬取

### 数据质量
- 爬取的数据可能包含HTML标签，需要进一步清理
- 图片链接可能需要额外处理才能访问
- 时间格式可能需要统一化处理
- 建议定期验证数据的完整性和准确性

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
