-- 添加翻译字段到圈子表
-- 数据库: wq889111_mdkeji
-- 表: ims_mdkeji_im_circle

-- 添加 msg_zh 字段（中文消息）
ALTER TABLE `ims_mdkeji_im_circle` 
ADD COLUMN `msg_zh` TEXT DEFAULT NULL COMMENT '中文消息' 
AFTER `msg`;

-- 添加 msg_en 字段（英文消息）
ALTER TABLE `ims_mdkeji_im_circle` 
ADD COLUMN `msg_en` TEXT DEFAULT NULL COMMENT '英文消息' 
AFTER `msg_zh`;

-- 添加索引以提高查询性能
CREATE INDEX `idx_msg_zh` ON `ims_mdkeji_im_circle` (`msg_zh`(255));
CREATE INDEX `idx_msg_en` ON `ims_mdkeji_im_circle` (`msg_en`(255));

-- 查看表结构
DESCRIBE `ims_mdkeji_im_circle`;
