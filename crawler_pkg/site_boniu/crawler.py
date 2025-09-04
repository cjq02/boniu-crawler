"""博牛站点爬虫实现（从包 boniu_crawler 迁移并更名为 crawler_pkg）"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler_pkg.core.requests_impl import RequestsCrawler
from utils import clean_text, extract_number, format_datetime


def _extract_text(result: Any) -> Optional[str]:
	# 兼容 CrawlResult / dict / str
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
	def __init__(self):
		super().__init__("boniu_crawler")
		self.base_url = "https://bbs.boniu123.cc"
		self.forum_url = "https://bbs.boniu123.cc/forum-89-1.html"
		self._setup_headers()

	def _setup_headers(self):
		self.session.headers.update({
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Accept-Encoding': 'gzip, deflate, br',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1',
		})

	def _parse_view_count(self, view_text: str) -> int:
		if not view_text:
			return 0
		if '万' in view_text:
			number = extract_number(view_text)
			return int(number * 10000) if number else 0
		return int(extract_number(view_text) or 0)

	def crawl_forum_posts(self) -> List[Dict[str, Any]]:
		self.logger.info(f"开始爬取论坛页面: {self.forum_url}")
		resp = self.crawl_url(self.forum_url)
		html = _extract_text(resp)
		if not html:
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
				self.logger.warning(f"解析帖子行失败: {e}")
		self.logger.info(f"解析到 {len(posts)} 个帖子")
		return posts

	def _parse_post_row(self, row) -> Optional[Dict[str, Any]]:
		# 标题与URL
		title_link = row.find('a', class_='s xst') or row.find('a', href=re.compile(r'thread-\d+'))
		if not title_link:
			return None
		title = clean_text(title_link.get_text())
		post_url = urljoin(self.base_url, title_link.get('href', ''))

		# 帖子ID
		post_id = None
		m = re.search(r'thread-(\d+)', post_url)
		if m:
			post_id = m.group(1)

		# 用户名
		username = "未知用户"
		user_element = row.find('a', class_=re.compile(r'username|author'))
		if user_element:
			username = clean_text(user_element.get_text())

		# 头像
		avatar_url = None
		avatar_img = row.find('img', class_='author-avatar') or row.find('img', src=re.compile(r'avatar'))
		if avatar_img and avatar_img.get('src'):
			avatar_url = urljoin(self.base_url, avatar_img['src'])

		# 发帖时间
		publish_time = ""
		for span in row.find_all('span', title=True):
			t = span.get('title', '')
			if re.search(r'\d{4}-\d{1,2}-\d{1,2}', t):
				publish_time = t
				break
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

		# 图片
		images: List[str] = []
		for img in row.find_all('img', src=True):
			if re.search(r'attachment|image|\.jpg|\.png|\.gif', img['src'], re.I):
				images.append(urljoin(self.base_url, img['src']))

		# 分类
		category = ""
		for a in row.find_all('a'):
			text = clean_text(a.get_text())
			if text in ['游戏包网', '游戏API', '支付渠道', '广告营销', '云服务', '技术外包', '媒体渠道', '本地服务']:
				category = text
				break

		# 标识
		is_sticky = bool(row.find('img', alt=re.compile(r'置顶|sticky|top')))
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
		}


