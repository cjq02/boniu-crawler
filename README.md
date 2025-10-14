# Boniu Crawler

一个专门用于爬取博牛社区论坛的Python爬虫项目，支持分页爬取、数据库存储、图片下载等完整功能。

## 🚀 功能特性

### 🎯 博牛社区专门爬虫
- **分页爬取**: 支持多页爬取，自动去重，智能停止
- **数据库存储**: 直接存储到MySQL数据库，支持增量更新
- **图片下载**: 自动下载帖子图片到本地，按日期分类存储
- **多版块支持**: 支持fid=89（我是提供商）和fid=734版块
- **完整帖子信息**: 获取标题、URL、用户信息、发帖时间、内容等
- **智能过滤**: 自动跳过置顶帖子，只爬取普通帖子
- **环境配置**: 支持开发/生产环境配置

### 🌐 智能翻译功能
- **自动翻译**: 爬取时自动翻译标题和内容为英文
- **批量翻译**: 支持历史数据的批量翻译
- **多API支持**: 支持百度翻译和谷歌翻译API
- **智能错误处理**: 翻译失败不影响数据保存
- **灵活配置**: 可调整翻译参数和批次大小
- **统计功能**: 实时查看翻译进度和统计信息

### ⏰ 定时任务功能
- **自动调度**: 支持每两天晚上11点自动执行爬虫任务
- **执行记录**: 完整的任务执行日志记录到数据库
- **状态监控**: 实时监控任务执行状态和结果
- **跨平台支持**: 支持Windows任务计划程序和Linux cron
- **错误处理**: 完善的异常处理和超时机制
- **日志管理**: 详细的执行日志和错误信息记录

### 🛠️ 技术特性
- **模块化设计**: 基于包结构的可扩展架构
- **数据库集成**: 使用PyMySQL连接MySQL数据库
- **图片管理**: 自动下载并保存图片到本地
- **环境变量**: 支持.env文件配置
- **详细日志**: 完整的爬取过程日志记录
- **错误处理**: 完善的异常处理和重试机制
- **去重策略**: 基于forum_post_id的智能去重

## 📦 技术栈

- **Python**: 3.11+
- **Requests**: HTTP客户端
- **BeautifulSoup4**: HTML解析
- **PyMySQL**: MySQL数据库连接
- **python-dotenv**: 环境变量管理
- **Loguru**: 日志管理

## 🏗️ 项目结构

```
boniu-crawler/
├── src/                           # 源代码目录
│   ├── cli/                       # 命令行接口
│   │   └── main.py               # 主程序入口
│   ├── crawler/                   # 爬虫核心
│   │   ├── sites/boniu/          # 博牛站点爬虫
│   │   │   └── crawler.py        # 博牛爬虫实现
│   │   └── utils/                # 工具模块
│   │       ├── db.py             # 数据库工具
│   │       └── image_downloader.py # 图片下载工具
│   └── scheduler/                 # 定时任务模块
│       └── scheduled_crawler.py  # 定时任务执行脚本
├── data/                          # 数据存储目录
├── logs/                          # 日志文件目录
│   └── scheduled/                 # 定时任务日志
├── docs/                          # 项目文档
│   └── scheduled_task_guide.md   # 定时任务设置指南
├── scripts/                       # 脚本工具
├── env.dev                        # 开发环境配置
├── env.prd                        # 生产环境配置
├── create_table_new.sql           # 数据库表结构
├── create_crawler_log_table.sql   # 定时任务日志表结构
├── run_scheduled_crawler.bat      # Windows定时任务执行脚本
├── setup_cron.sh                  # Linux cron设置脚本
├── setup_windows_task.ps1         # Windows任务计划程序设置脚本
├── requirements.txt               # 依赖文件
└── README.md                      # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd boniu-crawler

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

### 2. 数据库准备

```bash
# 连接MySQL数据库
mysql -h mysql -P 3306 -u fuye_user -p im_fuye

# 创建数据表
source create_table_new.sql;
```

### 3. 环境配置

```bash
# 检查环境变量文件
cat env.prd

