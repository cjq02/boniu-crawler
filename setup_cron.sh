#!/bin/bash
# 博牛社区爬虫定时任务设置脚本
# 每两天晚上11点执行一次

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "设置博牛社区爬虫定时任务..."
echo "项目目录: $SCRIPT_DIR"

# 创建cron任务条目
CRON_JOB="0 23 */2 * * cd $SCRIPT_DIR && python3 src/scheduler/scheduled_crawler.py >> logs/scheduled/cron.log 2>&1"

# 检查是否已存在相同的cron任务
if crontab -l 2>/dev/null | grep -q "scheduled_crawler.py"; then
    echo "警告: 已存在博牛爬虫的cron任务"
    echo "现有任务:"
    crontab -l 2>/dev/null | grep "scheduled_crawler.py"
    echo ""
    read -p "是否要替换现有任务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 删除现有任务
        crontab -l 2>/dev/null | grep -v "scheduled_crawler.py" | crontab -
        echo "已删除现有任务"
    else
        echo "取消设置"
        exit 0
    fi
fi

# 添加新的cron任务
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "定时任务设置成功!"
echo "任务详情: $CRON_JOB"
echo ""
echo "任务说明:"
echo "- 执行时间: 每两天晚上11点 (0 23 */2 * *)"
echo "- 执行脚本: $SCRIPT_DIR/src/scheduler/scheduled_crawler.py"
echo "- 日志文件: $SCRIPT_DIR/logs/scheduled/cron.log"
echo ""
echo "查看当前cron任务: crontab -l"
echo "编辑cron任务: crontab -e"
echo "删除所有cron任务: crontab -r"
echo ""
echo "测试执行: cd $SCRIPT_DIR && python3 src/scheduler/scheduled_crawler.py"
