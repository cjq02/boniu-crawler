# 博牛社区爬虫定时任务设置指南

本指南介绍如何设置博牛社区爬虫的定时任务，支持每两天晚上11点自动执行爬虫任务。

## 文件说明

### 核心文件
- `src/scheduler/scheduled_crawler.py` - 主要的定时任务执行脚本
- `create_crawler_log_table.sql` - 创建执行日志表的SQL脚本
- `run_scheduled_crawler.bat` - Windows批处理执行文件

### 设置脚本
- `setup_cron.sh` - Linux/Unix系统cron任务设置脚本
- `setup_windows_task.ps1` - Windows任务计划程序设置脚本

## 快速开始

### 1. 创建执行日志表

首先需要在数据库中创建执行日志表：

```bash
# 连接到MySQL数据库
mysql -u your_username -p your_database

# 执行SQL脚本
source create_crawler_log_table.sql
```

### 2. 设置定时任务

#### Windows系统

1. **使用PowerShell脚本（推荐）**：
   ```powershell
   # 以管理员身份运行PowerShell
   cd D:\me\epiboly\fuye\projects\boniu-crawler
   .\setup_windows_task.ps1
   ```

2. **手动设置任务计划程序**：
   - 打开"任务计划程序" (taskschd.msc)
   - 创建基本任务
   - 设置触发器：每两天，晚上11:00
   - 设置操作：启动程序 `D:\me\epiboly\fuye\projects\boniu-crawler\run_scheduled_crawler.bat`

#### Linux/Unix系统

```bash
# 给脚本执行权限
chmod +x setup_cron.sh

# 运行设置脚本
./setup_cron.sh
```

### 3. 测试执行

```bash
# 手动测试执行
python src/scheduler/scheduled_crawler.py

# 或使用批处理文件（Windows）
run_scheduled_crawler.bat
```

## 配置说明

### 环境变量

确保设置了正确的环境变量：

```bash
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=fuye_user
DB_PASSWORD=fuye345abc
DB_NAME=im_fuye
DB_CHARSET=utf8mb4

# 环境标识
ENVIRONMENT=production
```

### 执行参数

定时任务默认配置：
- 爬取页数：2页
- 执行环境：production
- 超时时间：1小时
- 日志级别：INFO

## 日志和监控

### 日志文件位置
- 主日志：`logs/scheduled/scheduled_crawler_YYYYMMDD.log`
- Cron日志：`logs/scheduled/cron.log` (Linux)
- 任务日志：通过Windows事件查看器查看

### 数据库日志表

执行记录存储在 `ims_mdkeji_im_boniu_crawler_log` 表中：

```sql
-- 查看最近执行记录
SELECT 
  id,
  start_time,
  end_time,
  status,
  posts_count,
  message,
  TIMESTAMPDIFF(SECOND, start_time, end_time) as duration_seconds
FROM ims_mdkeji_im_boniu_crawler_log 
ORDER BY start_time DESC 
LIMIT 10;

-- 查看执行统计
SELECT 
  DATE(start_time) as execution_date,
  COUNT(*) as total_executions,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
  SUM(posts_count) as total_posts_crawled
FROM ims_mdkeji_im_boniu_crawler_log 
WHERE start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(start_time)
ORDER BY execution_date DESC;
```

## 故障排除

### 常见问题

1. **任务不执行**
   - 检查任务计划程序中的任务状态
   - 查看Windows事件日志或cron日志
   - 确认Python环境和依赖包正确安装

2. **数据库连接失败**
   - 检查数据库配置和环境变量
   - 确认数据库服务正在运行
   - 验证用户权限

3. **爬虫执行失败**
   - 检查网络连接
   - 查看详细日志文件
   - 确认目标网站可访问

### 调试模式

临时启用调试模式：

```bash
# 修改src/scheduler/scheduled_crawler.py中的日志级别
logging.basicConfig(level=logging.DEBUG, ...)
```

## 维护和更新

### 更新任务
```bash
# 重新运行设置脚本
./setup_cron.sh  # Linux
.\setup_windows_task.ps1  # Windows
```

### 清理日志
```bash
# 清理30天前的日志文件
find logs/scheduled -name "*.log" -mtime +30 -delete
```

### 监控任务状态
```bash
# 检查cron任务状态
crontab -l

# 检查Windows任务状态
Get-ScheduledTask -TaskName "博牛社区爬虫定时任务"
```

## 安全注意事项

1. 确保数据库密码等敏感信息通过环境变量配置
2. 定期备份执行日志表
3. 监控任务执行情况，及时发现异常
4. 设置适当的文件权限，保护脚本和日志文件

## 联系支持

如果遇到问题，请检查：
1. 日志文件中的错误信息
2. 数据库连接状态
3. 网络连接情况
4. Python环境和依赖包版本