# 确认图片保存路径配置
# BONIU_IMG_BASE_PATH=D:\me\epiboly\fuye\resource\img\boniu
```

### 4. 运行爬虫

#### 手动运行爬虫命令

```bash
# 生产环境运行（默认--mode db）
python main.py crawl --env prd

# 开发环境运行
python main.py crawl --env dev

# 指定爬取页数
python main.py crawl --env prd --pages 3

# 开发环境指定页数
python main.py crawl --env dev --pages 2

# 查看帮助
python main.py --help
```

#### 直接运行爬虫模块

```bash
# 直接运行博牛爬虫（使用默认配置）
python -c "from src.crawler.sites.boniu.crawler import BoniuCrawler; crawler = BoniuCrawler(); crawler.run()"

# 运行爬虫并指定参数
python -c "
from src.crawler.sites.boniu.crawler import BoniuCrawler
crawler = BoniuCrawler()
crawler.crawl_paginated_and_store(max_pages=2, delay_seconds=3.0, overwrite=False)
"

# 运行爬虫并覆盖已存在数据
python -c "
from src.crawler.sites.boniu.crawler import BoniuCrawler
crawler = BoniuCrawler()
crawler.crawl_paginated_and_store(max_pages=1, delay_seconds=2.0, overwrite=True)
"
```

### 5. 翻译功能使用

#### 添加数据库字段（首次使用）
```sql
-- 添加中文标题字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_zh` VARCHAR(255) DEFAULT NULL COMMENT '中文标题' 
AFTER `title`;

-- 添加中文内容字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_zh` TEXT DEFAULT NULL COMMENT '中文内容' 
AFTER `content`;

-- 添加英文标题字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_en` VARCHAR(255) DEFAULT NULL COMMENT '英文标题' 
AFTER `title_zh`;

-- 添加英文内容字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_en` TEXT DEFAULT NULL COMMENT '英文内容' 
AFTER `content_zh`;

-- 添加内容摘要字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary` VARCHAR(200) DEFAULT NULL COMMENT '内容摘要' 
AFTER `content`;

-- 添加英文内容摘要字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary_en` VARCHAR(200) DEFAULT NULL COMMENT '英文内容摘要' 
AFTER `content_en`;

-- 添加中文内容摘要字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary_zh` VARCHAR(200) DEFAULT NULL COMMENT '中文内容摘要' 
AFTER `content_summary_en`;
```

#### 爬取时自动翻译
```bash
# 爬取新数据时自动翻译
python main.py crawl --env dev --pages 2
```

#### 翻译历史数据
```bash
# 查看翻译统计
python main.py translate --env dev --stats

# 自动翻译历史数据
python main.py translate --env dev --max-records 10 --batch-size 5 --auto

# 翻译所有历史数据
python main.py translate --env dev --batch-size 20 --delay 1.5 --auto
```

### 6. 翻译功能快速使用

#### 首次使用翻译功能
```bash
# 1. 添加数据库字段（首次使用）
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_translation_fields.sql

# 2. 添加摘要字段（首次使用）
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_content_summary_fields.sql

# 3. 查看翻译统计
python main.py translate --env dev --stats

# 4. 测试翻译（翻译5条记录）
python main.py translate --env dev --max-records 5 --batch-size 2 --auto

# 5. 批量翻译所有数据
python main.py translate --env dev --batch-size 20 --delay 1.5 --auto
```

#### 日常使用
```bash
# 爬取新数据（自动翻译）
python main.py crawl --env dev --pages 2

# 查看翻译进度
python main.py translate --env dev --stats

# 翻译剩余数据
python main.py translate --env dev --auto
```

## 📖 使用示例

### 命令行使用

