"""
日志管理模块
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from config import get_settings


def setup_logger(
    level: str = "INFO",
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    file: Optional[str] = None,
    rotation: str = "1 day",
    retention: str = "30 days",
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        format: 日志格式
        file: 日志文件路径
        rotation: 日志轮转策略
        retention: 日志保留策略
    """
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        level=level,
        format=format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # 添加文件处理器
    if file:
        # 确保日志目录存在
        log_path = Path(file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            file,
            level=level,
            format=format,
            rotation=rotation,
            retention=retention,
            backtrace=True,
            diagnose=True,
            encoding="utf-8",
        )
    
    # 添加错误日志文件
    if file:
        error_file = str(Path(file).parent / "error.log")
        logger.add(
            error_file,
            level="ERROR",
            format=format,
            rotation=rotation,
            retention=retention,
            backtrace=True,
            diagnose=True,
            encoding="utf-8",
        )


def get_logger(name: str = "boniu_crawler"):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return logger.bind(name=name)


class CrawlerLogger:
    """爬虫专用日志记录器"""
    
    def __init__(self, name: str = "crawler"):
        self.logger = get_logger(name)
    
    def crawl_start(self, url: str, **kwargs):
        """记录爬取开始"""
        self.logger.info(f"开始爬取: {url}", extra=kwargs)
    
    def crawl_success(self, url: str, data_count: int = 1, **kwargs):
        """记录爬取成功"""
        self.logger.info(f"爬取成功: {url} (数据量: {data_count})", extra=kwargs)
    
    def crawl_error(self, url: str, error: Exception, **kwargs):
        """记录爬取错误"""
        self.logger.error(f"爬取失败: {url} - {str(error)}", extra=kwargs)
    
    def retry(self, url: str, attempt: int, **kwargs):
        """记录重试"""
        self.logger.warning(f"重试爬取: {url} (第{attempt}次)", extra=kwargs)
    
    def proxy_switch(self, old_proxy: str, new_proxy: str, **kwargs):
        """记录代理切换"""
        self.logger.info(f"切换代理: {old_proxy} -> {new_proxy}", extra=kwargs)
    
    def rate_limit(self, url: str, delay: float, **kwargs):
        """记录频率限制"""
        self.logger.warning(f"触发频率限制: {url}, 延迟{delay}秒", extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """记录信息"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, extra=kwargs)


# 初始化日志配置
settings = get_settings()
setup_logger(
    level=settings.logging.level,
    format=settings.logging.format,
    file=settings.logging.file,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
)

# 导出主要日志记录器
__all__ = ["get_logger", "CrawlerLogger", "setup_logger"]
