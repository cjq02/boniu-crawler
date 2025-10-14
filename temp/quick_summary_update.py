#!/usr/bin/env python3
"""
快速摘要更新脚本
为现有数据快速生成摘要字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler.utils.db import get_db_config, connect, fetch_all, executemany

def quick_update_summaries():
    """快速更新摘要字段"""
    print("开始快速更新摘要字段...")
    
    # 获取数据库配置
    db_cfg = get_db_config()
    table_name = "ims_mdkeji_im_boniu_forum_post"
    
    try:
        # 连接数据库
        conn = connect()
        cursor = conn.cursor()
        
        # 查询需要更新的记录
        query = f"""
        SELECT id, content, content_zh, content_en
        FROM `{table_name}`
        WHERE (content IS NOT NULL AND content != '') 
           OR (content_zh IS NOT NULL AND content_zh != '') 
           OR (content_en IS NOT NULL AND content_en != '')
        """
        
        print("查询需要更新的记录...")
        cursor.execute(query)
        records = cursor.fetchall()
        
        if not records:
            print("没有找到需要更新的记录")
            return
        
        print(f"找到 {len(records)} 条记录需要更新")
        
        # 准备更新数据
        update_data = []
        
        for record in records:
            record_id = record['id']
            content = record['content'] or ''
            content_zh = record['content_zh'] or ''
            content_en = record['content_en'] or ''
            
            # 生成摘要（截取前200个字符）
            content_summary = content[:200] if content else ''
            content_summary_zh = content_zh[:200] if content_zh else ''
            content_summary_en = content_en[:200] if content_en else ''
            
            # 如果没有原始内容但有中文内容，使用中文内容作为原始摘要
            if not content_summary and content_summary_zh:
                content_summary = content_summary_zh
            
            # 如果没有中文内容但有原始内容，使用原始内容作为中文摘要
            if not content_summary_zh and content_summary:
                content_summary_zh = content_summary
            
            update_data.append((
                content_summary,
                content_summary_en,
                content_summary_zh,
                record_id
            ))
        
        # 批量更新
        if update_data:
            update_sql = f"""
            UPDATE `{table_name}` 
            SET 
                `content_summary` = %s,
                `content_summary_en` = %s,
                `content_summary_zh` = %s,
                `updated_at` = NOW()
            WHERE `id` = %s
            """
            
            print(f"开始批量更新 {len(update_data)} 条记录...")
            affected_rows = executemany(update_sql, update_data)
            
            print(f"更新完成！影响行数: {affected_rows}")
            
            # 显示统计信息
            stats_query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN content_summary IS NOT NULL AND content_summary != '' THEN 1 ELSE 0 END) as has_summary,
                SUM(CASE WHEN content_summary_zh IS NOT NULL AND content_summary_zh != '' THEN 1 ELSE 0 END) as has_summary_zh,
                SUM(CASE WHEN content_summary_en IS NOT NULL AND content_summary_en != '' THEN 1 ELSE 0 END) as has_summary_en
            FROM `{table_name}`
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            print("\n更新统计:")
            print(f"  总记录数: {stats['total']}")
            print(f"  有原始摘要: {stats['has_summary']}")
            print(f"  有中文摘要: {stats['has_summary_zh']}")
            print(f"  有英文摘要: {stats['has_summary_en']}")
            
    except Exception as e:
        print(f"更新失败: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        quick_update_summaries()
        print("\n✅ 摘要更新完成！")
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        sys.exit(1)
