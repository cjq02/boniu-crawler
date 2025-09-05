"""
测试修复版博牛社区爬虫
"""

from boniu_fixed_crawler import BoniuFixedCrawler

def test_fixed_crawler():
    """测试修复版爬虫"""
    print("测试修复版博牛社区爬虫")
    print("=" * 50)
    
    crawler = BoniuFixedCrawler()
    
    # 爬取帖子列表
    print("正在爬取帖子列表...")
    posts = crawler.crawl_forum_posts()
    
    if posts:
        print(f"✓ 成功获取 {len(posts)} 个帖子")
        
        # 显示前5个帖子的信息
        for i, post in enumerate(posts[:5]):
            print(f"\n帖子 {i+1}:")
            print(f"  标题: {post.get('title', 'N/A')}")
            print(f"  用户: {post.get('username', 'N/A')}")
            print(f"  发布时间: {post.get('publish_time', 'N/A')}")
            print(f"  回复数: {post.get('reply_count', 0)}")
            print(f"  浏览数: {post.get('view_count', 0)}")
            print(f"  图片数: {len(post.get('images', []))}")
            print(f"  分类: {post.get('category', 'N/A')}")
            print(f"  URL: {post.get('url', 'N/A')}")
        
        # 保存数据
        crawler.save_data(posts, "fixed_posts.json")
        print(f"\n✓ 修复版数据已保存到 data/fixed_posts.json")
        
        return True
    else:
        print("✗ 未能获取到帖子列表")
        return False

if __name__ == "__main__":
    test_fixed_crawler()
