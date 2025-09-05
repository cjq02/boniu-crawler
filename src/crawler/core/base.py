"""
基础爬虫类
"""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from ..config.settings import get_settings
from ..utils.anti_detect import random_delay, get_random_user_agent


@dataclass
class CrawlerStats:
    """爬虫统计信息"""
    total: int = 0
    success: int = 0
    failed: int = 0
    retries: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class CrawlResult:
    """爬取结果"""
    url: str
    data: Any
    status_code: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class BaseCrawler(ABC):
    """基础爬虫类"""
    
    def __init__(self, name: str = "crawler"):
        self.name = name
        self.settings = get_settings()
        self.logger = None  # 将在子类中初始化
        self.stats = CrawlerStats()
        self.is_running = False
        
    def start(self) -> None:
        """开始爬取"""
        if self.is_running:
            raise RuntimeError("爬虫已在运行中")
        
        self.is_running = True
        self.stats.start_time = datetime.now()
        if self.logger:
            self.logger.info(f"爬虫 {self.name} 开始运行")
        
        try:
            self.before_start()
            self.run()
            self.after_complete()
        except Exception as e:
            if self.logger:
                self.logger.error(f"爬虫运行失败: {str(e)}")
            raise
        finally:
            self.is_running = False
            self.stats.end_time = datetime.now()
            self.log_stats()
    
    def stop(self) -> None:
        """停止爬虫"""
        if not self.is_running:
            return
        
        if self.logger:
            self.logger.info("正在停止爬虫...")
        self.is_running = False
        self.before_stop()
    
    def get_status(self) -> Dict[str, Any]:
        """获取爬虫状态"""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "stats": {
                "total": self.stats.total,
                "success": self.stats.success,
                "failed": self.stats.failed,
                "retries": self.stats.retries,
                "start_time": self.stats.start_time.isoformat() if self.stats.start_time else None,
                "end_time": self.stats.end_time.isoformat() if self.stats.end_time else None,
            }
        }
    
    def log_stats(self) -> None:
        """记录统计信息"""
        if not self.stats.start_time or not self.stats.end_time or not self.logger:
            return
        
        duration = (self.stats.end_time - self.stats.start_time).total_seconds()
        success_rate = (self.stats.success / self.stats.total * 100) if self.stats.total > 0 else 0
        
        self.logger.info(
            f"爬虫统计: 总计={self.stats.total}, "
            f"成功={self.stats.success}, "
            f"失败={self.stats.failed}, "
            f"重试={self.stats.retries}, "
            f"成功率={success_rate:.2f}%, "
            f"耗时={duration:.2f}秒"
        )
    
    def apply_anti_crawler_strategy(self) -> None:
        """应用反爬虫策略"""
        if not self.settings.anti_crawler.enabled:
            return
        
        # 随机延迟
        if self.settings.anti_crawler.random_delay:
            delay = random_delay(*self.settings.anti_crawler.delay_range)
            if self.logger:
                self.logger.debug(f"应用随机延迟: {delay:.2f}秒")
            time.sleep(delay)
        
        # 旋转User-Agent
        if self.settings.anti_crawler.rotate_user_agents:
            user_agent = get_random_user_agent()
            if self.logger:
                self.logger.debug(f"切换User-Agent: {user_agent}")
    
    def handle_error(self, error: Exception, url: str, attempt: int = 1) -> bool:
        """
        处理错误
        
        Args:
            error: 错误对象
            url: 请求的URL
            attempt: 当前尝试次数
            
        Returns:
            是否应该重试
        """
        if self.logger:
            self.logger.error(f"爬取失败 {url}: {str(error)} (尝试 {attempt})")
        self.stats.failed += 1
        
        if attempt < self.settings.crawler.retries:
            if self.logger:
                self.logger.info(f"重试 {url} (第 {attempt + 1} 次)")
            self.stats.retries += 1
            time.sleep(self.settings.crawler.retry_delay * attempt)
            return True
        
        return False
    
    def validate_response(self, response: Any, url: str) -> bool:
        """
        验证响应
        
        Args:
            response: 响应对象
            url: 请求的URL
            
        Returns:
            是否有效
        """
        if response is None:
            raise ValueError("响应为空")
        
        # 子类可以重写此方法进行更详细的验证
        return True
    
    def parse_data(self, data: Any, url: str) -> Any:
        """
        解析数据
        
        Args:
            data: 原始数据
            url: 请求的URL
            
        Returns:
            解析后的数据
        """
        # 子类可以重写此方法进行数据解析
        return data
    
    def save_data(self, data: Any, filename: Optional[str] = None) -> str:
        """
        保存数据
        
        Args:
            data: 要保存的数据
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        from ..utils.storage import save_data, generate_filename
        
        if filename is None:
            filename = generate_filename("crawled_data", self.settings.storage.format)
        
        file_path = save_data(data, filename)
        if self.logger:
            self.logger.info(f"数据已保存: {file_path}")
        return file_path
    
    def before_start(self) -> None:
        """爬取前的准备工作"""
        pass
    
    def after_complete(self) -> None:
        """爬取完成后的清理工作"""
        pass
    
    def before_stop(self) -> None:
        """停止前的清理工作"""
        pass
    
    @abstractmethod
    def run(self) -> None:
        """运行爬虫的主要逻辑"""
        pass
    
    @abstractmethod
    def crawl_url(self, url: str, **kwargs) -> CrawlResult:
        """
        爬取单个URL
        
        Args:
            url: 要爬取的URL
            **kwargs: 其他参数
            
        Returns:
            爬取结果
        """
        pass


class AsyncBaseCrawler(BaseCrawler):
    """异步基础爬虫类"""
    
    async def start(self) -> None:
        """异步开始爬取"""
        if self.is_running:
            raise RuntimeError("爬虫已在运行中")
        
        self.is_running = True
        self.stats.start_time = datetime.now()
        if self.logger:
            self.logger.info(f"异步爬虫 {self.name} 开始运行")
        
        try:
            await self.before_start()
            await self.run()
            await self.after_complete()
        except Exception as e:
            if self.logger:
                self.logger.error(f"异步爬虫运行失败: {str(e)}")
            raise
        finally:
            self.is_running = False
            self.stats.end_time = datetime.now()
            self.log_stats()
    
    async def stop(self) -> None:
        """异步停止爬虫"""
        if not self.is_running:
            return
        
        if self.logger:
            self.logger.info("正在停止异步爬虫...")
        self.is_running = False
        await self.before_stop()
    
    async def apply_anti_crawler_strategy(self) -> None:
        """异步应用反爬虫策略"""
        if not self.settings.anti_crawler.enabled:
            return
        
        # 随机延迟
        if self.settings.anti_crawler.random_delay:
            delay = random_delay(*self.settings.anti_crawler.delay_range)
            if self.logger:
                self.logger.debug(f"应用随机延迟: {delay:.2f}秒")
            await asyncio.sleep(delay)
        
        # 旋转User-Agent
        if self.settings.anti_crawler.rotate_user_agents:
            user_agent = get_random_user_agent()
            if self.logger:
                self.logger.debug(f"切换User-Agent: {user_agent}")
    
    async def handle_error(self, error: Exception, url: str, attempt: int = 1) -> bool:
        """
        异步处理错误
        
        Args:
            error: 错误对象
            url: 请求的URL
            attempt: 当前尝试次数
            
        Returns:
            是否应该重试
        """
        if self.logger:
            self.logger.error(f"爬取失败 {url}: {str(error)} (尝试 {attempt})")
        self.stats.failed += 1
        
        if attempt < self.settings.crawler.retries:
            if self.logger:
                self.logger.info(f"重试 {url} (第 {attempt + 1} 次)")
            self.stats.retries += 1
            await asyncio.sleep(self.settings.crawler.retry_delay * attempt)
            return True
        
        return False
    
    async def before_start(self) -> None:
        """异步爬取前的准备工作"""
        pass
    
    async def after_complete(self) -> None:
        """异步爬取完成后的清理工作"""
        pass
    
    async def before_stop(self) -> None:
        """异步停止前的清理工作"""
        pass
    
    @abstractmethod
    async def run(self) -> None:
        """异步运行爬虫的主要逻辑"""
        pass
    
    @abstractmethod
    async def crawl_url(self, url: str, **kwargs) -> CrawlResult:
        """
        异步爬取单个URL
        
        Args:
            url: 要爬取的URL
            **kwargs: 其他参数
            
        Returns:
            爬取结果
        """
        pass
