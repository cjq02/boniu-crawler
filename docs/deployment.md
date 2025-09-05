# 部署文档

## 环境要求

- Python 3.8+
- pip 或 conda
- 网络连接

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd boniu-crawler
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 使用 conda
conda create -n boniu-crawler python=3.8
conda activate boniu-crawler
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
# 根据需要修改 .env 文件
```

## 运行方式

### 命令行运行

```bash
# 使用主入口
python main.py

# 使用CLI模块
python -m src.cli.main

# 指定输出文件
python main.py --output data/my_posts.json
```

### 作为包运行

```bash
# 安装包
pip install -e .

# 使用命令行工具
boniu-crawler --output data/posts.json
```

### Python代码中使用

```python
from src.crawler.sites.boniu.crawler import BoniuCrawler

crawler = BoniuCrawler()
posts = crawler.crawl_forum_posts()
crawler.save_data(posts, "my_posts.json")
```

## 配置说明

### 环境变量

主要环境变量：

- `BONIU__BASE_URL`: 博牛社区基础URL
- `BONIU__FORUM_URL`: 论坛页面URL
- `CRAWLER__TIMEOUT`: 请求超时时间
- `CRAWLER__RETRIES`: 重试次数
- `ANTI_CRAWLER__ENABLED`: 是否启用反爬虫策略
- `PROXY__ENABLED`: 是否启用代理

### 配置文件

- `config/development.yaml`: 开发环境配置
- `config/production.yaml`: 生产环境配置
- `config/sites/boniu.yaml`: 博牛站点配置

## 生产部署

### 1. 服务器要求

- Linux/Windows 服务器
- Python 3.8+
- 足够的磁盘空间存储数据
- 稳定的网络连接

### 2. 部署步骤

```bash
# 1. 上传代码到服务器
scp -r boniu-crawler/ user@server:/opt/

# 2. 在服务器上安装依赖
cd /opt/boniu-crawler
pip install -r requirements.txt

# 3. 配置生产环境
cp config/production.yaml config/active.yaml
cp env.example .env
# 编辑 .env 文件

# 4. 创建必要目录
mkdir -p data/{raw,processed,exports,cache}
mkdir -p logs

# 5. 设置权限
chmod +x scripts/*.sh
```

### 3. 定时任务

使用 cron 设置定时爬取：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天凌晨2点执行）
0 2 * * * cd /opt/boniu-crawler && python main.py >> logs/cron.log 2>&1
```

### 4. 监控

- 监控日志文件大小
- 监控数据文件更新
- 监控爬虫运行状态

## 故障排除

### 常见问题

1. **网络连接问题**
   - 检查网络连接
   - 检查代理设置
   - 检查防火墙设置

2. **权限问题**
   - 检查文件读写权限
   - 检查目录创建权限

3. **依赖问题**
   - 重新安装依赖
   - 检查Python版本

4. **配置问题**
   - 检查配置文件格式
   - 检查环境变量设置

### 日志查看

```bash
# 查看最新日志
tail -f logs/crawler.log

# 查看错误日志
grep ERROR logs/crawler.log

# 查看特定日期日志
grep "2024-01-01" logs/crawler.log
```

## 性能优化

### 1. 并发设置

```yaml
crawler:
  max_concurrent: 5  # 根据服务器性能调整
```

### 2. 延迟设置

```yaml
anti_crawler:
  delay_range: [2, 5]  # 增加延迟避免被封
```

### 3. 代理使用

```yaml
proxy:
  enabled: true
  host: "proxy.example.com"
  port: 8080
```

## 安全考虑

1. **数据保护**
   - 定期备份数据
   - 加密敏感信息
   - 限制文件访问权限

2. **网络安全**
   - 使用HTTPS
   - 配置防火墙
   - 监控异常访问

3. **合规性**
   - 遵守robots.txt
   - 合理设置爬取频率
   - 遵守网站使用条款
