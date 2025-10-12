-- 创建爬虫执行日志表
-- 用于记录每次定时任务的执行情况

CREATE TABLE IF NOT EXISTS `ims_mdkeji_im_boniu_crawler_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `start_time` datetime NOT NULL COMMENT '任务开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '任务结束时间',
  `status` enum('running','success','failed','timeout','error') NOT NULL DEFAULT 'running' COMMENT '执行状态',
  `environment` varchar(50) NOT NULL DEFAULT 'production' COMMENT '执行环境',
  `pages` int(11) NOT NULL DEFAULT 2 COMMENT '爬取页数',
  `posts_count` int(11) NOT NULL DEFAULT 0 COMMENT '本次爬取的帖子数量',
  `message` text COMMENT '执行消息或错误信息',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_start_time` (`start_time`),
  KEY `idx_status` (`status`),
  KEY `idx_environment` (`environment`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬虫执行日志表';

-- 插入示例数据（可选）
-- INSERT INTO `ims_mdkeji_im_boniu_crawler_log` 
-- (`start_time`, `end_time`, `status`, `environment`, `pages`, `posts_count`, `message`) 
-- VALUES 
-- (NOW(), NOW(), 'success', 'production', 2, 15, '定时任务执行成功，爬取了15个新帖子');

-- 查询最近执行记录的SQL示例
-- SELECT 
--   id,
--   start_time,
--   end_time,
--   status,
--   environment,
--   pages,
--   posts_count,
--   message,
--   TIMESTAMPDIFF(SECOND, start_time, end_time) as duration_seconds
-- FROM ims_mdkeji_im_boniu_crawler_log 
-- ORDER BY start_time DESC 
-- LIMIT 10;

-- 查询执行统计的SQL示例
-- SELECT 
--   DATE(start_time) as execution_date,
--   COUNT(*) as total_executions,
--   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
--   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
--   SUM(posts_count) as total_posts_crawled,
--   AVG(TIMESTAMPDIFF(SECOND, start_time, end_time)) as avg_duration_seconds
-- FROM ims_mdkeji_im_boniu_crawler_log 
-- WHERE start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
-- GROUP BY DATE(start_time)
-- ORDER BY execution_date DESC;
