"""博牛站点爬虫实现"""

import os
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import logging
import pymysql

from ...core.requests_impl import RequestsCrawler
from ...utils.parser import clean_text, extract_number
from ...utils.http import format_datetime
from ...utils.db import get_db_config, connect, fetch_all, executemany
from ...utils.image_downloader import ImageDownloader


def _extract_text(result: Any) -> Optional[str]:
    """兼容 CrawlResult / dict / str"""
    try:
        if hasattr(result, 'data') and result.data:
            return result.data
        if isinstance(result, dict) and 'data' in result:
            return result['data']
        if isinstance(result, str):
            return result
        return None
    except Exception:
        return None


class BoniuCrawler(RequestsCrawler):
    """博牛社区爬虫"""
    
    # 配置常量
    DEFAULT_MAX_PAGES = 2
    DEFAULT_DELAY_SECONDS = 1.0
    # DEFAULT_IMG_SAVE_PATH = r"D:\me\epiboly\fuye\resource\img\boniu"
    DEFAULT_IMG_SAVE_PATH = r"D:\me\epiboly\fuye\projects\im.fuye.io\attachment\images\boniu"
    
    def __init__(self):
        super().__init__("boniu_crawler")
        # 初始化日志器
        if not self.logger:
            self.logger = logging.getLogger(self.name)
            if not self.logger.handlers:
                logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        self.base_url = "https://bbs.boniu123.cc"
        self.forum_url = "https://bbs.boniu123.cc/forum.php?mod=forumdisplay&fid=89&page=1"
        self._setup_headers()
        # DB 配置（可通过环境变量覆盖）
        self.db_cfg = get_db_config()
        self.table_name = "ims_mdkeji_im_boniu_forum_post"
        
        # 初始化图片下载器
        self.image_downloader = ImageDownloader(
            base_path=self.DEFAULT_IMG_SAVE_PATH,
            logger=self.logger
        )

    def _setup_headers(self):
        """设置博牛社区特定的请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _parse_view_count(self, view_text: str) -> int:
        """解析浏览数"""
        if not view_text:
            return 0
        if '万' in view_text:
            number = extract_number(view_text)
            return int(number * 10000) if number else 0
        return int(extract_number(view_text) or 0)

    def crawl_forum_posts(self) -> List[Dict[str, Any]]:
        """爬取论坛帖子列表"""
        if self.logger:
            self.logger.info(f"开始爬取论坛页面: {self.forum_url}")
        
        resp = self.crawl_url(self.forum_url)
        html = _extract_text(resp)
        if not html:
            if self.logger:
                self.logger.error("爬取论坛页面失败")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        posts: List[Dict[str, Any]] = []
        
        for row in soup.find_all('tr'):
            try:
                item = self._parse_post_row(row)
                if item:
                    posts.append(item)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"解析帖子行失败: {e}")
        
        if self.logger:
            self.logger.info(f"解析到 {len(posts)} 个帖子")
        
        return posts

    def _parse_post_row(self, row) -> Optional[Dict[str, Any]]:
        """解析帖子行数据"""
        # 标题与URL
        title_link = row.find('a', class_='s xst') or row.find('a', href=re.compile(r'thread-\d+'))
        if not title_link:
            return None
        
        title = clean_text(title_link.get_text())
        post_url = urljoin(self.base_url, title_link.get('href', ''))

        # 帖子ID
        post_id = None
        # 优先从tbody的id属性中提取
        tbody = row.find_parent('tbody')
        if tbody and tbody.get('id'):
            m = re.search(r'normalthread_(\d+)', tbody.get('id'))
            if m:
                post_id = m.group(1)
        
        # 如果没找到，从URL中提取
        if not post_id:
            m = re.search(r'thread-(\d+)', post_url)
            if m:
                post_id = m.group(1)
            # 从viewthread URL中提取tid
            if not post_id:
                m = re.search(r'tid=(\d+)', post_url)
                if m:
                    post_id = m.group(1)

        # 用户名
        username = None
        user_element = (
            row.select_one('td.by cite a')
            or row.select_one('td.by a[href*="space-uid"]')
            or row.find('a', href=re.compile(r'space-uid|uid=\d+'))
            or row.find('a', class_=re.compile(r'username|author'))
        )
        if user_element and user_element.get_text(strip=True):
            username = clean_text(user_element.get_text())
        if not username:
            username = "未知用户"

        # 头像
        avatar_url = None
        avatar_img = row.find('img', class_='author-avatar') or row.find('img', src=re.compile(r'avatar'))
        if avatar_img and avatar_img.get('src'):
            avatar_url = urljoin(self.base_url, avatar_img['src'])

        # 发帖时间
        publish_time = ""
        # 优先获取有title属性的span
        for span in row.find_all('span', title=True):
            t = span.get('title', '')
            if re.search(r'\d{4}-\d{1,2}-\d{1,2}', t):
                publish_time = t
                break
        
        # 如果没有找到title，则获取span的文本内容
        if not publish_time:
            for span in row.find_all('span'):
                text = clean_text(span.get_text())
                if re.search(r'\d{4}-\d{1,2}-\d{1,2}', text):
                    publish_time = text
                    break

        # 回复/浏览
        reply_count = 0
        reply_el = row.find('span', class_='replayNum')
        if reply_el:
            reply_count = int(extract_number(clean_text(reply_el.get_text())) or 0)
        
        view_count = 0
        view_el = row.find('span', class_='viewNum')
        if view_el:
            view_count = self._parse_view_count(clean_text(view_el.get_text()))

        # 图片（列表页不爬取图片，只爬取内容页的图片）
        images: List[str] = []

        # 分类
        category = ""
        for a in row.find_all('a'):
            text = clean_text(a.get_text())
            if text in ['游戏包网', '游戏API', '支付渠道', '广告营销', '云服务', '技术外包', '媒体渠道', '本地服务']:
                category = text
                break

        # 标识
        is_sticky = False
        # 检查置顶图片：static/image/common/pin_*.gif
        sticky_img = row.find('img', src=re.compile(r'static/image/common/pin_.*\.gif'))
        if sticky_img:
            is_sticky = True
            
        # 跳过置顶帖子
        if is_sticky:
            return None
            
        is_essence = bool(row.find('img', alt=re.compile(r'精华|essence|hot')))

        return {
            'id': post_id,
            'title': title,
            'url': post_url,
            'username': username,
            'avatar_url': avatar_url,
            'publish_time': publish_time,
            'reply_count': reply_count,
            'view_count': view_count,
            'images': images,
            'category': category,
            'is_sticky': is_sticky,
            'is_essence': is_essence,
            'crawl_time': format_datetime(),
            'content': '',  # 初始为空，后续通过详情页获取
        }

    def _fetch_post_content(self, post_url: str) -> tuple[str, List[str]]:
        """获取帖子详情页内容和图片
        
        Returns:
            tuple: (content, images) - 内容文本和图片URL列表
        """
        try:
            if self.logger:
                self.logger.debug(f"获取帖子内容: {post_url}")
            
            resp = self.crawl_url(post_url)
            html = _extract_text(resp)
            if not html:
                return "", []
            
            # 调试：保存内容页HTML（仅第一个帖子）
            if self.logger and not hasattr(self, '_debug_saved'):
                try:
                    import os
                    debug_dir = "data/debug"
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(f"{debug_dir}/content_page.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    self.logger.info(f"调试：已保存内容页HTML到 {debug_dir}/content_page.html")
                    self._debug_saved = True
                except Exception as e:
                    self.logger.warning(f"保存调试HTML失败: {e}")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试多种选择器获取帖子内容（博牛论坛特定）
            content_selectors = [
                'div.t_f',  # Discuz论坛常见的内容区域
                'div.t_fsz',  # Discuz论坛内容区域
                'div.postmessage',  # 帖子消息区域
                'div#postmessage',  # ID选择器
                'div.content',  # 通用内容区域
                'div.message',  # 消息区域
                'div.post_content',  # 帖子内容区域
                'div.thread_content',  # 线程内容区域
                'div[id*="postmessage"]',  # 包含postmessage的ID
                'div[class*="postmessage"]',  # 包含postmessage的class
                'td.t_f',  # 表格中的内容区域
                'td[id*="postmessage"]',  # 表格中的postmessage
            ]
            
            content = ""
            content_element = None
            for selector in content_selectors:
                content_el = soup.select_one(selector)
                if content_el:
                    # 移除脚本和样式标签
                    for script in content_el(["script", "style"]):
                        script.decompose()
                    content = clean_text(content_el.get_text())
                    if content:
                        content_element = content_el
                        if self.logger:
                            self.logger.debug(f"找到内容区域: {selector}")
                        break
            
            # 从内容区域提取图片
            images: List[str] = []
            if content_element:
                # 查找所有图片标签
                all_imgs = content_element.find_all('img', src=True)
                if self.logger:
                    self.logger.debug(f"内容区域找到 {len(all_imgs)} 个图片标签")
                
                for img in all_imgs:
                    # 博牛论坛特殊处理：优先获取zoomfile或file属性
                    img_url = None
                    
                    # 检查zoomfile属性（博牛论坛的真实图片URL）
                    if img.get('zoomfile'):
                        img_url = img.get('zoomfile')
                        if self.logger:
                            self.logger.debug(f"找到zoomfile图片: {img_url}")
                    # 检查file属性（备用真实图片URL）
                    elif img.get('file'):
                        img_url = img.get('file')
                        if self.logger:
                            self.logger.debug(f"找到file图片: {img_url}")
                    # 最后检查src属性
                    elif img.get('src'):
                        img_src = img.get('src')
                        if self.logger:
                            self.logger.debug(f"检查src图片: {img_src}")
                        
                        # 过滤掉无效图片
                        invalid_patterns = [
                            r'none\.gif',  # 占位图片
                            r'blank\.gif',  # 空白图片
                            r'loading\.gif',  # 加载图片
                            r'spacer\.gif',  # 间距图片
                            r'pixel\.gif',  # 像素图片
                            r'1x1\.gif',  # 1x1像素图片
                            r'clear\.gif',  # 清除图片
                            r'static/image/common/',  # 通用静态图片
                            r'static/image/diy/',  # DIY图片
                            r'static/image/',  # 静态图片
                        ]
                        
                        # 检查是否为无效图片
                        is_invalid = any(re.search(pattern, img_src, re.I) for pattern in invalid_patterns)
                        if is_invalid:
                            if self.logger:
                                self.logger.debug(f"跳过无效图片: {img_src}")
                            continue
                        
                        # 检查是否为有效的内容图片
                        valid_patterns = [
                            r'attachment/',  # 附件图片
                            r'data/attachment/',  # 数据附件
                            r'uploads/',  # 上传图片
                            r'images/',  # 图片目录
                            r'\.jpg$|\.jpeg$|\.png$|\.gif$|\.webp$',  # 图片文件扩展名
                        ]
                        
                        is_valid = any(re.search(pattern, img_src, re.I) for pattern in valid_patterns)
                        if is_valid:
                            img_url = img_src
                        else:
                            if self.logger:
                                self.logger.debug(f"跳过非内容图片: {img_src}")
                            continue
                    
                    # 处理找到的图片URL
                    if img_url:
                        # 如果是相对路径，转换为绝对路径
                        if not img_url.startswith('http'):
                            img_url = urljoin(self.base_url, img_url)
                        
                        # 避免重复添加
                        if img_url not in images:
                            images.append(img_url)
                            if self.logger:
                                self.logger.debug(f"添加图片: {img_url}")
            
            # 限制长度避免过长
            content = content[:65535] if content else ""
            return content, images
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"获取帖子内容失败 {post_url}: {e}")
            return "", []


    # ========= 分页爬取 + 去重 + 入库 =========

    def _get_existing_ids(self) -> set:
        """读取库中已存在的帖子ID集合"""
        if self.logger:
            self.logger.info(f"查询已存在ID: 表={self.table_name}")
        rows = fetch_all(f"SELECT forum_post_id FROM `{self.table_name}` WHERE forum_post_id IS NOT NULL")
        existing = {str(row['forum_post_id']) for row in rows}
        if self.logger:
            self.logger.info(f"已存在ID数量: {len(existing)}")
        return existing

    def _insert_posts(self, posts: List[Dict[str, Any]]) -> int:
        """批量插入/更新帖子"""
        if not posts:
            return 0
        sql = f"""
        INSERT INTO `{self.table_name}` (
          `forum_post_id`,`title`,`url`,`user_id`,`username`,`avatar_url`,
          `publish_time`,`reply_count`,`view_count`,`images`,`category`,
          `is_sticky`,`is_essence`,`crawl_time`,`type`,`is_crawl`,`content`,`uniacid`
        ) VALUES (
          %s,%s,%s,%s,%s,%s,
          %s,%s,%s,%s,%s,
          %s,%s,%s,%s,%s,%s,%s
        )
        ON DUPLICATE KEY UPDATE
          `title`=VALUES(`title`),
          `url`=VALUES(`url`),
          `user_id`=VALUES(`user_id`),
          `username`=VALUES(`username`),
          `avatar_url`=VALUES(`avatar_url`),
          `publish_time`=VALUES(`publish_time`),
          `reply_count`=VALUES(`reply_count`),
          `view_count`=VALUES(`view_count`),
          `images`=VALUES(`images`),
          `category`=VALUES(`category`),
          `is_sticky`=VALUES(`is_sticky`),
          `is_essence`=VALUES(`is_essence`),
          `crawl_time`=VALUES(`crawl_time`),
          `type`=VALUES(`type`),
          `is_crawl`=VALUES(`is_crawl`),
          `content`=VALUES(`content`),
          `uniacid`=VALUES(`uniacid`);
        """
        rows = []
        for p in posts:
            images_json = json.dumps(p.get('images') or [], ensure_ascii=False)
            rows.append(
                (
                    int(p.get('id') or 0),
                    (p.get('title') or '')[:255],
                    (p.get('url') or '')[:512],
                    None if p.get('user_id') in (None, '') else int(p.get('user_id')),
                    (p.get('username') or '')[:100],
                    (p.get('avatar_url') or None),
                    p.get('publish_time') or None,
                    int(p.get('reply_count') or 0),
                    int(p.get('view_count') or 0),
                    images_json,
                    (p.get('category') or '')[:100],
                    1 if p.get('is_sticky') else 0,
                    1 if p.get('is_essence') else 0,
                    p.get('crawl_time') or None,
                    (p.get('type') or '')[:50],
                    1 if p.get('is_crawl', 1) else 0,
                    (p.get('content') or '')[:65535],  # TEXT字段最大长度
                    1,  # uniacid=1
                )
            )
        if rows:
            if self.logger:
                self.logger.info(f"批量入库: 记录数={len(rows)} 表={self.table_name}")
            affected = executemany(sql, rows)
            if self.logger:
                self.logger.info(f"入库完成: 受影响行数≈{affected}")
            return len(rows)
        return 0

    def crawl_paginated_and_store(self, max_pages: int = None, delay_seconds: float = None) -> None:
        """分页爬取；若当前页所有帖子已存在则停止；最后插入新数据"""
        # 使用默认值
        max_pages = max_pages or self.DEFAULT_MAX_PAGES
        delay_seconds = delay_seconds or self.DEFAULT_DELAY_SECONDS
        
        if self.logger:
            self.logger.info(f"开始分页爬取并入库 (最大页数: {max_pages}, 延迟: {delay_seconds}秒)")

        existing_ids = self._get_existing_ids()
        if self.logger:
            self.logger.info(f"数据库已有 {len(existing_ids)} 条")

        all_new_posts: List[Dict[str, Any]] = []

        page = 1
        while page <= max_pages:
            # 构造分页 URL
            self.forum_url = f"https://bbs.boniu123.cc/forum.php?mod=forumdisplay&fid=89&page={page}"
            if self.logger:
                self.logger.info(f"爬取第 {page} 页: {self.forum_url}")

            posts = self.crawl_forum_posts()
            if not posts:
                if self.logger:
                    self.logger.info("该页无数据，停止")
                break

            ids_on_page = {str(p.get('id')) for p in posts if p.get('id')}
            if self.logger:
                self.logger.info(f"第 {page} 页帖子数={len(posts)}，可识别ID数={len(ids_on_page)}")
            new_ids = ids_on_page - existing_ids

            if not new_ids:
                if self.logger:
                    self.logger.info("该页全部 ID 已存在，停止继续翻页")
                break

            new_posts = [p for p in posts if str(p.get('id')) in new_ids]
            if self.logger:
                self.logger.info(f"第 {page} 页新增 {len(new_posts)} 条")

            # 为新帖子获取内容
            if self.logger:
                self.logger.info(f"开始获取 {len(new_posts)} 个新帖子的详细内容...")
            
            for i, post in enumerate(new_posts, 1):
                if post.get('url'):
                    if self.logger:
                        self.logger.info(f"获取内容 [{i}/{len(new_posts)}]: 帖子ID={post.get('id')}")
                    
                    content, images = self._fetch_post_content(post['url'])
                    post['content'] = content
                    
                    # 下载图片到本地
                    if images:
                        local_images = self.image_downloader.download_images(images)
                        post['images'] = local_images  # 更新为本地图片路径
                    else:
                        post['images'] = []  # 没有图片
                    
                    if self.logger:
                        if content:
                            self.logger.info(f"✓ 成功获取内容: {len(content)} 字符")
                        else:
                            self.logger.warning(f"✗ 未能获取到内容")

            all_new_posts.extend(new_posts)
            existing_ids.update(ids_on_page)

            page += 1
            if delay_seconds and delay_seconds > 0:
                try:
                    import time
                    time.sleep(delay_seconds)
                except Exception:
                    pass

        if all_new_posts:
            inserted = self._insert_posts(all_new_posts)
            if self.logger:
                self.logger.info(f"已插入/更新 {inserted} 条")
        else:
            if self.logger:
                self.logger.info("无新增数据，无需入库")

    def run(self) -> None:
        """运行博牛爬虫的主要逻辑（分页入库）"""
        self.crawl_paginated_and_store()
