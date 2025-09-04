"""
博牛社区爬虫 - 正式入口
"""

import sys
import traceback


def _extract_text(result):
	try:
		# CrawlResult 风格
		if hasattr(result, 'data') and result.data:
			return result.data
		# dict 风格
		if isinstance(result, dict) and 'data' in result:
			return result['data']
		# 纯文本
		if isinstance(result, str):
			return result
		return None
	except Exception:
		return None


def test_imports() -> bool:
	try:
		from boniu_crawler import BoniuCrawler  # noqa: F401
		print("✓ 成功导入 BoniuCrawler")
		return True
	except ImportError as e:
		print(f"✗ 导入失败: {e}")
		return False


def test_basic_crawl() -> bool:
	try:
		from boniu_crawler import BoniuCrawler

		print("开始测试基本爬取功能...")
		crawler = BoniuCrawler()

		# 测试爬取论坛页面
		print("正在爬取论坛页面...")
		result = crawler.crawl_url(crawler.forum_url)
		text = _extract_text(result)

		if not text:
			print("✗ 爬取失败: 返回空结果")
			return False

		print(f"✓ 成功爬取页面，内容长度: {len(text)} 字符")

		# 内容验证
		page_content = text.lower()
		if ("博牛" in page_content or "forum" in page_content or "thread" in page_content or "discuz" in page_content or "bbs" in page_content):
			print("✓ 页面内容验证通过")

			# 保存原始页面内容用于调试
			import os
			os.makedirs("data", exist_ok=True)
			with open("data/raw_page.html", "w", encoding="utf-8") as f:
				f.write(text)
			print("✓ 原始页面内容已保存到 data/raw_page.html")

			return True
		else:
			print("✗ 页面内容验证失败")
			print("页面内容预览:")
			print(text[:500] + "...")
			return False

	except Exception as e:
		print(f"✗ 测试失败: {e}")
		traceback.print_exc()
		return False


def test_full_crawl() -> bool:
	try:
		from boniu_crawler import BoniuCrawler

		print("\n开始测试完整爬取功能...")
		crawler = BoniuCrawler()

		# 爬取帖子列表
		print("正在爬取帖子列表...")
		posts = crawler.crawl_forum_posts()

		if posts:
			print(f"✓ 成功获取 {len(posts)} 个帖子")

			# 显示前3个帖子的信息
			for i, post in enumerate(posts[:3]):
				print(f"\n帖子 {i+1}:")
				print(f"  ID: {post.get('id', 'N/A')}")
				print(f"  标题: {post.get('title', 'N/A')}")
				print(f"  用户: {post.get('username', 'N/A')}")
				print(f"  发布时间: {post.get('publish_time', 'N/A')}")
				print(f"  回复数: {post.get('reply_count', 0)}")
				print(f"  浏览数: {post.get('view_count', 0)}")
				print(f"  图片数: {len(post.get('images', []))}")
				print(f"  分类: {post.get('category', 'N/A')}")
				print(f"  URL: {post.get('url', 'N/A')}")

			# 保存数据
			crawler.save_data(posts, "test_posts.json")
			print(f"\n✓ 测试数据已保存到 data/test_posts.json")

			return True
		else:
			print("✗ 未能获取到帖子列表")
			return False

	except Exception as e:
		print(f"✗ 完整爬取测试失败: {e}")
		traceback.print_exc()
		return False


def main() -> None:
	print("博牛社区爬虫 - 正式入口")
	print("=" * 50)

	# 测试导入
	if not test_imports():
		print("\n请先安装依赖: pip install -r requirements.txt")
		return

	# 测试基本爬取
	if test_basic_crawl():
		print("\n✓ 基本爬取测试通过！")

		# 测试完整爬取
		if test_full_crawl():
			print("\n✓ 所有测试通过！爬虫可以正常工作。")
			print("\n数据文件位置:")
			print("- data/test_posts.json - 测试帖子数据")
			print("- data/raw_page.html - 原始页面内容")
			print("\n下一步:")
			print("1. 直接执行: python main.py 进行抓取与验证")
		else:
			print("\n✗ 完整爬取测试失败")
	else:
		print("\n✗ 基本爬取测试失败，请检查网络连接或网站可访问性")


if __name__ == "__main__":
	main()
