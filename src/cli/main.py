"""命令行接口主模块"""

import argparse
import os
from typing import Optional

from ..crawler.sites.boniu.crawler import BoniuCrawler
from ..crawler.utils.storage import save_data


def ensure_dir(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def run(mode: str, output: Optional[str]) -> None:
    """运行博牛爬虫

    Args:
        mode: 运行模式，db=分页入库；json=仅抓取并保存为 JSON
        output: 当 mode=json 时的输出文件路径
    """
    crawler = BoniuCrawler()
    if mode == "db":
        print("开始分页抓取并保存到数据库...")
        crawler.crawl_paginated_and_store()
        print("分页抓取入库完成")
        return

    # JSON 模式（与之前行为一致）
    print("开始抓取论坛帖子...")
    posts = crawler.crawl_forum_posts()
    if not posts:
        print("未抓取到任何帖子数据")
        return

    if not output:
        output = "data/boniu_forum_posts.json"
    dirname = os.path.dirname(output) or "."
    ensure_dir(dirname)

    file_path = save_data(posts, os.path.basename(output), output_dir=dirname)
    print(f"抓取完成，共 {len(posts)} 条；已保存到: {file_path}")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="博牛社区论坛爬虫 CLI")
    parser.add_argument(
        "--mode",
        choices=["db", "json"],
        default="db",
        help="运行模式：db=分页入库（默认），json=保存为文件",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件路径（默认 data/boniu_forum_posts.json）",
        default=None,
    )
    args = parser.parse_args()
    run(args.mode, args.output)


if __name__ == "__main__":
    main()
