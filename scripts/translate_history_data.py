#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译历史数据脚本
将数据库中现有的title和content翻译为英文，并保存到title_en和content_en字段
"""

import sys
import os
import io
import time
from typing import List, Dict, Any

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.crawler.utils.translator_config import create_translator_from_config
from src.crawler.utils.db import fetch_all, executemany, get_db_config


class HistoryDataTranslator:
    """历史数据翻译器"""
    
    def __init__(self, table_name: str = "ims_mdkeji_im_boniu_forum_post"):
        """
        初始化翻译器
        
        Args:
            table_name: 数据表名称
        """
        self.table_name = table_name
        self.translator = create_translator_from_config()
        self.db_config = get_db_config()
        
        print(f"数据库配置: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
        print(f"数据表: {self.table_name}")
        print("翻译器初始化成功")
    
    def get_untranslated_posts(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取未翻译的帖子列表
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            帖子列表
        """
        sql = f"""
        SELECT forum_post_id, title, content 
        FROM `{self.table_name}` 
        WHERE (title_en IS NULL OR title_en = '' OR content_en IS NULL OR content_en = '')
        AND title IS NOT NULL AND title != ''
        ORDER BY forum_post_id DESC
        """
        
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"
        
        rows = fetch_all(sql)
        print(f"查询到 {len(rows)} 条未翻译记录")
        return rows
    
    def translate_text(self, text: str, from_lang: str = "zh", to_lang: str = "en") -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            from_lang: 源语言
            to_lang: 目标语言
            
        Returns:
            翻译后的文本
        """
        if not text:
            return ""
        
        try:
            # 对于长文本，截取前1000字符进行翻译
            text_to_translate = text[:1000] if len(text) > 1000 else text
            result = self.translator.translate(text_to_translate, from_lang, to_lang)
            return result
        except Exception as e:
            print(f"翻译失败: {e}")
            return ""
    
    def update_translated_posts(self, posts: List[Dict[str, Any]]) -> int:
        """
        更新翻译后的帖子
        
        Args:
            posts: 包含翻译结果的帖子列表
            
        Returns:
            更新的记录数
        """
        if not posts:
            return 0
        
        sql = f"""
        UPDATE `{self.table_name}` 
        SET title_en = %s, content_en = %s 
        WHERE forum_post_id = %s
        """
        
        rows = [
            (
                (p.get('title_en') or '')[:255],
                (p.get('content_en') or '')[:65535],
                p['forum_post_id']
            )
            for p in posts
        ]
        
        affected = executemany(sql, rows)
        print(f"更新了 {affected} 条记录")
        return affected
    
    def translate_batch(self, batch_size: int = 10, delay: float = 1.0, max_records: int = None) -> int:
        """
        批量翻译历史数据
        
        Args:
            batch_size: 每批处理的记录数
            delay: 每批之间的延迟时间（秒）
            max_records: 最大处理记录数
            
        Returns:
            总共翻译的记录数
        """
        total_translated = 0
        offset = 0
        
        print(f"开始批量翻译，批大小: {batch_size}, 延迟: {delay}秒")
        print("=" * 60)
        
        while True:
            # 获取未翻译的记录
            limit = batch_size
            if max_records and (total_translated + batch_size) > max_records:
                limit = max_records - total_translated
            
            posts = self.get_untranslated_posts(limit=limit, offset=0)  # offset=0因为每次翻译后会减少未翻译记录
            
            if not posts:
                print("没有更多未翻译的记录")
                break
            
            print(f"\n批次 {offset // batch_size + 1}: 处理 {len(posts)} 条记录")
            
            # 翻译每条记录
            translated_posts = []
            for i, post in enumerate(posts, 1):
                post_id = post['forum_post_id']
                title = post['title'] or ''
                content = post['content'] or ''
                
                print(f"  [{i}/{len(posts)}] ID: {post_id}")
                
                # 翻译标题
                title_en = self.translate_text(title, 'zh', 'en')
                print(f"    标题: {title[:50]} -> {title_en[:50]}")
                
                # 翻译内容（长文本只翻译前1000字符）
                if content:
                    content_en = self.translate_text(content, 'zh', 'en')
                    print(f"    内容: {len(content)} 字符 -> {len(content_en)} 字符")
                else:
                    content_en = ""
                
                translated_posts.append({
                    'forum_post_id': post_id,
                    'title_en': title_en,
                    'content_en': content_en
                })
                
                # 小延迟避免API频率限制
                if i < len(posts):
                    time.sleep(0.5)
            
            # 更新到数据库
            print(f"\n  更新数据库...")
            self.update_translated_posts(translated_posts)
            
            total_translated += len(posts)
            offset += batch_size
            
            print(f"  已完成: {total_translated} 条记录")
            
            # 检查是否达到最大记录数
            if max_records and total_translated >= max_records:
                print(f"\n达到最大记录数限制: {max_records}")
                break
            
            # 批次之间延迟
            if posts and len(posts) == batch_size:
                print(f"\n等待 {delay} 秒...")
                time.sleep(delay)
            else:
                break
        
        print("\n" + "=" * 60)
        print(f"翻译完成！总共翻译了 {total_translated} 条记录")
        return total_translated
    
    def get_translation_statistics(self) -> Dict[str, int]:
        """
        获取翻译统计信息
        
        Returns:
            统计信息字典
        """
        # 总记录数
        total_sql = f"SELECT COUNT(*) as total FROM `{self.table_name}`"
        total_rows = fetch_all(total_sql)
        total = total_rows[0]['total'] if total_rows else 0
        
        # 已翻译记录数
        translated_sql = f"""
        SELECT COUNT(*) as translated FROM `{self.table_name}` 
        WHERE title_en IS NOT NULL AND title_en != '' 
        AND content_en IS NOT NULL AND content_en != ''
        """
        translated_rows = fetch_all(translated_sql)
        translated = translated_rows[0]['translated'] if translated_rows else 0
        
        # 未翻译记录数
        untranslated = total - translated
        
        return {
            'total': total,
            'translated': translated,
            'untranslated': untranslated,
            'percentage': round(translated / total * 100, 2) if total > 0 else 0
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='翻译历史数据')
    parser.add_argument('--batch-size', type=int, default=10, help='每批处理的记录数（默认10）')
    parser.add_argument('--delay', type=float, default=1.0, help='批次之间的延迟时间（秒，默认1.0）')
    parser.add_argument('--max-records', type=int, default=None, help='最大处理记录数（默认无限制）')
    parser.add_argument('--table', type=str, default='ims_mdkeji_im_boniu_forum_post', help='数据表名称')
    parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    
    args = parser.parse_args()
    
    try:
        translator = HistoryDataTranslator(table_name=args.table)
        
        if args.stats:
            # 只显示统计信息
            print("\n翻译统计信息")
            print("=" * 60)
            stats = translator.get_translation_statistics()
            print(f"总记录数: {stats['total']}")
            print(f"已翻译: {stats['translated']} ({stats['percentage']}%)")
            print(f"未翻译: {stats['untranslated']}")
        else:
            # 显示统计信息
            stats = translator.get_translation_statistics()
            print(f"\n当前状态: {stats['translated']}/{stats['total']} 已翻译 ({stats['percentage']}%)")
            print(f"未翻译记录: {stats['untranslated']}")
            
            if stats['untranslated'] == 0:
                print("\n所有记录已翻译完成！")
                return
            
            # 开始翻译
            input(f"\n按回车键开始翻译（将处理最多 {args.max_records or '全部'} 条记录）...")
            
            total = translator.translate_batch(
                batch_size=args.batch_size,
                delay=args.delay,
                max_records=args.max_records
            )
            
            # 显示最终统计
            print("\n最终统计信息")
            print("=" * 60)
            final_stats = translator.get_translation_statistics()
            print(f"总记录数: {final_stats['total']}")
            print(f"已翻译: {final_stats['translated']} ({final_stats['percentage']}%)")
            print(f"未翻译: {final_stats['untranslated']}")
            
    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
