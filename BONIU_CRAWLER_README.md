# 博牛社区爬虫使用说明

## 概述

这是一个专门用于爬取博牛社区论坛 (https://bbs.boniu123.cc/forum-89-1.html) 的Python爬虫项目。该爬虫可以获取帖子的标题、图片、用户、发表时间以及帖子详情等信息。

## 功能特性

- **帖子列表爬取**: 获取论坛首页的帖子列表
- **帖子详情爬取**: 获取每个帖子的详细内容
- **图片提取**: 提取帖子中的图片链接
- **用户信息**: 获取发帖用户信息
- **回复信息**: 获取帖子的回复列表
- **数据存储**: 支持JSON格式保存

## 爬取的数据字段

### 帖子基本信息
- `title`: 帖子标题
- `url`: 帖子链接
- `username`: 发帖用户名
- `avatar_url`: 用户头像链接
- `publish_time`: 发布时间
- `reply_count`: 回复数
- `view_count`: 浏览数
- `images`: 帖子图片列表
- `category`: 帖子分类
- `is_sticky`: 是否置顶
- `is_essence`: 是否精华
- `crawl_time`: 爬取时间

### 帖子详情
- `content`: 帖子内容
- `content_images`: 帖子内容中的图片
- `attachments`: 帖子附件
- `replies`: 回复列表
- `post_id`: 帖子ID
- `original_publish_time`: 原始发布时间
- `last_reply_time`: 最后回复时间

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

#### 方式一：直接运行简化版爬虫
```bash
python boniu_simple_crawler.py
```

#### 方式二：运行完整版爬虫
```bash
python boniu_forum_crawler.py
```

#### 方式三：运行测试脚本
```bash
python test_boniu_crawler.py
```

### 3. 自定义使用

```python
from boniu_simple_crawler import BoniuSimpleCrawler

# 创建爬虫实例
crawler = BoniuSimpleCrawler()

# 爬取帖子列表
posts = crawler.crawl_forum_posts()

# 爬取特定帖子详情
detail = crawler.crawl_post_detail("https://bbs.boniu123.cc/thread-123456-1-1.html")

# 保存数据
crawler.save_data(posts, "my_posts.json")
```

## 配置说明

### 反爬虫设置

在 `config.py` 中可以调整以下设置：

```python
# 延迟设置
ANTI_CRAWLER__RANDOM_DELAY=true
ANTI_CRAWLER__DELAY_RANGE=1,3

# User-Agent轮换
ANTI_CRAWLER__ROTATE_USER_AGENTS=true

# 代理设置（可选）
PROXY__ENABLED=false
PROXY__HOST=127.0.0.1
PROXY__PORT=8080
```

### 请求设置

```python
# 超时设置
CRAWLER__TIMEOUT=30

# 重试设置
CRAWLER__RETRIES=3
CRAWLER__RETRY_DELAY=1
```

## 输出文件

爬虫运行后会生成以下文件：

- `boniu_forum_posts.json`: 完整的帖子数据
- `test_boniu_posts.json`: 测试数据
- `logs/crawler.log`: 日志文件

## 数据格式示例

```json
{
  "title": "【广告】源码接口冰点费率 + RTP可控，助你快速盈利",
  "url": "https://bbs.boniu123.cc/thread-1348365-1-1.html",
  "username": "Quickgaming",
  "avatar_url": "https://bbs.boniu123.cc/uc_server/data/avatar/000/67/65/87_avatar_small.jpg",
  "publish_time": "发表于 2025-7-5",
  "reply_count": 106,
  "view_count": 219000,
  "images": [
    "https://boniu-image-02-h.bn.live/discuz/data/attachment/forum/202507/05/123456.jpg"
  ],
  "category": "游戏API",
  "is_sticky": true,
  "is_essence": false,
  "crawl_time": "2025-09-04 10:30:00",
  "content": "帖子详细内容...",
  "content_images": [],
  "attachments": [],
  "replies": [
    {
      "username": "CliffScand",
      "reply_time": "6天前",
      "content": "回复内容...",
      "images": []
    }
  ],
  "post_id": "1348365",
  "original_publish_time": "2025-7-5 10:30:00",
  "last_reply_time": "6天前"
}
```

## 注意事项

### 1. 法律合规性
- 请确保遵守目标网站的使用条款
- 注意数据使用的法律合规性
- 建议在爬取前查看网站的robots.txt

### 2. 技术注意事项
- 合理设置爬取频率，避免对服务器造成压力
- 建议使用代理池避免IP被封
- 定期检查网站结构变化，及时更新爬虫

### 3. 数据质量
- 爬取的数据可能包含HTML标签，需要进一步清理
- 图片链接可能需要额外处理才能访问
- 时间格式可能需要统一化处理

## 故障排除

### 常见问题

1. **无法获取帖子列表**
   - 检查网络连接
   - 确认网站是否可访问
   - 查看日志文件了解详细错误

2. **解析失败**
   - 网站HTML结构可能发生变化
   - 运行 `test_boniu_crawler.py` 分析HTML结构
   - 更新选择器

3. **被封IP**
   - 增加延迟时间
   - 使用代理
   - 轮换User-Agent

### 调试方法

1. **查看日志**
```bash
tail -f logs/crawler.log
```

2. **分析HTML结构**
```bash
python test_boniu_crawler.py
```

3. **测试单个功能**
```python
from boniu_simple_crawler import BoniuSimpleCrawler
crawler = BoniuSimpleCrawler()
result = crawler.crawl_url("https://bbs.boniu123.cc/forum-89-1.html")
print(result.data[:1000])  # 查看页面内容
```

## 更新日志

### v1.0.0
- 初始版本
- 支持帖子列表和详情爬取
- 支持图片和附件提取
- 支持回复信息获取

## 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 运行测试脚本
3. 检查网络连接
4. 确认网站可访问性

## 免责声明

本爬虫仅供学习和研究使用，请遵守相关法律法规和网站使用条款。使用者需自行承担使用风险。
