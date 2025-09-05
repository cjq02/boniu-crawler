"""HTTP工具模块"""

import hashlib
import time
from datetime import datetime
from typing import Any, Callable, Optional
from functools import wraps


def generate_hash(text: str) -> str:
    """
    生成文本的MD5哈希值
    
    Args:
        text: 要哈希的文本
        
    Returns:
        MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象，如果为None则使用当前时间
        format_str: 格式化字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def measure_time(func: Callable) -> Callable:
    """
    测量函数执行时间的装饰器
    
    Args:
        func: 要测量的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.2f}秒")
        return result
    return wrapper


def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 延迟时间的倍数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception
            return None
        return wrapper
    return decorator