```bash
# 爬取数据
python main.py crawl --env prd
python main.py crawl --env dev

# 指定爬取页数
python main.py crawl --env prd --pages 3
python main.py crawl --env dev --pages 2

# 直接运行爬虫模块（绕过CLI）
python -c "from src.crawler.sites.boniu.crawler import BoniuCrawler; crawler = BoniuCrawler(); crawler.run()"

# 运行爬虫并自定义参数
python -c "
from src.crawler.sites.boniu.crawler import BoniuCrawler
crawler = BoniuCrawler()
crawler.crawl_paginated_and_store(max_pages=2, delay_seconds=3.0, overwrite=False)
"

# 翻译功能
python main.py translate --env dev --stats
python main.py translate --env dev --max-records 10 --auto

# 查看运行日志
tail -f logs/crawler.log
```

### 数据库查询

```sql
-- 查看爬取的数据
SELECT COUNT(*) FROM ims_mdkeji_im_boniu_forum_post;

-- 查看最新数据
SELECT title, username, publish_time, fid 
FROM ims_mdkeji_im_boniu_forum_post 
ORDER BY crawl_time DESC 
LIMIT 10;

-- 按版块统计
SELECT fid, COUNT(*) as count 
FROM ims_mdkeji_im_boniu_forum_post 
GROUP BY fid;

-- 查看翻译统计
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN title_zh IS NOT NULL AND title_zh != '' AND title_en IS NOT NULL AND title_en != '' THEN 1 ELSE 0 END) as translated
FROM ims_mdkeji_im_boniu_forum_post;

-- 查看翻译结果
SELECT forum_post_id, title, title_zh, title_en, LEFT(content, 50) as content, LEFT(content_zh, 50) as content_zh, LEFT(content_en, 50) as content_en
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_zh IS NOT NULL AND title_zh != '' AND title_en IS NOT NULL AND title_en != ''
LIMIT 10;

-- 查看摘要字段
SELECT forum_post_id, title, content_summary, content_summary_zh, content_summary_en
FROM ims_mdkeji_im_boniu_forum_post 
WHERE content_summary IS NOT NULL AND content_summary != ''
LIMIT 10;

-- 查看执行记录
SELECT 
  id,
  start_time,
  end_time,
  status,
  execution_type,
  command,
  parameters,
  posts_count,
  message,
  TIMESTAMPDIFF(SECOND, start_time, end_time) as duration_seconds
FROM ims_mdkeji_im_boniu_crawler_log 
ORDER BY start_time DESC 
LIMIT 10;

-- 查看执行统计（按日期和执行类型）
SELECT 
  DATE(start_time) as execution_date,
  execution_type,
  COUNT(*) as total_executions,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
  SUM(posts_count) as total_posts_crawled
FROM ims_mdkeji_im_boniu_crawler_log 
WHERE start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(start_time), execution_type
ORDER BY execution_date DESC, execution_type;

-- 按执行类型统计
SELECT 
  execution_type,
  COUNT(*) as total_executions,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
  SUM(posts_count) as total_posts_crawled
FROM ims_mdkeji_im_boniu_crawler_log 
WHERE start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY execution_type;
```

## ⚙️ 配置说明

### 环境变量配置

#### 开发环境 (env.dev)
```bash
BONIU_IMG_BASE_PATH=D:\me\epiboly\fuye\projects\im.fuye.io\attachment\images\boniu
```

#### 生产环境 (env.prd)
```bash
BONIU_IMG_BASE_PATH=D:\me\epiboly\fuye\resource\img\boniu
```

### 翻译功能配置

#### 翻译器配置 (config/translator.yaml)
```yaml
translator:
  default_provider: "baidu"
  
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    api_url: "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
  google:
    api_key: ""
    api_url: "https://translation.googleapis.com/language/translate/v2"
    
  settings:
    default_from_lang: "zh"
    default_to_lang: "en"
    timeout: 10
    retry_count: 3
    retry_interval: 1
```

### 数据库配置

数据库连接参数通过环境变量配置：
- `DB_HOST`: 数据库主机（默认：127.0.0.1）
- `DB_PORT`: 数据库端口（默认：3306）
- `DB_USER`: 数据库用户名（默认：fuye_user）
- `DB_PASSWORD`: 数据库密码（默认：fuye345abc）
- `DB_NAME`: 数据库名称（默认：im_fuye）

