-- 为现有的爬虫执行日志表添加新字段
-- 用于区分定时任务执行和手动执行，并记录执行命令和参数

-- 添加执行类型字段
ALTER TABLE `ims_mdkeji_im_boniu_crawler_log` 
ADD COLUMN `execution_type` enum('scheduled','manual') NOT NULL DEFAULT 'manual' COMMENT '执行类型：scheduled=定时任务，manual=手动执行' 
AFTER `status`;

-- 添加执行命令字段
ALTER TABLE `ims_mdkeji_im_boniu_crawler_log` 
ADD COLUMN `command` varchar(500) DEFAULT NULL COMMENT '执行命令' 
AFTER `environment`;

-- 添加执行参数字段
ALTER TABLE `ims_mdkeji_im_boniu_crawler_log` 
ADD COLUMN `parameters` text COMMENT '执行参数JSON' 
AFTER `command`;

-- 添加索引
ALTER TABLE `ims_mdkeji_im_boniu_crawler_log` 
ADD INDEX `idx_execution_type` (`execution_type`);

-- 更新现有记录的execution_type为manual（手动执行）
UPDATE `ims_mdkeji_im_boniu_crawler_log` 
SET `execution_type` = 'manual' 
WHERE `execution_type` IS NULL OR `execution_type` = '';

-- 显示表结构
DESCRIBE `ims_mdkeji_im_boniu_crawler_log`;
