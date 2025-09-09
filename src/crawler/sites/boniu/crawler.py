"""博牛站点爬虫实现"""

import os
import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from ...core.requests_impl import RequestsCrawler
from ...utils.parser import clean_text
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
    DEFAULT_DELAY_SECONDS = 3.0  # 增加延迟时间
    DEFAULT_FIDS = [89, 734]
    
    def __init__(self):
        super().__init__("boniu_crawler")
        # 初始化日志器
        if not self.logger:
            self.logger = logging.getLogger(self.name)
            if not self.logger.handlers:
                logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        # 文件日志：logs/YYYY/MM/DD.log
        try:
            logs_root = os.path.join(os.getcwd(), 'logs')
            year_str = datetime.now().strftime('%Y')
            month_str = datetime.now().strftime('%m')
            day_str = datetime.now().strftime('%d')
            year_dir = os.path.join(logs_root, year_str)
            month_dir = os.path.join(year_dir, month_str)
            os.makedirs(month_dir, exist_ok=True)
            log_file = os.path.join(month_dir, f'{day_str}.log')
            has_file_handler = any(getattr(h, 'baseFilename', None) == log_file for h in self.logger.handlers)
            if not has_file_handler:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
                self.logger.addHandler(file_handler)
        except Exception:
            pass
        self.base_url = "https://bbs.boniu123.cc"
        self.forum_url = "https://bbs.boniu123.cc/forum.php?mod=forumdisplay&fid=89&page=1"
        self.fids = self.DEFAULT_FIDS[:]
        self._setup_headers()
        # DB 配置（可通过环境变量覆盖）
        self.db_cfg = get_db_config()
        self.table_name = "ims_mdkeji_im_boniu_forum_post"
        
        # 初始化图片下载器
        # 通过环境变量控制图片基础路径；未提供时退回到项目目录下 images/boniu
        img_base_path = os.getenv("BONIU_IMG_BASE_PATH") or os.path.join(os.getcwd(), "images", "boniu")
        self.image_downloader = ImageDownloader(
            base_path=img_base_path,
            logger=self.logger
        )

    def _setup_headers(self):
        """设置博牛社区特定的请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            # 去掉 br，避免生产环境未解码时保存乱码
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.base_url,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })


    def crawl_forum_posts(self) -> List[Dict[str, Any]]:
        """爬取论坛帖子列表"""
        if self.logger:
            self.logger.info(f"开始爬取论坛页面: {self.forum_url}")
        
        # 先访问主页，模拟真实用户行为（含重试）
        import time
        homepage_ok = False
        for i in range(2):
            try:
                if self.logger:
                    self.logger.info("先访问主页建立会话...")
                resp_home = self.crawl_url(self.base_url)
                if _extract_text(resp_home):
                    homepage_ok = True
                    break
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"访问主页失败(第{i+1}次): {e}")
            time.sleep(1)
        
        # 添加重试机制
        max_retries = 3
        html = None
        for attempt in range(max_retries):
            try:
                resp = self.crawl_url(self.forum_url)
                html = _extract_text(resp)
                if html:
                    break
                else:
                    if self.logger:
                        self.logger.warning(f"第 {attempt + 1} 次尝试获取HTML失败")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"第 {attempt + 1} 次爬取失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)

        # 列表页失败时，切换备用静态路径 forum-<fid>-1.html 再试
        if not html:
            try:
                fid_match = re.search(r'fid=(\d+)', self.forum_url)
                if fid_match:
                    alt_url = f"{self.base_url}/forum-{fid_match.group(1)}-1.html"
                    if self.logger:
                        self.logger.info(f"主URL获取失败，尝试备用URL: {alt_url}")
                    for attempt in range(max_retries):
                        try:
                            resp_alt = self.crawl_url(alt_url)
                            html = _extract_text(resp_alt)
                            if html:
                                break
                        except Exception as e:
                            if self.logger:
                                self.logger.warning(f"备用URL第 {attempt + 1} 次失败: {e}")
                        time.sleep(2)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"备用URL尝试异常: {e}")
        
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

        # 回复/浏览（不抓取，默认0）
        reply_count = 0
        view_count = 0

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

        # 从当前爬取的URL中提取fid参数值作为type
        type_value = ""
        if self.forum_url:
            match = re.search(r'fid=(\d+)', self.forum_url)
            if match:
                type_value = match.group(1)

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
            'fid': type_value,  # 存储fid值
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
            
            # 可选：如需调试可在此保存HTML
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试多种选择器获取帖子内容（博牛论坛特定）
            content_selectors = [
                'td.t_f[id^="postmessage_"]',
                '#postlist div[id^="post_"]:not([id$="_li"]) td.t_f',
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
                    # 先提取将被排除节点中的图片（如 ignore_js_op 内的附件图片）
                    try:
                        pre_images: List[str] = []
                        # 目标区域：class 为 ignore_js_op 或标签 <ignore_js_op>
                        pre_nodes = []
                        try:
                            pre_nodes.extend(content_el.select('.ignore_js_op'))
                        except Exception:
                            pass
                        try:
                            pre_nodes.extend(content_el.find_all(True, class_=re.compile(r'(?:^|\\s)ignore_js_op(?:\\s|$)')))
                        except Exception:
                            pass
                        try:
                            pre_nodes.extend(content_el.find_all('ignore_js_op'))
                        except Exception:
                            pass
                        for n in pre_nodes:
                            for img in n.find_all('img'):
                                img_url = None
                                if img.get('zoomfile'):
                                    img_url = img.get('zoomfile')
                                elif img.get('file'):
                                    img_url = img.get('file')
                                elif img.get('src'):
                                    img_url = img.get('src')
                                if img_url:
                                    if not img_url.startswith('http'):
                                        img_url = urljoin(self.base_url, img_url)
                                    if img_url not in pre_images:
                                        pre_images.append(img_url)

                    except Exception:
                        pre_images = []

                    # 先移除可能的附件容器与相关节点（Discuz 常见结构）
                    try:
                        attachment_selectors = [
                            'div.pattl', 'div.pattc', 'div.attach', 'div.attnm', 'p.attnm',
                            'dl.tattl', 'ul.attlist', 'div.attlist', 'table.attnm', 'span.attprice',
                            'div.mbm', 'div.mbn', 'div.mtm', 'span.xg1', 'em.xg1',
                            '.ignore_js_op',
                            'ignore_js_op'
                        ]
                        for sel in attachment_selectors:
                            for node in content_el.select(sel):
                                node.decompose()
                        # 兼容移除：通过 class 正则匹配 ignore_js_op（避免选择器遗漏）
                        for node in content_el.find_all(True, class_=re.compile(r'(?:^|\s)ignore_js_op(?:\s|$)')):
                            try:
                                node.decompose()
                            except Exception:
                                pass
                        # 兼容移除：通过标签名直接移除 <ignore_js_op>
                        for node in content_el.find_all('ignore_js_op'):
                            try:
                                node.decompose()
                            except Exception:
                                pass
                        # 根据文本关键字移除包含附件信息的节点
                        text_patterns = re.compile(r"下载附件|保存到相册|下载次数|\\.(?:png|jpg|jpeg|gif|webp)(?:\\s*\\([^)]+\\))?|上传\\s*$", re.I)
                        for txt in content_el.find_all(string=text_patterns):
                            parent = txt.parent
                            # 尽量删除包含该文本的一整块
                            container = parent.find_parent(["p", "div", "li", "td", "span"]) if parent else None
                            if container:
                                container.decompose()
                            elif parent:
                                parent.decompose()
                            else:
                                txt.extract()
                    except Exception:
                        pass
                    content = clean_text(content_el.get_text())
                    if content:
                        content_element = content_el
                        if self.logger:
                            self.logger.debug(f"找到内容区域: {selector}")
                        break
            
            # 保留内容原文（已做DOM级过滤）
            
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

            # 合并在 ignore_js_op 中预先提取到的图片
            try:
                for u in pre_images:
                    if u not in images:
                        images.append(u)
            except Exception:
                pass
                if self.logger:
                    self.logger.debug(f"添加图片: {img_url}")
            
            # 限制长度避免过长
            content = content[:65535] if content else ""
            return content, images
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"获取帖子内容失败 {post_url}: {e}")
            return "", []

    # 已移除：仅保留DOM级过滤后的内容


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

    def _insert_posts(self, posts: List[Dict[str, Any]], overwrite: bool = False) -> int:
        """批量插入/更新帖子"""
        if not posts:
            return 0
        sql = f"""
        INSERT INTO `{self.table_name}` (
          `forum_post_id`,`title`,`url`,`user_id`,`username`,`avatar_url`,
          `publish_time`,`reply_count`,`view_count`,`images`,`category`,
          `is_sticky`,`is_essence`,`crawl_time`,`fid`,`is_crawl`,`content`,`uniacid`
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
          `fid`=VALUES(`fid`),
          `is_crawl`=VALUES(`is_crawl`),
          `content`=VALUES(`content`),
          `uniacid`=VALUES(`uniacid`);
        """
        rows = []
        for p in posts:
            # 过滤掉无效或缺失的帖子ID，避免产生重复/脏数据
            try:
                pid = int(p.get('id') or 0)
            except Exception:
                pid = 0
            if pid <= 0:
                continue
            images_json = json.dumps(p.get('images') or [], ensure_ascii=False)
            if overwrite:
                # Overwrite 模式：执行 UPDATE，仅更新指定字段
                rows.append(
                    (
                        (p.get('title') or '')[:255],
                        (p.get('content') or '')[:65535],
                        images_json,
                        pid,
                    )
                )
            else:
                rows.append(
                    (
                        pid,
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
                        (p.get('fid') or '')[:50],
                        1 if p.get('is_crawl', 1) else 0,
                        (p.get('content') or '')[:65535],  # TEXT字段最大长度
                        1,  # uniacid=1
                    )
                )
        if rows:
            if self.logger:
                self.logger.info(f"批量入库: 记录数={len(rows)} 表={self.table_name}")
            if overwrite:
                update_sql = f"UPDATE `{self.table_name}` SET `title`=%s, `content`=%s, `images`=%s, `updated_at`=NOW() WHERE `forum_post_id`=%s"
                affected = executemany(update_sql, rows)
            else:
                affected = executemany(sql, rows)
            if self.logger:
                self.logger.info(f"入库完成: 受影响行数≈{affected}")
            return len(rows)
        return 0


    def crawl_paginated_and_store(self, max_pages: int = None, delay_seconds: float = None, overwrite: bool = False) -> None:
        """分页爬取；若当前页所有帖子已存在则停止；最后插入新数据
        
        Args:
            max_pages: 最大爬取页数
            delay_seconds: 延迟秒数
            overwrite: 是否覆盖已存在的记录
        """
        # 使用默认值
        max_pages = max_pages or self.DEFAULT_MAX_PAGES
        delay_seconds = delay_seconds or self.DEFAULT_DELAY_SECONDS
        
        if self.logger:
            self.logger.info(f"开始分页爬取并入库 (最大页数: {max_pages}, 延迟: {delay_seconds}秒, 覆盖模式: {overwrite})")

        existing_ids = set()
        if not overwrite:
            existing_ids = self._get_existing_ids()
            if self.logger:
                self.logger.info(f"数据库已有 {len(existing_ids)} 条")
        else:
            if self.logger:
                self.logger.info("覆盖模式：将处理所有帖子，包括已存在的记录")

        # 遍历多个 fid 抓取
        for fid in self.fids:
            page = 1
            while page <= max_pages:
                # 构造分页 URL（根据 fid 与页码）
                self.forum_url = f"https://bbs.boniu123.cc/forum.php?mod=forumdisplay&fid={fid}&page={page}"
                if self.logger:
                    self.logger.info(f"爬取(fid={fid}) 第 {page} 页: {self.forum_url}")

                posts = self.crawl_forum_posts()
                if not posts:
                    if self.logger:
                        self.logger.info("该页无数据，停止当前fid")
                    break

                ids_on_page = {str(p.get('id')) for p in posts if p.get('id')}
                if self.logger:
                    self.logger.info(f"(fid={fid}) 第 {page} 页帖子数={len(posts)}，可识别ID数={len(ids_on_page)}")
                
                # 根据覆盖模式决定处理哪些帖子
                if overwrite:
                    # 覆盖模式：处理所有帖子
                    posts_to_process = posts
                    if self.logger:
                        self.logger.info(f"(fid={fid}) 第 {page} 页覆盖模式：处理所有 {len(posts_to_process)} 条")
                else:
                    # 非覆盖模式：只处理新帖子
                    new_ids = ids_on_page - existing_ids
                    if not new_ids:
                        if self.logger:
                            self.logger.info("该页全部 ID 已存在，停止当前fid继续翻页")
                        break
                    posts_to_process = [p for p in posts if str(p.get('id')) in new_ids]
                    if self.logger:
                        self.logger.info(f"(fid={fid}) 第 {page} 页新增 {len(posts_to_process)} 条")

                # 为帖子获取内容
                if self.logger:
                    self.logger.info(f"开始获取 {len(posts_to_process)} 个帖子的详细内容...")
                
                for i, post in enumerate(posts_to_process, 1):
                    if post.get('url'):
                        if self.logger:
                            self.logger.info(f"获取内容 [{i}/{len(posts_to_process)}]: 帖子ID={post.get('id')}")
                        
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

                # 当前页入库：覆盖模式走 UPDATE，否则 INSERT/UPDATE
                if posts_to_process:
                    inserted = self._insert_posts(posts_to_process, overwrite=overwrite)
                    if self.logger:
                        self.logger.info(f"(fid={fid}) 第 {page} 页已插入/更新 {inserted} 条")
                
                # 更新已存在的ID集合（用于非覆盖模式）
                if not overwrite:
                    existing_ids.update(ids_on_page)

                page += 1
                if delay_seconds and delay_seconds > 0:
                    try:
                        import time
                        time.sleep(delay_seconds)
                    except Exception:
                        pass

        if self.logger:
            self.logger.info("分页抓取入库完成")

    def run(self) -> None:
        """运行博牛爬虫的主要逻辑（分页入库）"""
        self.crawl_paginated_and_store()
