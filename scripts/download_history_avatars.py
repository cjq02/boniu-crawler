#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载历史数据中的头像URL到本地，并更新数据库
如果用户名重复，使用已有的头像，不重复下载
"""

# 立即输出，确保脚本开始执行
import sys
# 强制刷新输出
sys.stdout.flush()

print("=" * 60, flush=True)
print("脚本开始执行...", flush=True)

import os
print(f"Python版本: {sys.version.split()[0]}", flush=True)
print(f"脚本文件: {__file__}", flush=True)
print("=" * 60, flush=True)

# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# 切换到项目根目录（重要！）
os.chdir(project_root)

# 输出调试信息
print(f"脚本目录: {script_dir}")
print(f"项目根目录: {project_root}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}")

import logging
from typing import Dict, Optional

# 确保logs目录存在
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, 'download_history_avatars.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 导入模块（在日志配置之后）
print("正在导入模块...")
try:
    # 直接导入utils模块，避免触发__init__.py的导入链
    import importlib.util
    
    # 导入db模块
    db_path = os.path.join(project_root, 'src', 'crawler', 'utils', 'db.py')
    spec = importlib.util.spec_from_file_location("db", db_path)
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    get_db_config = db_module.get_db_config
    connect = db_module.connect
    fetch_all = db_module.fetch_all
    executemany = db_module.executemany
    print("  ✓ 导入 src.crawler.utils.db 成功")
    
    # 导入image_downloader模块
    img_downloader_path = os.path.join(project_root, 'src', 'crawler', 'utils', 'image_downloader.py')
    spec = importlib.util.spec_from_file_location("image_downloader", img_downloader_path)
    img_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(img_module)
    ImageDownloader = img_module.ImageDownloader
    print("  ✓ 导入 src.crawler.utils.image_downloader 成功")
except Exception as e:
    print(f"  ✗ 导入模块失败: {e}")
    import traceback
    traceback.print_exc()
    logger.error(f"导入模块失败: {e}")
    logger.error("请确保在项目根目录执行脚本，并且虚拟环境已激活")
    sys.exit(1)


def download_history_avatars():
    """下载历史数据中的头像并更新数据库"""
    print("开始下载历史数据中的头像...")
    logger.info("开始下载历史数据中的头像...")
    
    # 获取数据库配置
    db_cfg = get_db_config()
    table_name = "ims_mdkeji_im_boniu_forum_post"
    
    # 初始化图片下载器
    img_base_path = os.getenv("BONIU_IMG_BASE_PATH") or os.path.join(os.getcwd(), "images", "boniu")
    avatar_save_path = os.path.join(img_base_path, 'avatar')
    image_downloader = ImageDownloader(
        base_path=img_base_path,
        logger=logger
    )
    
    try:
        # 连接数据库
        conn = connect()
        cursor = conn.cursor()
        
        # 步骤1: 查询所有需要下载头像的记录（URL格式且用户名不为空）
        # 对于每个用户名，只获取最早记录的头像URL
        query = f"""
        SELECT 
            t_min.username,
            t_avatar.avatar_url
        FROM (
            SELECT 
                username,
                MIN(id) as min_id
            FROM `{table_name}`
            WHERE username IS NOT NULL 
              AND username != '' 
              AND username != '未知用户'
              AND avatar_url IS NOT NULL 
              AND avatar_url != ''
              AND (avatar_url LIKE 'http://%' OR avatar_url LIKE 'https://%')
            GROUP BY username
        ) AS t_min
        INNER JOIN `{table_name}` AS t_avatar 
            ON t_min.username = t_avatar.username 
            AND t_min.min_id = t_avatar.id
        ORDER BY t_min.min_id ASC
        """
        
        logger.info("查询需要下载头像的记录...")
        cursor.execute(query)
        records = cursor.fetchall()
        
        if not records:
            logger.info("没有找到需要下载头像的记录")
            return
        
        logger.info(f"找到 {len(records)} 条需要下载头像的记录")
        
        # 步骤2: 构建用户名到本地头像路径的映射（避免重复下载）
        username_avatar_map: Dict[str, str] = {}
        update_data = []
        downloaded_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, record in enumerate(records, 1):
            username = record['username']
            avatar_url = record['avatar_url']
            
            # 如果该用户名已经有本地头像，跳过
            if username in username_avatar_map:
                skipped_count += 1
                if i % 100 == 0:
                    logger.info(f"处理进度: {i}/{len(records)}, 已下载: {downloaded_count}, 跳过: {skipped_count}, 错误: {error_count}")
                continue
            
            # 下载头像
            try:
                logger.debug(f"下载头像 [{i}/{len(records)}]: {username} -> {avatar_url}")
                local_avatar = image_downloader.download_image(avatar_url, save_path=avatar_save_path)
                
                if local_avatar:
                    # 保存到映射中
                    username_avatar_map[username] = local_avatar
                    downloaded_count += 1
                    logger.debug(f"头像下载成功: {username} -> {local_avatar}")
                else:
                    error_count += 1
                    logger.warning(f"头像下载失败: {username} -> {avatar_url}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"下载头像异常 {username} -> {avatar_url}: {e}")
            
            # 每处理100条记录输出一次进度
            if i % 100 == 0:
                logger.info(f"处理进度: {i}/{len(records)}, 已下载: {downloaded_count}, 跳过: {skipped_count}, 错误: {error_count}")
        
        logger.info(f"头像下载完成: 成功 {downloaded_count} 个, 跳过 {skipped_count} 个, 失败 {error_count} 个")
        
        # 步骤3: 更新数据库中所有该用户名的头像URL
        if username_avatar_map:
            logger.info(f"开始更新数据库，共 {len(username_avatar_map)} 个用户...")
            
            for username, local_avatar in username_avatar_map.items():
                # 查询该用户名所有需要更新的记录
                update_query = f"""
                SELECT id FROM `{table_name}`
                WHERE username = %s
                  AND (avatar_url LIKE 'http://%%' OR avatar_url LIKE 'https://%%')
                """
                cursor.execute(update_query, (username,))
                record_ids = cursor.fetchall()
                
                if record_ids:
                    # 批量更新
                    for record_id in record_ids:
                        update_data.append((local_avatar, record_id['id']))
            
            # 执行批量更新
            if update_data:
                update_sql = f"""
                UPDATE `{table_name}` 
                SET avatar_url = %s, updated_at = NOW()
                WHERE id = %s
                """
                
                logger.info(f"开始批量更新 {len(update_data)} 条记录...")
                affected_rows = executemany(update_sql, update_data)
                logger.info(f"数据库更新完成，影响行数: {affected_rows}")
            else:
                logger.warning("没有需要更新的记录")
        else:
            logger.warning("没有成功下载的头像，跳过数据库更新")
        
        # 步骤4: 统计更新结果
        stats_query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN avatar_url LIKE 'http://%' OR avatar_url LIKE 'https://%' THEN 1 ELSE 0 END) as url_count,
            SUM(CASE WHEN avatar_url LIKE 'images/boniu/%' THEN 1 ELSE 0 END) as local_count,
            SUM(CASE WHEN avatar_url IS NULL OR avatar_url = '' THEN 1 ELSE 0 END) as empty_count
        FROM `{table_name}`
        WHERE username IS NOT NULL 
          AND username != '' 
          AND username != '未知用户'
        """
        
        cursor.execute(stats_query)
        stats = cursor.fetchone()
        
        logger.info("=" * 60)
        logger.info("更新统计:")
        logger.info(f"  总记录数: {stats['total_records']}")
        logger.info(f"  URL格式头像: {stats['url_count']}")
        logger.info(f"  本地路径头像: {stats['local_count']}")
        logger.info(f"  空头像: {stats['empty_count']}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")


if __name__ == "__main__":
    try:
        # 输出初始信息
        print("=" * 60)
        print("开始执行历史头像下载脚本")
        print("=" * 60)
        logger.info("=" * 60)
        logger.info("开始执行历史头像下载脚本")
        logger.info(f"工作目录: {os.getcwd()}")
        logger.info(f"Python版本: {sys.version}")
        logger.info("=" * 60)
        
        download_history_avatars()
        
        print("=" * 60)
        print("历史头像下载脚本执行完成")
        print("=" * 60)
        logger.info("=" * 60)
        logger.info("历史头像下载脚本执行完成")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
        logger.warning("用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"脚本执行失败: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
