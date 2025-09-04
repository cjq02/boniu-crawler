"""
工具函数模块
"""

import hashlib
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import csv
import pandas as pd
from config import get_settings


def clean_text(text: Optional[str]) -> str:
    """
    清理文本内容
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


def extract_number(text: Optional[str]) -> Optional[float]:
    """
    从文本中提取数字
    
    Args:
        text: 包含数字的文本
        
    Returns:
        提取的数字，如果没有找到返回None
    """
    if not text:
        return None
    match = re.search(r'\d+(\.\d+)?', text)
    return float(match.group()) if match else None


def extract_url(text: Optional[str]) -> Optional[str]:
    """
    从文本中提取URL
    
    Args:
        text: 包含URL的文本
        
    Returns:
        提取的URL，如果没有找到返回None
    """
    if not text:
        return None
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    return match.group() if match else None


def is_valid_url(url: str) -> bool:
    """
    验证URL格式是否有效
    
    Args:
        url: 要验证的URL
        
    Returns:
        是否有效
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def generate_hash(text: str) -> str:
    """
    生成文本的MD5哈希值
    
    Args:
        text: 要哈希的文本
        
    Returns:
        MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


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
    settings = get_settings()
    return random.choice(settings.anti_crawler.user_agents)


def ensure_dir(path: Union[str, Path]) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def generate_filename(prefix: str = "data", extension: str = "json") -> str:
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        extension: 文件扩展名
        
    Returns:
        生成的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_data(data: Any, filename: str, output_dir: Optional[str] = None) -> str:
    """
    保存数据到文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.storage.output_dir
    
    ensure_dir(output_dir)
    file_path = Path(output_dir) / filename
    
    if filename.endswith('.json'):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif filename.endswith('.csv'):
        if isinstance(data, list) and data:
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8')
        else:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
    elif filename.endswith('.txt'):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(data))
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(data))
    
    return str(file_path)


def load_data(filename: str, output_dir: Optional[str] = None) -> Any:
    """
    从文件加载数据
    
    Args:
        filename: 文件名
        output_dir: 输出目录
        
    Returns:
        加载的数据
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.storage.output_dir
    
    file_path = Path(output_dir) / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    if filename.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif filename.endswith('.csv'):
        return pd.read_csv(file_path, encoding='utf-8').to_dict('records')
    elif filename.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分块
    
    Args:
        lst: 要分块的列表
        chunk_size: 每块的大小
        
    Returns:
        分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key: Optional[str] = None) -> List[Any]:
    """
    去除列表中的重复项
    
    Args:
        lst: 要去重的列表
        key: 如果是字典列表，指定用于去重的键
        
    Returns:
        去重后的列表
    """
    if key and lst and isinstance(lst[0], dict):
        seen = set()
        return [item for item in lst if not (item[key] in seen or seen.add(item[key]))]
    else:
        return list(dict.fromkeys(lst))


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


def measure_time(func):
    """
    测量函数执行时间的装饰器
    
    Args:
        func: 要测量的函数
        
    Returns:
        装饰后的函数
    """
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
    def decorator(func):
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


def extract_links_from_html(html: str, base_url: str = "") -> List[str]:
    """
    从HTML中提取链接
    
    Args:
        html: HTML内容
        base_url: 基础URL
        
    Returns:
        提取的链接列表
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http'):
            links.append(href)
        elif href.startswith('/'):
            links.append(base_url + href)
    
    return remove_duplicates(links)


def extract_json_from_html(html: str, script_selector: str = 'script[type="application/json"]') -> Optional[Dict]:
    """
    从HTML中提取JSON数据
    
    Args:
        html: HTML内容
        script_selector: 脚本选择器
        
    Returns:
        提取的JSON数据
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.select_one(script_selector)
    
    if script and script.string:
        try:
            return json.loads(script.string)
        except json.JSONDecodeError:
            return None
    
    return None


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


# 导出主要函数
__all__ = [
    "clean_text",
    "extract_number", 
    "extract_url",
    "is_valid_url",
    "generate_hash",
    "random_delay",
    "get_random_user_agent",
    "ensure_dir",
    "generate_filename",
    "save_data",
    "load_data",
    "chunk_list",
    "remove_duplicates",
    "format_datetime",
    "measure_time",
    "retry",
    "extract_links_from_html",
    "extract_json_from_html",
    "random_string",
]