## 📊 数据存储

### 数据库表结构

```sql
CREATE TABLE `ims_mdkeji_im_boniu_forum_post` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `forum_post_id` int(11) NOT NULL COMMENT '论坛帖子ID',
  `title` varchar(255) NOT NULL COMMENT '帖子标题',
  `url` varchar(500) NOT NULL COMMENT '帖子链接',
  `user_id` int(11) DEFAULT NULL COMMENT '用户ID',
  `username` varchar(100) NOT NULL COMMENT '用户名',
  `avatar_url` varchar(500) DEFAULT NULL COMMENT '头像链接',
  `publish_time` datetime NOT NULL COMMENT '发布时间',
  `reply_count` int(11) DEFAULT 0 COMMENT '回复数',
  `view_count` int(11) DEFAULT 0 COMMENT '浏览数',
  `images` text COMMENT '图片路径JSON',
  `category` varchar(100) DEFAULT NULL COMMENT '分类',
  `is_sticky` tinyint(1) DEFAULT 0 COMMENT '是否置顶',
  `is_essence` tinyint(1) DEFAULT 0 COMMENT '是否精华',
  `crawl_time` datetime NOT NULL COMMENT '爬取时间',
  `fid` int(11) NOT NULL COMMENT '版块ID',
  `is_crawl` tinyint(1) DEFAULT 1 COMMENT '是否已爬取',
  `content` text COMMENT '帖子内容',
  `uniacid` int(11) NOT NULL DEFAULT 1 COMMENT '应用ID',
  `title_zh` varchar(255) DEFAULT NULL COMMENT '中文标题',
  `content_zh` text DEFAULT NULL COMMENT '中文内容',
  `title_en` varchar(255) DEFAULT NULL COMMENT '英文标题',
  `content_en` text DEFAULT NULL COMMENT '英文内容',
  `content_summary` varchar(200) DEFAULT NULL COMMENT '内容摘要',
  `content_summary_en` varchar(200) DEFAULT NULL COMMENT '英文内容摘要',
  `content_summary_zh` varchar(200) DEFAULT NULL COMMENT '中文内容摘要',
  PRIMARY KEY (`id`),
  UNIQUE KEY `forum_post_id` (`forum_post_id`),
  KEY `idx_title_zh` (`title_zh`),
  KEY `idx_title_en` (`title_en`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='博牛论坛帖子表';
```

### 数据字段说明

- `id`: 自增主键
- `forum_post_id`: 论坛原始帖子ID（唯一键）
- `title`: 帖子标题
- `url`: 帖子链接
- `user_id`: 用户ID（可为空）
- `username`: 用户名
- `avatar_url`: 用户头像链接
- `publish_time`: 发布时间
- `reply_count`: 回复数（默认0）
- `view_count`: 浏览数（默认0）
- `images`: 图片路径JSON数组
- `category`: 帖子分类
- `is_sticky`: 是否置顶（0/1）
- `is_essence`: 是否精华（0/1）
- `crawl_time`: 爬取时间
- `fid`: 版块ID（89或734）
- `is_crawl`: 是否已爬取（0/1）
- `content`: 帖子正文内容（原文）
- `uniacid`: 应用ID（默认1）
- `title_zh`: 中文标题（翻译功能）
- `content_zh`: 中文内容（翻译功能）
- `title_en`: 英文标题（翻译功能）
- `content_en`: 英文内容（翻译功能）
- `content_summary`: 内容摘要（前200字符）
- `content_summary_en`: 英文内容摘要（前200字符）
- `content_summary_zh`: 中文内容摘要（前200字符）

### 定时任务日志表结构

