"""图片下载工具模块"""

import os
import requests
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse
from pathlib import Path


class ImageDownloader:
    """图片下载器"""
    
    def __init__(self, base_path: str, logger=None):
        """
        初始化图片下载器
        
        Args:
            base_path: 图片保存的基础路径
            logger: 日志器
        """
        self.base_path = base_path
        self.logger = logger
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _get_relative_path(self, local_path: str) -> str:
        """
        将绝对路径转换为相对路径格式
        
        Args:
            local_path: 绝对路径
            
        Returns:
            相对路径格式，如：images/boniu/2025/9/11/image.jpg
        """
        try:
            # 获取相对于base_path的路径
            rel_path = os.path.relpath(local_path, self.base_path)
            # 转换为Unix风格路径并添加前缀
            unix_path = rel_path.replace(os.sep, '/')
            return f"images/boniu/{unix_path}"
        except ValueError:
            # 如果路径不在base_path下，直接使用文件名
            filename = os.path.basename(local_path)
            today = datetime.now().strftime("%Y/%m/%d")
            return f"images/boniu/{today}/{filename}"
    
    def download_image(self, img_url: str, save_path: str = None) -> Optional[str]:
        """
        下载单张图片并保存到本地
        
        Args:
            img_url: 图片URL
            save_path: 保存路径，如果为None则使用默认路径
            
        Returns:
            相对路径格式的图片路径（如：images/boniu/2025/9/11/image.jpg），如果下载失败返回None
        """
        try:
            if not save_path:
                # 使用默认路径并按日期创建文件夹
                today = datetime.now().strftime("%Y/%m/%d")
                save_path = os.path.join(self.base_path, today)
            
            # 确保目录存在
            os.makedirs(save_path, exist_ok=True)
            
            # 获取图片文件名
            parsed_url = urlparse(img_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                # 如果没有文件名或扩展名，生成一个
                filename = f"image_{datetime.now().strftime('%H%M%S_%f')}.jpg"
            
            local_path = os.path.join(save_path, filename)
            
            # 检查文件是否已存在
            if os.path.exists(local_path):
                if self.logger:
                    self.logger.debug(f"图片已存在，跳过下载: {local_path}")
                # 返回相对路径格式
                return self._get_relative_path(local_path)
            
            # 下载图片
            if self.logger:
                self.logger.debug(f"下载图片: {img_url} -> {local_path}")
            
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            if self.logger:
                self.logger.debug(f"图片保存成功: {local_path}")
            
            # 返回相对路径格式
            return self._get_relative_path(local_path)
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"图片下载失败 {img_url}: {e}")
            return None
    
    def download_images(self, img_urls: List[str], save_path: str = None) -> List[str]:
        """
        批量下载图片并保存到本地
        
        Args:
            img_urls: 图片URL列表
            save_path: 保存路径，如果为None则使用默认路径
            
        Returns:
            相对路径格式的图片路径列表（如：images/boniu/2025/9/11/image.jpg）
        """
        local_images = []
        
        if not img_urls:
            return local_images
        
        if self.logger:
            self.logger.info(f"开始批量下载 {len(img_urls)} 张图片...")
        
        for i, img_url in enumerate(img_urls, 1):
            if self.logger:
                self.logger.debug(f"下载进度 [{i}/{len(img_urls)}]: {img_url}")
            
            local_path = self.download_image(img_url, save_path)
            if local_path:
                local_images.append(local_path)
        
        if self.logger:
            self.logger.info(f"批量下载完成: 成功 {len(local_images)}/{len(img_urls)} 张")
        
        return local_images
    
    def set_base_path(self, base_path: str):
        """设置基础保存路径"""
        self.base_path = base_path
    
    def get_today_path(self) -> str:
        """获取今天的保存路径（相对路径格式）"""
        today = datetime.now().strftime("%Y/%m/%d")
        return f"images/boniu/{today}"
    
    def __del__(self):
        """析构函数，关闭会话"""
        if hasattr(self, 'session'):
            self.session.close()
