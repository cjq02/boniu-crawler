#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译圈子数据脚本
将ims_mdkeji_im_circle表中现有的msg字段翻译为中文和英文，并保存到msg_zh和msg_en字段
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


class CircleDataTranslator:
    """圈子数据翻译器"""
    
    def __init__(self, table_name: str = "ims_mdkeji_im_circle"):
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
    
    def get_untranslated_circles(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取未翻译的圈子列表
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            圈子列表
        """
        sql = f"""
        SELECT id, msg, msg_zh, msg_en
        FROM `{self.table_name}` 
        WHERE (msg_zh IS NULL OR msg_zh = '' OR msg_en IS NULL OR msg_en = '')
        AND msg IS NOT NULL AND msg != ''
        ORDER BY sendtime DESC
        """
        
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"
        
        print(f"    🔍 执行查询: {sql[:100]}...")
        rows = list(fetch_all(sql))
        print(f"    📊 查询到 {len(rows)} 条未翻译记录")
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
            if len(text) > 1000:
                print(f"    ⚠️  文本过长，截取前1000字符进行翻译")
            
            result = self.translator.translate(text_to_translate, from_lang, to_lang)
            if result:
                print(f"    🌐 翻译API调用成功")
            return result
        except Exception as e:
            print(f"    ❌ 翻译失败: {e}")
            return ""
    
    def update_translated_circles(self, circles: List[Dict[str, Any]]) -> int:
        """
        更新翻译后的圈子
        
        Args:
            circles: 包含翻译结果的圈子列表
            
        Returns:
            更新的记录数
        """
        if not circles:
            print("    ⚠️  没有需要更新的记录")
            return 0
        
        print(f"    📝 准备更新 {len(circles)} 条记录到数据库...")
        
        sql = f"""
        UPDATE `{self.table_name}` 
        SET msg_zh = %s, msg_en = %s 
        WHERE id = %s
        """
        
        rows = [
            (
                (c.get('msg_zh') or '')[:65535],
                (c.get('msg_en') or '')[:65535],
                c['id']
            )
            for c in circles
        ]
        
        try:
            affected = executemany(sql, rows)
            print(f"    ✅ 数据库更新成功，影响 {affected} 条记录")
            return affected
        except Exception as e:
            print(f"    ❌ 数据库更新失败: {e}")
            return 0
    
    def translate_batch(self, batch_size: int = 10, delay: float = 1.0, max_records: int = None) -> int:
        """
        批量翻译圈子数据
        
        Args:
            batch_size: 每批处理的记录数
            delay: 每批之间的延迟时间（秒）
            max_records: 最大处理记录数
            
        Returns:
            总共翻译的记录数
        """
        total_translated = 0
        offset = 0
        batch_count = 0
        
        print(f"开始批量翻译，批大小: {batch_size}, 延迟: {delay}秒")
        print("=" * 60)
        
        while True:
            # 获取未翻译的记录
            limit = batch_size
            if max_records and (total_translated + batch_size) > max_records:
                limit = max_records - total_translated
            
            print(f"\n🔍 查询未翻译记录...")
            circles = self.get_untranslated_circles(limit=limit, offset=0)  # offset=0因为每次翻译后会减少未翻译记录
            
            if not circles:
                print("✅ 没有更多未翻译的记录")
                break
            
            batch_count += 1
            print(f"\n📦 批次 {batch_count}: 处理 {len(circles)} 条记录")
            print("-" * 40)
            
            # 翻译每条记录
            translated_circles = []
            for i, circle in enumerate(circles, 1):
                circle_id = circle['id']
                original_msg = circle['msg'] or ''
                
                # 获取已有的翻译
                msg_zh = circle.get('msg_zh') or ''
                msg_en = circle.get('msg_en') or ''
                
                print(f"  🔄 [{i}/{len(circles)}] 处理记录 ID: {circle_id}")
                
                # 如果没有中文翻译，使用原文作为中文
                if not msg_zh and original_msg:
                    msg_zh = original_msg
                    print(f"    📝 使用原文作为中文: {msg_zh[:50]}...")
                
                # 翻译为英文
                if not msg_en and msg_zh:
                    print(f"    🌐 正在翻译为英文...")
                    msg_en = self.translate_text(msg_zh, 'zh', 'en')
                    if msg_en:
                        print(f"    ✅ 翻译成功: {msg_zh[:30]}... -> {msg_en[:30]}...")
                    else:
                        print(f"    ❌ 翻译失败")
                else:
                    print(f"    ⏭️  跳过翻译（已有英文翻译）")
                
                translated_circles.append({
                    'id': circle_id,
                    'msg_zh': msg_zh,
                    'msg_en': msg_en
                })
                
                # 小延迟避免API频率限制
                if i < len(circles):
                    time.sleep(0.5)
            
            # 更新到数据库
            print(f"\n💾 正在更新数据库...")
            affected = self.update_translated_circles(translated_circles)
            print(f"✅ 数据库更新完成，影响 {affected} 条记录")
            
            total_translated += len(circles)
            offset += batch_size
            
            print(f"📊 批次完成: {total_translated} 条记录已处理")
            
            # 检查是否达到最大记录数
            if max_records and total_translated >= max_records:
                print(f"\n⏹️  达到最大记录数限制: {max_records}")
                break
            
            # 批次之间延迟
            if circles and len(circles) == batch_size:
                print(f"\n⏳ 等待 {delay} 秒后继续下一批次...")
                time.sleep(delay)
            else:
                break
        
        print("\n" + "=" * 60)
        print(f"🎉 翻译完成！总共翻译了 {total_translated} 条记录")
        return total_translated
    
    def get_translation_statistics(self) -> Dict[str, int]:
        """
        获取翻译统计信息
        
        Returns:
            统计信息字典
        """
        # 总记录数
        total_sql = f"SELECT COUNT(*) as total FROM `{self.table_name}`"
        total_rows = list(fetch_all(total_sql))
        total = total_rows[0]['total'] if total_rows else 0
        
        # 已翻译记录数
        translated_sql = f"""
        SELECT COUNT(*) as translated FROM `{self.table_name}` 
        WHERE msg_zh IS NOT NULL AND msg_zh != '' 
        AND msg_en IS NOT NULL AND msg_en != ''
        """
        translated_rows = list(fetch_all(translated_sql))
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
    
    parser = argparse.ArgumentParser(description='翻译圈子数据')
    parser.add_argument('--batch-size', type=int, default=10, help='每批处理的记录数（默认10）')
    parser.add_argument('--delay', type=float, default=1.0, help='批次之间的延迟时间（秒，默认1.0）')
    parser.add_argument('--max-records', type=int, default=None, help='最大处理记录数（默认无限制）')
    parser.add_argument('--table', type=str, default='ims_mdkeji_im_circle', help='数据表名称')
    parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    parser.add_argument('--auto', action='store_true', help='自动模式，不需要用户确认')
    
    args = parser.parse_args()
    
    try:
        print("🚀 启动圈子数据翻译工具")
        print("=" * 60)
        
        translator = CircleDataTranslator(table_name=args.table)
        
        if args.stats:
            # 只显示统计信息
            print("\n📊 翻译统计信息")
            print("=" * 60)
            stats = translator.get_translation_statistics()
            print(f"📈 总记录数: {stats['total']}")
            print(f"✅ 已翻译: {stats['translated']} ({stats['percentage']}%)")
            print(f"⏳ 未翻译: {stats['untranslated']}")
        else:
            # 显示统计信息
            print("\n📊 当前翻译状态")
            print("-" * 40)
            stats = translator.get_translation_statistics()
            print(f"📈 总记录数: {stats['total']}")
            print(f"✅ 已翻译: {stats['translated']} ({stats['percentage']}%)")
            print(f"⏳ 未翻译: {stats['untranslated']}")
            
            if stats['untranslated'] == 0:
                print("\n🎉 所有记录已翻译完成！")
                return
            
            # 开始翻译
            print(f"\n⚙️  翻译配置:")
            print(f"   📦 批大小: {args.batch_size}")
            print(f"   ⏱️  延迟: {args.delay}秒")
            print(f"   📊 最大记录: {args.max_records or '无限制'}")
            
            if not args.auto:
                try:
                    input(f"\n⏳ 按回车键开始翻译（将处理最多 {args.max_records or '全部'} 条记录）...")
                except (EOFError, KeyboardInterrupt):
                    print("\n❌ 用户取消操作")
                    return
            else:
                print(f"\n🤖 自动模式：开始翻译（将处理最多 {args.max_records or '全部'} 条记录）...")
            
            total = translator.translate_batch(
                batch_size=args.batch_size,
                delay=args.delay,
                max_records=args.max_records
            )
            
            # 显示最终统计
            print("\n📊 最终统计信息")
            print("=" * 60)
            final_stats = translator.get_translation_statistics()
            print(f"📈 总记录数: {final_stats['total']}")
            print(f"✅ 已翻译: {final_stats['translated']} ({final_stats['percentage']}%)")
            print(f"⏳ 未翻译: {final_stats['untranslated']}")
            
    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