```sql
CREATE TABLE `ims_mdkeji_im_boniu_crawler_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `start_time` datetime NOT NULL COMMENT '任务开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '任务结束时间',
  `status` enum('running','success','failed','timeout','error') NOT NULL DEFAULT 'running' COMMENT '执行状态',
  `execution_type` enum('scheduled','manual') NOT NULL DEFAULT 'manual' COMMENT '执行类型：scheduled=定时任务，manual=手动执行',
  `environment` varchar(50) NOT NULL DEFAULT 'production' COMMENT '执行环境',
  `command` varchar(500) DEFAULT NULL COMMENT '执行命令',
  `parameters` text COMMENT '执行参数JSON',
  `pages` int(11) NOT NULL DEFAULT 2 COMMENT '爬取页数',
  `posts_count` int(11) NOT NULL DEFAULT 0 COMMENT '本次爬取的帖子数量',
  `message` text COMMENT '执行消息或错误信息',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_start_time` (`start_time`),
  KEY `idx_status` (`status`),
  KEY `idx_execution_type` (`execution_type`),
  KEY `idx_environment` (`environment`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬虫执行日志表';
```

### 定时任务日志字段说明

- `id`: 自增主键
- `start_time`: 任务开始时间
- `end_time`: 任务结束时间
- `status`: 执行状态（running/success/failed/timeout/error）
- `execution_type`: 执行类型（scheduled=定时任务，manual=手动执行）
- `environment`: 执行环境（production/development）
- `command`: 执行命令
- `parameters`: 执行参数JSON
- `pages`: 爬取页数
- `posts_count`: 本次爬取的帖子数量
- `message`: 执行消息或错误信息
- `created_at`: 记录创建时间
- `updated_at`: 记录更新时间

## 🖼️ 图片管理

### 图片存储结构

```
BONIU_IMG_BASE_PATH/
└── boniu/
    └── 2025/
        └── 01/
            └── 15/
                ├── image1.jpg
                ├── image2.png
                └── ...
```

### 图片路径格式

- 本地存储路径: `{BONIU_IMG_BASE_PATH}/boniu/YYYY/MM/DD/filename.ext`
- 数据库存储路径: `images/boniu/YYYY/MM/DD/filename.ext`

## 📝 日志管理

### 爬虫运行日志
爬虫运行时会生成详细日志，包括：

- 爬取进度信息
- 数据库操作记录
- 图片下载状态
- 错误和异常信息
- 性能统计信息

日志文件位置: `logs/crawler.log`

### 定时任务日志
定时任务执行时会生成专门的日志：

- 任务执行状态
- 执行时间和持续时间
- 爬取结果统计
- 错误和异常信息
- 数据库执行记录

日志文件位置: 
- 主日志: `logs/scheduled/YYYY/MM/DD.log` (按年/月/日组织)
- Cron日志: `logs/scheduled/cron.log` (Linux)
- 任务日志: 通过Windows事件查看器查看

## 🧪 测试

```bash
# 测试模块导入
python -c "from src.crawler.sites.boniu.crawler import BoniuCrawler; print('导入成功')"

# 测试数据库连接
python -c "from src.crawler.utils.db_utils import get_db_connection; conn = get_db_connection(); print('数据库连接成功')"

# 测试图片下载
python -c "from src.crawler.utils.image_downloader import ImageDownloader; downloader = ImageDownloader(); print('图片下载器初始化成功')"
```

## 🔧 生产环境部署

### 1. 服务器环境准备

```bash
# 安装Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 安装MySQL客户端
sudo apt install mysql-client
```

### 2. 项目部署

```bash
# 上传项目到服务器
scp -r boniu-crawler/ user@server:/path/to/project/

# 进入项目目录
cd /path/to/project/boniu-crawler

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 配置生产环境变量
cp env.prd .env

# 创建图片存储目录
mkdir -p /path/to/resource/img/boniu
```

### 4. 运行爬虫

```bash
# 后台运行
nohup python main.py --env prd > crawler.log 2>&1 &

# 查看运行状态
ps aux | grep python

# 查看日志
tail -f crawler.log
```

### 5. 定时任务设置

#### 创建执行日志表
```bash
# 连接到MySQL数据库
mysql -u your_username -p your_database

# 执行SQL脚本创建日志表
source create_crawler_log_table.sql
```

#### Windows系统设置
```powershell
# 以管理员身份运行PowerShell
cd D:\me\epiboly\fuye\projects\boniu-crawler
.\setup_windows_task.ps1
```

