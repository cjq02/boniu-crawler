#!/usr/bin/env python3
"""
博牛社区爬虫定时任务脚本
每两天晚上11点执行一次爬虫任务
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.utils.db import connect
from src.scheduler.execution_logger import get_execution_logger


def setup_logging():
    """设置日志"""
    log_dir = project_root / "logs" / "scheduled"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"scheduled_crawler_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


# 移除旧的记录函数，使用新的ExecutionLogger


def run_crawler():
    """执行爬虫任务"""
    logger = logging.getLogger(__name__)
    
    # 获取执行日志记录器
    execution_logger = get_execution_logger(environment='production', execution_type='scheduled')
    
    # 构建执行命令和参数
    cmd = [
        sys.executable, 
        "main.py", 
        "crawl", 
        "--env", "prd",  # 使用生产环境配置
        "--pages", "2",  # 爬取2页
        "--mode", "db"   # 直接入库模式
    ]
    
    command = " ".join(cmd)
    parameters = {
        "env": "prd",
        "pages": 2,
        "mode": "db"
    }
    
    # 使用执行上下文管理器记录日志
    with execution_logger.execution_context(pages=2, command=command, parameters=parameters):
        try:
            logger.info("开始执行博牛社区爬虫任务...")
            
            # 切换到项目根目录
            os.chdir(project_root)
            
            # 设置环境变量
            env = os.environ.copy()
            env['ENVIRONMENT'] = 'production'
            
            logger.info(f"执行命令: {command}")
            
            # 执行命令并捕获输出
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode == 0:
                logger.info("爬虫任务执行成功")
                logger.info(f"标准输出: {result.stdout}")
                
                # 尝试从输出中提取帖子数量
                posts_count = 0
                if "已插入/更新" in result.stdout:
                    import re
                    match = re.search(r'已插入/更新 (\d+) 条', result.stdout)
                    if match:
                        posts_count = int(match.group(1))
                
                # 更新执行记录中的帖子数量
                execution_logger.end_execution('success', '任务执行成功', posts_count)
                return True
                
            else:
                error_msg = f"爬虫任务执行失败，返回码: {result.returncode}"
                logger.error(error_msg)
                logger.error(f"错误输出: {result.stderr}")
                logger.error(f"标准输出: {result.stdout}")
                
                execution_logger.end_execution('failed', f"执行失败: {result.stderr[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "爬虫任务执行超时（1小时）"
            logger.error(error_msg)
            execution_logger.end_execution('timeout', error_msg)
            return False
            
        except Exception as e:
            error_msg = f"爬虫任务执行异常: {str(e)}"
            logger.error(error_msg)
            execution_logger.end_execution('error', error_msg)
            return False


def main():
    """主函数"""
    logger = setup_logging()
    
    logger.info("=" * 50)
    logger.info("博牛社区爬虫定时任务开始")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        success = run_crawler()
        
        if success:
            logger.info("定时任务执行成功")
            sys.exit(0)
        else:
            logger.error("定时任务执行失败")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"定时任务执行异常: {e}")
        sys.exit(1)
    
    finally:
        logger.info("=" * 50)
        logger.info("博牛社区爬虫定时任务结束")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
