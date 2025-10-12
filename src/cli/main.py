"""命令行接口主模块"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from ..crawler.sites.boniu.crawler import BoniuCrawler
from ..crawler.utils.storage import save_data
from ..scheduler.execution_logger import get_execution_logger


def ensure_dir(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def run(
    mode: str = "db",
    output: Optional[str] = None,
    pages: int = 2,
    overwrite: bool = False,
    fid: Optional[int] = None,
    post_id: Optional[int] = None,
) -> None:
    """运行博牛爬虫

    Args:
        mode: 运行模式，db=分页入库；json=仅抓取并保存为 JSON，默认为db
        output: 当 mode=json 时的输出文件路径
        pages: 最大爬取页数，默认为2
        overwrite: 是否覆盖数据库中已存在的记录，默认为False
        fid: 仅抓取指定的版块ID（fid）
        post_id: 仅抓取指定的帖子ID（thread id），用于快速调试
    """
    # 获取执行日志记录器
    execution_logger = get_execution_logger(execution_type="manual")
    
    # 构建执行命令和参数
    import sys
    command = " ".join(sys.argv)
    parameters = {
        "mode": mode,
        "pages": pages,
        "overwrite": overwrite,
        "fid": fid,
        "post_id": post_id,
        "output": output
    }
    
    # 使用执行上下文管理器记录日志
    with execution_logger.execution_context(pages=pages, command=command, parameters=parameters):
        crawler = BoniuCrawler()
        # 覆盖 fid 列表（若提供）
        if fid is not None:
            crawler.fids = [fid]

        # 若提供 post_id，则直接抓取该帖子详情，保存到 data/debug 后返回
        if post_id is not None:
            from pathlib import Path
            thread_url = f"https://bbs.boniu123.cc/thread-{post_id}-1-1.html"
            content, images = crawler._fetch_post_content(thread_url)
            debug_dir = Path("data/debug")
            debug_dir.mkdir(parents=True, exist_ok=True)
            (debug_dir / f"thread_{post_id}_clean.txt").write_text(content or "", encoding="utf-8")
            import json as _json
            (debug_dir / f"thread_{post_id}_images.json").write_text(
                _json.dumps(images or [], ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"已保存: {debug_dir}/thread_{post_id}_clean.txt")
            print(f"已保存: {debug_dir}/thread_{post_id}_images.json")
            return
            
        if mode == "db":
            print(f"开始分页抓取并保存到数据库... (最大页数: {pages}, 覆盖模式: {overwrite})")
            crawler.crawl_paginated_and_store(max_pages=pages, overwrite=overwrite)
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


def _load_env(env_name: str) -> None:
    """根据 --env 加载 env.dev / env.prd 文件到环境变量

    优先不覆盖已有环境变量。
    """
    filename = f"env.{env_name}"
    candidate = Path(filename)
    if not candidate.exists():
        return
    try:
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key and (key not in os.environ):
                os.environ[key] = value
    except Exception:
        pass


def translate_history() -> None:
    """翻译历史数据"""
    # 导入翻译脚本
    script_path = Path(__file__).parent.parent.parent / "scripts" / "translate_history_data.py"
    if not script_path.exists():
        print(f"错误: 找不到翻译脚本 {script_path}")
        sys.exit(1)
    
    # 执行翻译脚本
    import subprocess
    # 过滤掉 --env 参数，因为翻译脚本不需要
    args = []
    skip_next = False
    for i, arg in enumerate(sys.argv[2:]):
        if skip_next:
            skip_next = False
            continue
        if arg == '--env':
            skip_next = True
            continue
        args.append(arg)
    subprocess.run([sys.executable, str(script_path)] + args)


def translate_circle() -> None:
    """翻译圈子数据"""
    # 导入翻译脚本
    script_path = Path(__file__).parent.parent.parent / "scripts" / "translate_circle_data.py"
    if not script_path.exists():
        print(f"错误: 找不到圈子翻译脚本 {script_path}")
        sys.exit(1)
    
    # 执行翻译脚本
    import subprocess
    # 过滤掉 --env 参数，因为翻译脚本不需要
    args = []
    skip_next = False
    for i, arg in enumerate(sys.argv[2:]):
        if skip_next:
            skip_next = False
            continue
        if arg == '--env':
            skip_next = True
            continue
        args.append(arg)
    subprocess.run([sys.executable, str(script_path)] + args)


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="博牛社区论坛爬虫 CLI")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # crawl 子命令（原有功能）
    crawl_parser = subparsers.add_parser('crawl', help='爬取数据')
    crawl_parser.add_argument(
        "--mode",
        choices=["db", "json"],
        default="db",
        help="运行模式：db=分页入库（默认），json=保存为文件",
    )
    crawl_parser.add_argument(
        "--env",
        choices=["dev", "prd"],
        required=True,
        help="加载环境变量文件：dev -> env.dev；prd -> env.prd（必传）",
    )
    crawl_parser.add_argument(
        "--output",
        "-o",
        help="输出文件路径（默认 data/boniu_forum_posts.json）",
        default=None,
    )
    crawl_parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="最大爬取页数（默认 2）",
    )
    crawl_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖数据库中已存在的记录（默认不覆盖）",
    )
    crawl_parser.add_argument(
        "--fid",
        type=int,
        help="仅抓取指定的版块ID（fid）",
        default=None,
    )
    crawl_parser.add_argument(
        "--post-id",
        type=int,
        help="仅抓取指定的帖子ID（thread id），会保存清洗结果到 data/debug",
        default=None,
    )
    
    # translate 子命令（翻译历史数据）
    translate_parser = subparsers.add_parser('translate', help='翻译历史数据')
    translate_parser.add_argument('--batch-size', type=int, default=10, help='每批处理的记录数（默认10）')
    translate_parser.add_argument('--delay', type=float, default=1.0, help='批次之间的延迟时间（秒，默认1.0）')
    translate_parser.add_argument('--max-records', type=int, default=None, help='最大处理记录数（默认无限制）')
    translate_parser.add_argument('--table', type=str, default='ims_mdkeji_im_boniu_forum_post', help='数据表名称')
    translate_parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    translate_parser.add_argument('--auto', action='store_true', help='自动模式，不需要用户确认')
    translate_parser.add_argument(
        "--env",
        choices=["dev", "prd"],
        required=True,
        help="加载环境变量文件：dev -> env.dev；prd -> env.prd（必传）",
    )
    
    # translate-circle 子命令（翻译圈子数据）
    translate_circle_parser = subparsers.add_parser('translate-circle', help='翻译圈子数据')
    translate_circle_parser.add_argument('--batch-size', type=int, default=10, help='每批处理的记录数（默认10）')
    translate_circle_parser.add_argument('--delay', type=float, default=1.0, help='批次之间的延迟时间（秒，默认1.0）')
    translate_circle_parser.add_argument('--max-records', type=int, default=None, help='最大处理记录数（默认无限制）')
    translate_circle_parser.add_argument('--table', type=str, default='ims_mdkeji_im_circle', help='数据表名称')
    translate_circle_parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    translate_circle_parser.add_argument('--auto', action='store_true', help='自动模式，不需要用户确认')
    translate_circle_parser.add_argument(
        "--env",
        choices=["dev", "prd"],
        required=True,
        help="加载环境变量文件：dev -> env.dev；prd -> env.prd（必传）",
    )
    
    args = parser.parse_args()
    
    # 如果没有子命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # 加载环境变量
    if hasattr(args, 'env') and args.env:
        _load_env(args.env)
    
    # 执行对应的命令
    if args.command == 'crawl':
        run(args.mode, args.output, args.pages, args.overwrite, args.fid, args.post_id)
    elif args.command == 'translate':
        translate_history()
    elif args.command == 'translate-circle':
        translate_circle()


if __name__ == "__main__":
    main()