#### Linux/Unix系统设置
```bash
# 给脚本执行权限
chmod +x setup_cron.sh

# 运行设置脚本
./setup_cron.sh
```

#### 测试定时任务
```bash
# 手动测试执行
python src/scheduler/scheduled_crawler.py

# 或使用批处理文件（Windows）
run_scheduled_crawler.bat
```

### 6. 定时任务状态检查

在 CentOS 服务器上检查定时任务状态的常用命令：

1. 查看 crond 服务状态
```bash
systemctl status crond
```

2. 查看当前用户的定时任务
```bash
crontab -l
```

3. 查看系统级定时任务
```bash
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
ls -la /etc/cron.monthly/
ls -la /etc/cron.weekly/
```

4. 查看定时任务执行日志
```bash
# 查看最近的 cron 日志
tail -20 /var/log/cron

# 实时监控 cron 日志
tail -f /var/log/cron

# 查看今天的 cron 日志
grep "$(date +%b\ %d)" /var/log/cron
```

5. 检查 crond 服务是否运行
```bash
# 检查服务状态
systemctl is-active crond

# 检查服务是否启用
systemctl is-enabled crond

# 查看服务详细信息
systemctl show crond
```

6. 查看定时任务进程
```bash
# 查看 crond 进程
ps aux | grep crond

# 查看定时任务相关进程
ps aux | grep cron
```

7. 测试定时任务语法
```bash
# 如果有具体的定时任务文件，可以测试语法
crontab -T
```

8. 查看系统时间（定时任务依赖系统时间）
```bash
date
timedatectl status
```

## ⚠️ 注意事项

### 法律合规性
- 请遵守博牛社区的使用条款和robots.txt规则
- 注意数据使用的法律合规性，仅用于学习和研究目的
- 不要将爬取的数据用于商业用途

### 技术注意事项
- 合理设置爬取频率，避免对服务器造成压力
- 建议使用代理池避免IP被封
- 定期检查网站结构变化，及时更新爬虫代码
- 建议在非高峰时段进行爬取
- 确保数据库连接稳定
- 定期清理日志文件

### 数据质量
- 爬取的数据可能包含HTML标签，需要进一步清理
- 图片链接需要额外处理才能访问
- 时间格式需要统一化处理
- 建议定期验证数据的完整性和准确性

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库连接参数
   - 确认网络连接正常

2. **图片下载失败**
   - 检查图片保存路径权限
   - 验证网络连接
   - 检查磁盘空间

3. **爬取中断**
   - 查看日志文件定位问题
   - 检查网络连接稳定性
   - 验证目标网站可访问性

4. **导入错误**
   - 检查Python版本兼容性
   - 验证依赖包安装
   - 确认项目路径正确

5. **定时任务不执行**
   - 检查任务计划程序中的任务状态
   - 查看Windows事件日志或cron日志
   - 确认Python环境和依赖包正确安装
   - 验证数据库连接和日志表是否存在

6. **定时任务执行失败**
   - 查看详细日志文件
   - 检查网络连接
   - 确认目标网站可访问
   - 验证环境变量配置

## 📚 相关文档

### 项目文档
- [翻译功能使用指南](docs/translation_guide.md)
- [翻译功能快速开始](TRANSLATION_QUICKSTART.md)
- [翻译工具文档](docs/translator.md)
- [翻译功能实现文档](docs/translation_implementation.md)
- [定时任务设置指南](docs/scheduled_task_guide.md)

### 技术文档
- [Python 官方文档](https://docs.python.org/)
- [Requests 文档](https://requests.readthedocs.io/)
- [BeautifulSoup4 文档](https://www.crummy.com/software/BeautifulSoup/)
- [PyMySQL 文档](https://pymysql.readthedocs.io/)
- [python-dotenv 文档](https://python-dotenv.readthedocs.io/)
- [百度翻译API文档](https://fanyi-api.baidu.com/doc/21)
- [谷歌翻译API文档](https://cloud.google.com/translate/docs)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request
5. 打开 Pull Request