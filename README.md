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
│   │       ├── db_utils.py       # 数据库工具
│   │       └── image_downloader.py # 图片下载工具
├── data/                          # 数据存储目录
├── logs/                          # 日志文件目录
├── env.dev                        # 开发环境配置
├── env.prd                        # 生产环境配置
├── create_table_new.sql           # 数据库表结构
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

```bash
# 生产环境运行（默认--mode db）
python main.py crawl --env prd

# 开发环境运行
python main.py crawl --env dev

# 查看帮助
python main.py --help
```

### 5. 翻译功能使用

#### 添加数据库字段（首次使用）
```sql
-- 添加英文标题字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_en` VARCHAR(255) DEFAULT NULL COMMENT '英文标题' 
AFTER `title`;

-- 添加英文内容字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_en` TEXT DEFAULT NULL COMMENT '英文内容' 
AFTER `content`;
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

# 2. 查看翻译统计
python main.py translate --env dev --stats

# 3. 测试翻译（翻译5条记录）
python main.py translate --env dev --max-records 5 --batch-size 2 --auto

# 4. 批量翻译所有数据
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
    SUM(CASE WHEN title_en IS NOT NULL AND title_en != '' THEN 1 ELSE 0 END) as translated
FROM ims_mdkeji_im_boniu_forum_post;

-- 查看翻译结果
SELECT forum_post_id, title, title_en, LEFT(content, 50) as content, LEFT(content_en, 50) as content_en
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_en IS NOT NULL AND title_en != ''
LIMIT 10;
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
  `title_en` varchar(255) DEFAULT NULL COMMENT '英文标题',
  `content_en` text DEFAULT NULL COMMENT '英文内容',
  PRIMARY KEY (`id`),
  UNIQUE KEY `forum_post_id` (`forum_post_id`),
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
- `content`: 帖子正文内容
- `uniacid`: 应用ID（默认1）
- `title_en`: 英文标题（翻译功能）
- `content_en`: 英文内容（翻译功能）

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

爬虫运行时会生成详细日志，包括：

- 爬取进度信息
- 数据库操作记录
- 图片下载状态
- 错误和异常信息
- 性能统计信息

日志文件位置: `logs/crawler.log`

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

### 5. 定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点运行）
0 2 * * * cd /path/to/project/boniu-crawler && source venv/bin/activate && python main.py --env prd
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

## 📚 相关文档

### 项目文档
- [翻译功能使用指南](docs/translation_guide.md)
- [翻译功能快速开始](TRANSLATION_QUICKSTART.md)
- [翻译工具文档](docs/translator.md)
- [翻译功能实现文档](docs/translation_implementation.md)

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