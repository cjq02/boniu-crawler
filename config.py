"""
配置管理模块
"""

import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ProxyConfig(BaseModel):
    """代理配置"""
    enabled: bool = False
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None


class BrowserConfig(BaseModel):
    """浏览器配置"""
    headless: bool = True
    window_size: str = "1920x1080"
    user_agent: Optional[str] = None
    proxy: Optional[ProxyConfig] = None


class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = "sqlite"  # sqlite, mysql, postgresql, mongodb
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    url: Optional[str] = None


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    file: Optional[str] = None
    rotation: str = "1 day"
    retention: str = "30 days"


class StorageConfig(BaseModel):
    """存储配置"""
    output_dir: str = "./data"
    format: str = "json"  # json, csv, excel, txt
    filename: str = "crawled_data"


class AntiCrawlerConfig(BaseModel):
    """反爬虫配置"""
    enabled: bool = True
    random_delay: bool = True
    delay_range: tuple = (1, 3)  # 延迟范围（秒）
    rotate_user_agents: bool = True
    user_agents: List[str] = Field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ])
    use_proxy_pool: bool = False
    proxy_pool_url: Optional[str] = None


class CrawlerConfig(BaseModel):
    """爬虫基础配置"""
    timeout: int = 30
    retries: int = 3
    retry_delay: int = 1
    max_concurrent: int = 5
    headers: Dict[str, str] = Field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })


class Settings(BaseSettings):
    """应用设置"""
    # 基础配置
    app_name: str = "Boniu Crawler"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # 爬虫配置
    crawler: CrawlerConfig = CrawlerConfig()
    
    # 浏览器配置
    browser: BrowserConfig = BrowserConfig()
    
    # 数据库配置
    database: DatabaseConfig = DatabaseConfig()
    
    # 日志配置
    logging: LoggingConfig = LoggingConfig()
    
    # 存储配置
    storage: StorageConfig = StorageConfig()
    
    # 反爬虫配置
    anti_crawler: AntiCrawlerConfig = AntiCrawlerConfig()
    
    # 代理配置
    proxy: ProxyConfig = ProxyConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Union[str, int, float, bool, None]:
            """解析环境变量"""
            if field_name in ["debug", "anti_crawler__enabled", "proxy__enabled", "browser__headless"]:
                return raw_val.lower() in ("true", "1", "yes", "on")
            elif field_name in ["timeout", "retries", "retry_delay", "max_concurrent", "proxy__port", "database__port"]:
                return int(raw_val)
            elif field_name in ["delay_range"]:
                # 格式: "1,3" -> (1, 3)
                parts = raw_val.split(",")
                return (int(parts[0]), int(parts[1]))
            return raw_val


# 全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return settings


def reload_settings() -> Settings:
    """重新加载设置"""
    global settings
    settings = Settings()
    return settings
