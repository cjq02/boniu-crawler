"""
基于requests的爬虫类
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from .base import BaseCrawler, CrawlResult
from ..config.settings import get_settings
from ..utils.parser import clean_text, extract_links_from_html, extract_json_from_html


class RequestsCrawler(BaseCrawler):
    """基于requests的爬虫类"""
    
    def __init__(self, name: str = "requests_crawler"):
        super().__init__(name)
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """设置会话配置"""
        # 设置默认请求头
        self.session.headers.update(self.settings.crawler.headers)
        
        # 设置代理
        if self.settings.proxy.enabled and self.settings.proxy.host:
            proxy_url = f"http://{self.settings.proxy.host}:{self.settings.proxy.port}"
            if self.settings.proxy.username and self.settings.proxy.password:
                proxy_url = f"http://{self.settings.proxy.username}:{self.settings.proxy.password}@{self.settings.proxy.host}:{self.settings.proxy.port}"
            
            self.session.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
        
        # 设置超时
        self.session.timeout = self.settings.crawler.timeout
    
    def crawl_url(self, url: str, **kwargs) -> CrawlResult:
        """
        爬取单个URL
        
        Args:
            url: 要爬取的URL
            **kwargs: 其他参数
            
        Returns:
            爬取结果
        """
        if self.logger:
            self.logger.info(f"开始爬取: {url}")
        
        # 应用反爬虫策略
        self.apply_anti_crawler_strategy()
        
        # 更新请求头
        headers = kwargs.get('headers', {})
        if self.settings.anti_crawler.rotate_user_agents:
            headers['User-Agent'] = self.ua.random
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=kwargs.get('timeout', self.settings.crawler.timeout),
                allow_redirects=kwargs.get('allow_redirects', True),
                verify=kwargs.get('verify', True),
            )
            
            # 验证响应
            self.validate_response(response, url)
            
            # 解析数据
            data = self.parse_data(response, url)
            
            self.stats.success += 1
            if self.logger:
                self.logger.info(f"爬取成功: {url}")
            
            return CrawlResult(
                url=url,
                data=data,
                status_code=response.status_code,
            )
            
        except Exception as e:
            self.stats.failed += 1
            if self.logger:
                self.logger.error(f"爬取失败 {url}: {str(e)}")
            
            return CrawlResult(
                url=url,
                data=None,
                error=str(e),
            )
    
    def crawl_html(self, url: str, selectors: Optional[Dict[str, str]] = None, **kwargs) -> CrawlResult:
        """
        爬取HTML页面并提取数据
        
        Args:
            url: 要爬取的URL
            selectors: CSS选择器字典
            **kwargs: 其他参数
            
        Returns:
            爬取结果
        """
        result = self.crawl_url(url, **kwargs)
        
        if result.error:
            return result
        
        # 解析HTML
        soup = BeautifulSoup(result.data, 'html.parser')
        
        # 提取数据
        extracted_data = {}
        if selectors:
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if len(elements) == 1:
                    extracted_data[key] = clean_text(elements[0].get_text())
                else:
                    extracted_data[key] = [clean_text(el.get_text()) for el in elements]
        
        # 添加页面基本信息
        extracted_data['title'] = soup.title.get_text() if soup.title else ""
        extracted_data['url'] = url
        extracted_data['links'] = extract_links_from_html(str(soup), url)
        
        result.data = extracted_data
        return result
    
    def crawl_api(self, url: str, method: str = "GET", data: Optional[Dict] = None, **kwargs) -> CrawlResult:
        """
        爬取API数据
        
        Args:
            url: API URL
            method: HTTP方法
            data: 请求数据
            **kwargs: 其他参数
            
        Returns:
            爬取结果
        """
        if self.logger:
            self.logger.info(f"开始爬取API: {url}")
        
        # 应用反爬虫策略
        self.apply_anti_crawler_strategy()
        
        # 设置API请求头
        headers = kwargs.get('headers', {})
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        if self.settings.anti_crawler.rotate_user_agents:
            headers['User-Agent'] = self.ua.random
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, **kwargs)
            else:
                response = self.session.request(method, url, json=data, headers=headers, **kwargs)
            
            # 验证响应
            self.validate_response(response, url)
            
            # 解析JSON数据
            try:
                data = response.json()
            except ValueError:
                data = response.text
            
            self.stats.success += 1
            if self.logger:
                self.logger.info(f"API爬取成功: {url}")
            
            return CrawlResult(
                url=url,
                data=data,
                status_code=response.status_code,
            )
            
        except Exception as e:
            self.stats.failed += 1
            if self.logger:
                self.logger.error(f"API爬取失败 {url}: {str(e)}")
            
            return CrawlResult(
                url=url,
                data=None,
                error=str(e),
            )
    
    def batch_crawl(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """
        批量爬取URLs
        
        Args:
            urls: URL列表
            **kwargs: 其他参数
            
        Returns:
            爬取结果列表
        """
        self.stats.total = len(urls)
        if self.logger:
            self.logger.info(f"开始批量爬取 {len(urls)} 个URL")
        
        results = []
        for i, url in enumerate(urls):
            if not self.is_running:
                break
            
            result = self.crawl_url(url, **kwargs)
            results.append(result)
            
            # 添加延迟
            if i < len(urls) - 1:
                time.sleep(self.settings.crawler.retry_delay)
        
        success_count = len([r for r in results if not r.error])
        failed_count = len([r for r in results if r.error])
        if self.logger:
            self.logger.info(f"批量爬取完成: 成功 {success_count}, 失败 {failed_count}")
        
        return results
    
    def crawl_paginated(self, base_url: str, page_config: Dict[str, Any], **kwargs) -> List[Any]:
        """
        爬取分页数据
        
        Args:
            base_url: 基础URL
            page_config: 分页配置
            **kwargs: 其他参数
            
        Returns:
            所有页面的数据
        """
        start_page = page_config.get('start_page', 1)
        max_pages = page_config.get('max_pages', 10)
        page_param = page_config.get('page_param', 'page')
        data_selector = page_config.get('data_selector')
        
        all_data = []
        current_page = start_page
        
        while current_page <= max_pages and self.is_running:
            # 构建页面URL
            page_url = f"{base_url}?{page_param}={current_page}"
            if '?' in base_url:
                page_url = f"{base_url}&{page_param}={current_page}"
            
            if self.logger:
                self.logger.info(f"爬取第 {current_page} 页: {page_url}")
            
            # 爬取页面
            if data_selector:
                result = self.crawl_html(page_url, {data_selector: data_selector}, **kwargs)
            else:
                result = self.crawl_url(page_url, **kwargs)
            
            if result.error:
                if self.logger:
                    self.logger.error(f"爬取第 {current_page} 页失败: {result.error}")
                break
            
            # 提取数据
            if data_selector and isinstance(result.data, dict):
                page_data = result.data.get(data_selector, [])
                if isinstance(page_data, list):
                    all_data.extend(page_data)
                else:
                    all_data.append(page_data)
            else:
                all_data.append(result.data)
            
            current_page += 1
            
            # 页面间延迟
            if current_page <= max_pages:
                time.sleep(self.settings.crawler.retry_delay)
        
        return all_data
    
    def validate_response(self, response: requests.Response, url: str) -> bool:
        """
        验证响应
        
        Args:
            response: 响应对象
            url: 请求的URL
            
        Returns:
            是否有效
        """
        super().validate_response(response, url)
        
        if response.status_code >= 400:
            raise requests.HTTPError(f"HTTP错误: {response.status_code} {response.reason}")
        
        return True
    
    def parse_data(self, response: requests.Response, url: str) -> Any:
        """
        解析响应数据
        
        Args:
            response: 响应对象
            url: 请求的URL
            
        Returns:
            解析后的数据
        """
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        elif 'text/html' in content_type:
            return response.text
        else:
            return response.text
    
    def run(self) -> None:
        """运行爬虫的主要逻辑"""
        # 子类需要实现具体的爬取逻辑
        pass
    
    def __del__(self):
        """析构函数，关闭会话"""
        if hasattr(self, 'session'):
            self.session.close()
