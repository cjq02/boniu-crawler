#!/usr/bin/env python3
"""
一次性脚本：为现有数据生成摘要字段
为 ims_mdkeji_im_boniu_forum_post 表中的现有数据生成 content_summary、content_summary_en、content_summary_zh 字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler.utils.db import get_db_config, connect, fetch_all, executemany
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('temp/generate_summaries.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def generate_summaries():
    """为现有数据生成摘要字段"""
    logger.info("开始为现有数据生成摘要字段...")
    
    # 获取数据库配置
    db_cfg = get_db_config()
    table_name = "ims_mdkeji_im_boniu_forum_post"
    
    try:
        # 连接数据库
        conn = connect()
        cursor = conn.cursor()
        
        # 查询所有需要生成摘要的记录
        query = f"""
        SELECT id, forum_post_id, content, content_zh, content_en, title
        FROM `{table_name}`
        WHERE (content IS NOT NULL AND content != '') 
           OR (content_zh IS NOT NULL AND content_zh != '') 
           OR (content_en IS NOT NULL AND content_en != '')
        ORDER BY id
        """
        
        logger.info("查询需要生成摘要的记录...")
        cursor.execute(query)
        records = cursor.fetchall()
        
        if not records:
            logger.info("没有找到需要生成摘要的记录")
            return
        
        logger.info(f"找到 {len(records)} 条记录需要生成摘要")
        
        # 准备更新数据
        update_data = []
        processed_count = 0
        
        for record in records:
            record_id = record['id']
            forum_post_id = record['forum_post_id']
            content = record['content'] or ''
            content_zh = record['content_zh'] or ''
            content_en = record['content_en'] or ''
            title = record['title'] or ''
            
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
            
            processed_count += 1
            
            # 每处理100条记录输出一次进度
            if processed_count % 100 == 0:
                logger.info(f"已处理 {processed_count}/{len(records)} 条记录")
        
        # 批量更新数据库
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
            
            logger.info(f"开始批量更新 {len(update_data)} 条记录...")
            affected_rows = executemany(update_sql, update_data)
            
            logger.info(f"批量更新完成，影响行数: {affected_rows}")
            
            # 统计摘要生成情况
            stats_query = f"""
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN content_summary IS NOT NULL AND content_summary != '' THEN 1 ELSE 0 END) as has_summary,
                SUM(CASE WHEN content_summary_zh IS NOT NULL AND content_summary_zh != '' THEN 1 ELSE 0 END) as has_summary_zh,
                SUM(CASE WHEN content_summary_en IS NOT NULL AND content_summary_en != '' THEN 1 ELSE 0 END) as has_summary_en
            FROM `{table_name}`
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            logger.info("摘要生成统计:")
            logger.info(f"  总记录数: {stats['total_records']}")
            logger.info(f"  有原始摘要: {stats['has_summary']}")
            logger.info(f"  有中文摘要: {stats['has_summary_zh']}")
            logger.info(f"  有英文摘要: {stats['has_summary_en']}")
            
        else:
            logger.warning("没有数据需要更新")
            
    except Exception as e:
        logger.error(f"生成摘要时发生错误: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")

def verify_summaries():
    """验证摘要生成结果"""
    logger.info("验证摘要生成结果...")
    
    db_cfg = get_db_config()
    table_name = "ims_mdkeji_im_boniu_forum_post"
    
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # 查询一些示例记录
        sample_query = f"""
        SELECT id, forum_post_id, title, 
               LEFT(content, 100) as content_preview,
               content_summary, content_summary_zh, content_summary_en
        FROM `{table_name}`
        WHERE content_summary IS NOT NULL AND content_summary != ''
        ORDER BY id
        LIMIT 10
        """
        
        cursor.execute(sample_query)
        samples = cursor.fetchall()
        
        logger.info("摘要生成示例:")
        for sample in samples:
            logger.info(f"ID: {sample['id']}, 标题: {sample['title'][:50]}...")
            logger.info(f"  原始摘要: {sample['content_summary'][:100]}...")
            logger.info(f"  中文摘要: {sample['content_summary_zh'][:100] if sample['content_summary_zh'] else '无'}...")
            logger.info(f"  英文摘要: {sample['content_summary_en'][:100] if sample['content_summary_en'] else '无'}...")
            logger.info("---")
            
    except Exception as e:
        logger.error(f"验证摘要时发生错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("开始执行摘要生成脚本")
        logger.info("=" * 60)
        
        # 生成摘要
        generate_summaries()
        
        # 验证结果
        verify_summaries()
        
        logger.info("=" * 60)
        logger.info("摘要生成脚本执行完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)
