#!/usr/bin/env python3
"""
生产环境抓取测试脚本（不入库）

功能：
- 直接请求指定 fid 与 page 的列表页
- 保存原始 HTML 到 prd_test/outputs
- 使用站点解析逻辑解析帖子列表，保存 JSON 结果
- 支持备用静态路径 forum-<fid>-<page>.html 测试

用法示例：
  python prd_test/run_prd_test.py --fid 89 --page 1
  python prd_test/run_prd_test.py --fid 89 --page 1 --alt
"""

import argparse
import json
import os
import sys
from datetime import datetime

from bs4 import BeautifulSoup

# 将项目根目录加入路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.crawler.sites.boniu.crawler import BoniuCrawler, _extract_text  # type: ignore


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_posts_from_html(crawler: BoniuCrawler, html: str):
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    for row in soup.find_all('tr'):
        try:
            item = crawler._parse_post_row(row)
            if item:
                posts.append(item)
        except Exception:
            pass
    return posts


def main():
    parser = argparse.ArgumentParser(description="Boniu 生产抓取测试（不入库）")
    parser.add_argument("--fid", type=int, required=True, help="论坛 fid")
    parser.add_argument("--page", type=int, default=1, help="页码，默认1")
    parser.add_argument("--alt", action="store_true", help="使用备用静态路径 forum-<fid>-<page>.html")
    args = parser.parse_args()

    out_dir = os.path.join(PROJECT_ROOT, "prd_test", "outputs")
    ensure_dir(out_dir)

    crawler = BoniuCrawler()
    # 降低日志噪音
    try:
        import logging
        crawler.logger.setLevel(logging.WARNING)
    except Exception:
        pass

    # 构造URL
    base_url = crawler.base_url.rstrip('/')
    if args.alt:
        url = f"{base_url}/forum-{args.fid}-{args.page}.html"
    else:
        url = f"{base_url}/forum.php?mod=forumdisplay&fid={args.fid}&page={args.page}"

    # 执行请求
    result = crawler.crawl_url(url)
    html = _extract_text(result)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(out_dir, f"list_fid{args.fid}_p{args.page}{'_alt' if args.alt else ''}_{ts}.html")
    json_path = os.path.join(out_dir, f"parsed_fid{args.fid}_p{args.page}{'_alt' if args.alt else ''}_{ts}.json")
    meta_path = os.path.join(out_dir, f"meta_fid{args.fid}_p{args.page}{'_alt' if args.alt else ''}_{ts}.json")

    # 保存HTML
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html or "")
    except Exception:
        pass

    # 解析
    posts = []
    if html:
        posts = parse_posts_from_html(crawler, html)

    # 保存解析结果
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"count": len(posts), "posts": posts}, f, ensure_ascii=False, indent=2)

    # 保存元信息
    meta = {
        "request_url": url,
        "status_code": getattr(result, "status_code", None),
        "data_length": len(html or ""),
        "time": ts,
        "headers": dict(crawler.session.headers or {}),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"已保存 HTML: {os.path.relpath(html_path, PROJECT_ROOT)}")
    print(f"已保存解析 JSON: {os.path.relpath(json_path, PROJECT_ROOT)} (count={len(posts)})")
    print(f"已保存元信息: {os.path.relpath(meta_path, PROJECT_ROOT)}")


if __name__ == "__main__":
    main()


