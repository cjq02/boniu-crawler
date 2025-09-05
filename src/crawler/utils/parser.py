"""解析工具模块"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json


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


def extract_links_from_html(html: str, base_url: str = "") -> List[str]:
    """
    从HTML中提取链接
    
    Args:
        html: HTML内容
        base_url: 基础URL
        
    Returns:
        提取的链接列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http'):
            links.append(href)
        elif href.startswith('/'):
            links.append(base_url + href)
    
    return list(dict.fromkeys(links))  # 去重


def extract_json_from_html(html: str, script_selector: str = 'script[type="application/json"]') -> Optional[Dict]:
    """
    从HTML中提取JSON数据
    
    Args:
        html: HTML内容
        script_selector: 脚本选择器
        
    Returns:
        提取的JSON数据
    """
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.select_one(script_selector)
    
    if script and script.string:
        try:
            return json.loads(script.string)
        except json.JSONDecodeError:
            return None
    
    return None
