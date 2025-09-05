# Boniu Crawler - 重构版

一个专门用于爬取博牛社区论坛的专业Python爬虫项目，采用现代化的项目结构和最佳实践。

## 🏗️ 项目结构

```
boniu-crawler/
├── src/                          # 源代码目录
│   ├── crawler/                  # 爬虫核心包
│   │   ├── core/                 # 核心模块
│   │   │   ├── base.py           # 基础爬虫类
│   │   │   └── requests_impl.py  # Requests实现
│   │   ├── sites/                 # 站点特定爬虫
│   │   │   └── boniu/            # 博牛爬虫
│   │   │       └── crawler.py    # 博牛爬虫实现
│   │   ├── utils/                # 工具模块
│   │   │   ├── parser.py         # 解析工具
│   │   │   ├── storage.py        # 存储工具
│   │   │   ├── anti_detect.py    # 反检测工具
│   │   │   └── http.py           # HTTP工具
│   │   └── config/               # 配置模块
│   │       └── settings.py       # 配置管理
│   └── cli/                      # 命令行接口
│       └── main.py               # CLI主入口
├── tests/                        # 测试目录
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── fixtures/                 # 测试数据
├── data/                         # 数据目录
│   ├── raw/                      # 原始数据
│   ├── processed/                # 处理后数据
│   ├── exports/                  # 导出数据
│   └── cache/                    # 缓存数据
├── config/                       # 配置文件
│   ├── development.yaml          # 开发环境配置
│   ├── production.yaml           # 生产环境配置
│   └── sites/                    # 站点配置
│       └── boniu.yaml            # 博牛站点配置
├── docs/                         # 文档目录
│   ├── api.md                    # API文档
│   ├── architecture.md           # 架构文档
│   └── deployment.md             # 部署文档
├── logs/                         # 日志目录
├── scripts/                      # 脚本目录
├── main.py                       # 主入口文件
├── requirements.txt              # 依赖文件
├── pyproject.toml               # 项目配置
├── env.example                  # 环境变量示例
└── README.md                    # 项目说明
```

## 🚀 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行爬虫

```bash
# 使用主入口运行
python main.py

# 指定输出文件
python main.py --output data/my_posts.json

# 使用CLI模块
python -m src.cli.main --output data/posts.json
```

### Python代码中使用

```python
from src.crawler.sites.boniu.crawler import BoniuCrawler

# 创建爬虫实例
crawler = BoniuCrawler()

# 爬取论坛帖子
posts = crawler.crawl_forum_posts()
print(f"获取到 {len(posts)} 个帖子")

# 保存数据
crawler.save_data(posts, "boniu_posts.json")
```

## 🎯 功能特性

### 博牛社区专门爬虫
- **论坛帖子爬取**: 专门爬取博牛社区论坛
- **完整帖子信息**: 获取标题、URL、ID、用户名、头像、发帖时间、回复数、浏览数
- **图片提取**: 自动提取帖子中的图片链接
- **分类识别**: 自动识别帖子分类
- **特殊标识**: 识别置顶帖子和精华帖子

### 技术特性
- **模块化设计**: 基于包结构的可扩展架构
- **专业配置管理**: 使用Pydantic进行配置验证
- **完善的工具集**: 解析、存储、反检测等工具模块
- **详细的文档**: API文档、架构文档、部署文档
- **完整的测试**: 单元测试和集成测试

## 📊 数据格式

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

## ⚙️ 配置说明

### 环境变量配置

复制 `env.example` 文件为 `.env` 并配置：

```bash
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

# 反爬虫配置
ANTI_CRAWLER__ENABLED=true
ANTI_CRAWLER__RANDOM_DELAY=true
ANTI_CRAWLER__DELAY_RANGE=1,3
ANTI_CRAWLER__ROTATE_USER_AGENTS=true
```

### 配置文件

- `config/development.yaml`: 开发环境配置
- `config/production.yaml`: 生产环境配置
- `config/sites/boniu.yaml`: 博牛站点配置

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📚 文档

- [API文档](docs/api.md) - 详细的API说明
- [架构文档](docs/architecture.md) - 项目架构说明
- [部署文档](docs/deployment.md) - 部署指南

## 🔧 开发工具

```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# 导入排序
isort src/ tests/
```

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

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔄 重构说明

本项目已按照专业Python项目标准进行了重构：

- ✅ 采用 `src/` 布局，提高代码组织性
- ✅ 模块化设计，便于维护和扩展
- ✅ 完善的配置管理系统
- ✅ 专业的文档体系
- ✅ 完整的测试框架
- ✅ 现代化的项目结构

相比原版本，新版本具有更好的可维护性、可扩展性和专业性。
