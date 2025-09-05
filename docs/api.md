# API 文档

## 核心模块

### BaseCrawler

基础爬虫类，所有爬虫的父类。

#### 方法

- `start()`: 开始爬取
- `stop()`: 停止爬虫
- `crawl_url(url, **kwargs)`: 爬取单个URL
- `get_status()`: 获取爬虫状态
- `save_data(data, filename)`: 保存数据

### RequestsCrawler

基于requests的爬虫实现。

#### 方法

- `crawl_html(url, selectors, **kwargs)`: 爬取HTML页面
- `crawl_api(url, method, data, **kwargs)`: 爬取API数据
- `batch_crawl(urls, **kwargs)`: 批量爬取
- `crawl_paginated(base_url, page_config, **kwargs)`: 分页爬取

### BoniuCrawler

博牛社区专门爬虫。

#### 方法

- `crawl_forum_posts()`: 爬取论坛帖子列表
- `_parse_post_row(row)`: 解析帖子行数据

## 工具模块

### 解析工具 (parser.py)

- `clean_text(text)`: 清理文本
- `extract_number(text)`: 提取数字
- `extract_url(text)`: 提取URL
- `is_valid_url(url)`: 验证URL
- `extract_links_from_html(html, base_url)`: 从HTML提取链接
- `extract_json_from_html(html, script_selector)`: 从HTML提取JSON

### 存储工具 (storage.py)

- `save_data(data, filename, output_dir)`: 保存数据
- `load_data(filename, output_dir)`: 加载数据
- `generate_filename(prefix, extension)`: 生成文件名
- `ensure_dir(path)`: 确保目录存在

### 反检测工具 (anti_detect.py)

- `random_delay(min_delay, max_delay)`: 随机延迟
- `get_random_user_agent()`: 获取随机User-Agent
- `setup_session(session, settings)`: 设置会话

## 配置模块

### Settings

应用配置管理。

#### 配置项

- `crawler`: 爬虫基础配置
- `boniu`: 博牛爬虫配置
- `logging`: 日志配置
- `storage`: 存储配置
- `anti_crawler`: 反爬虫配置
- `proxy`: 代理配置

## 使用示例

```python
from src.crawler.sites.boniu.crawler import BoniuCrawler

# 创建爬虫实例
crawler = BoniuCrawler()

# 爬取论坛帖子
posts = crawler.crawl_forum_posts()

# 保存数据
crawler.save_data(posts, "boniu_posts.json")
```
