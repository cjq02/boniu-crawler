"""反检测工具模块"""

import random
import time
from typing import List
from fake_useragent import UserAgent

from ..config.settings import get_settings


def random_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> float:
    """
    生成随机延迟时间
    
    Args:
        min_delay: 最小延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        
    Returns:
        随机延迟时间
    """
    return random.uniform(min_delay, max_delay)


def get_random_user_agent() -> str:
    """
    获取随机User-Agent
    
    Returns:
        随机User-Agent字符串
    """
    try:
        ua = UserAgent()
        return ua.random
    except:
        # 如果fake_useragent失败，使用默认的User-Agent列表
        default_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        return random.choice(default_user_agents)


def random_string(length: int = 8) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        随机字符串
    """
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def setup_session(session, settings=None):
    """
    设置会话的反检测配置
    
    Args:
        session: requests.Session对象
        settings: 配置对象
    """
    if settings is None:
        settings = get_settings()
    
    # 设置默认请求头
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # 设置代理
    if settings.proxy.enabled and settings.proxy.host:
        proxy_url = f"http://{settings.proxy.host}:{settings.proxy.port}"
        if settings.proxy.username and settings.proxy.password:
            proxy_url = f"http://{settings.proxy.username}:{settings.proxy.password}@{settings.proxy.host}:{settings.proxy.port}"
        
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
    
    # 设置超时
    session.timeout = settings.crawler.timeout
