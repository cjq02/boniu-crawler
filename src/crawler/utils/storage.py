"""存储工具模块"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List
import pandas as pd

from ..config.settings import get_settings


def ensure_dir(path: Path) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """
    path.mkdir(parents=True, exist_ok=True)


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
    
    output_path = Path(output_dir)
    ensure_dir(output_path)
    file_path = output_path / filename
    
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
