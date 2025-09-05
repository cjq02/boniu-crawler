#!/usr/bin/env python3
"""
博牛爬虫演示脚本
展示重构后项目的使用方法
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from crawler.sites.boniu.crawler import BoniuCrawler
from crawler.utils.storage import save_data


def demo_basic_usage():
    """演示基本使用方法"""
    print("=== 博牛爬虫基本使用演示 ===")
    
    # 创建爬虫实例
    crawler = BoniuCrawler()
    
    # 爬取论坛帖子
    print("开始爬取博牛社区论坛帖子...")
    posts = crawler.crawl_forum_posts()
    
    if posts:
        print(f"✅ 成功获取 {len(posts)} 个帖子")
        
        # 显示前3个帖子的信息
        print("\n📋 帖子预览:")
        for i, post in enumerate(posts[:3], 1):
            print(f"{i}. {post['title']}")
            print(f"   用户: {post['username']}")
            print(f"   时间: {post['publish_time']}")
            print(f"   回复: {post['reply_count']}, 浏览: {post['view_count']}")
            print(f"   分类: {post['category']}")
            print(f"   置顶: {'是' if post['is_sticky'] else '否'}, 精华: {'是' if post['is_essence'] else '否'}")
            print()
        
        # 保存数据
        output_file = "data/processed/demo_posts.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        file_path = save_data(posts, os.path.basename(output_file), 
                            output_dir=os.path.dirname(output_file))
        print(f"💾 数据已保存到: {file_path}")
        
    else:
        print("❌ 未获取到任何帖子数据")


def demo_advanced_usage():
    """演示高级使用方法"""
    print("\n=== 高级使用演示 ===")
    
    # 创建爬虫实例
    crawler = BoniuCrawler()
    
    # 获取爬虫状态
    status = crawler.get_status()
    print(f"📊 爬虫状态: {status['name']}")
    print(f"   运行状态: {'运行中' if status['is_running'] else '已停止'}")
    
    # 爬取数据
    posts = crawler.crawl_forum_posts()
    
    if posts:
        # 数据分析
        total_posts = len(posts)
        sticky_posts = len([p for p in posts if p['is_sticky']])
        essence_posts = len([p for p in posts if p['is_essence']])
        categories = {}
        
        for post in posts:
            category = post['category'] or '未分类'
            categories[category] = categories.get(category, 0) + 1
        
        print(f"\n📈 数据分析:")
        print(f"   总帖子数: {total_posts}")
        print(f"   置顶帖子: {sticky_posts}")
        print(f"   精华帖子: {essence_posts}")
        print(f"   分类统计:")
        for category, count in categories.items():
            print(f"     {category}: {count}")
        
        # 保存分析结果
        analysis = {
            "summary": {
                "total_posts": total_posts,
                "sticky_posts": sticky_posts,
                "essence_posts": essence_posts,
                "categories": categories
            },
            "posts": posts
        }
        
        output_file = "data/processed/demo_analysis.json"
        file_path = save_data(analysis, os.path.basename(output_file),
                            output_dir=os.path.dirname(output_file))
        print(f"💾 分析结果已保存到: {file_path}")


def main():
    """主函数"""
    print("🚀 博牛爬虫重构版演示")
    print("=" * 50)
    
    try:
        # 基本使用演示
        demo_basic_usage()
        
        # 高级使用演示
        demo_advanced_usage()
        
        print("\n✅ 演示完成！")
        print("📚 更多信息请查看 docs/ 目录下的文档")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
