"""
测试博牛社区爬虫
"""

import json
from boniu_simple_crawler import BoniuSimpleCrawler
from logger import get_logger


def test_crawler():
    """测试爬虫功能"""
    logger = get_logger("test")
    logger.info("开始测试博牛社区爬虫")
    
    crawler = BoniuSimpleCrawler()
    
    try:
        # 测试爬取论坛页面
        logger.info("测试爬取论坛页面...")
        posts = crawler.crawl_forum_posts()
        
        if posts:
            logger.info(f"成功获取 {len(posts)} 个帖子")
            
            # 显示前3个帖子的信息
            for i, post in enumerate(posts[:3]):
                logger.info(f"帖子 {i+1}:")
                logger.info(f"  标题: {post.get('title', 'N/A')}")
                logger.info(f"  用户: {post.get('username', 'N/A')}")
                logger.info(f"  发布时间: {post.get('publish_time', 'N/A')}")
                logger.info(f"  回复数: {post.get('reply_count', 0)}")
                logger.info(f"  浏览数: {post.get('view_count', 0)}")
                logger.info(f"  图片数: {len(post.get('images', []))}")
                logger.info(f"  分类: {post.get('category', 'N/A')}")
                logger.info(f"  URL: {post.get('url', 'N/A')}")
                logger.info("---")
            
            # 测试爬取第一个帖子的详情
            if posts:
                logger.info("测试爬取帖子详情...")
                first_post = posts[0]
                detail = crawler.crawl_post_detail(first_post['url'])
                
                if detail:
                    logger.info("帖子详情:")
                    logger.info(f"  内容长度: {len(detail.get('content', ''))}")
                    logger.info(f"  内容图片数: {len(detail.get('content_images', []))}")
                    logger.info(f"  附件数: {len(detail.get('attachments', []))}")
                    logger.info(f"  回复数: {len(detail.get('replies', []))}")
                    logger.info(f"  帖子ID: {detail.get('post_id', 'N/A')}")
                    
                    # 显示前2个回复
                    replies = detail.get('replies', [])
                    for i, reply in enumerate(replies[:2]):
                        logger.info(f"  回复 {i+1}: {reply.get('username', 'N/A')} - {reply.get('reply_time', 'N/A')}")
                else:
                    logger.warning("未能获取帖子详情")
            
            # 保存测试数据
            crawler.save_data(posts, "test_boniu_posts.json")
            logger.info("测试数据已保存到 test_boniu_posts.json")
            
        else:
            logger.error("未能获取到帖子列表")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise


def analyze_html_structure():
    """分析HTML结构"""
    logger = get_logger("analyze")
    logger.info("分析博牛社区HTML结构...")
    
    crawler = BoniuSimpleCrawler()
    
    try:
        # 爬取页面
        result = crawler.crawl_url(crawler.forum_url)
        if result.error:
            logger.error(f"爬取失败: {result.error}")
            return
        
        # 解析HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(result.data, 'html.parser')
        
        # 查找所有tr元素
        tr_elements = soup.find_all('tr')
        logger.info(f"找到 {len(tr_elements)} 个tr元素")
        
        # 分析前几个tr元素的结构
        for i, tr in enumerate(tr_elements[:5]):
            logger.info(f"TR {i+1} 分析:")
            logger.info(f"  class: {tr.get('class', 'N/A')}")
            logger.info(f"  id: {tr.get('id', 'N/A')}")
            
            # 查找所有td元素
            td_elements = tr.find_all('td')
            logger.info(f"  td数量: {len(td_elements)}")
            
            for j, td in enumerate(td_elements):
                logger.info(f"    TD {j+1}: {clean_text(td.get_text())[:50]}...")
            
            # 查找所有链接
            links = tr.find_all('a')
            logger.info(f"  链接数量: {len(links)}")
            for j, link in enumerate(links[:3]):
                logger.info(f"    链接 {j+1}: {link.get('href', 'N/A')} - {clean_text(link.get_text())[:30]}...")
            
            logger.info("---")
        
        # 查找所有图片
        images = soup.find_all('img')
        logger.info(f"找到 {len(images)} 个图片")
        
        # 分析图片src
        image_srcs = []
        for img in images[:10]:
            src = img.get('src', '')
            if src:
                image_srcs.append(src)
        
        logger.info("图片src示例:")
        for src in image_srcs[:5]:
            logger.info(f"  {src}")
        
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")


def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    import re
    return re.sub(r'\s+', ' ', text.strip())


if __name__ == "__main__":
    # 先分析HTML结构
    analyze_html_structure()
    
    # 然后测试爬虫
    test_crawler()
