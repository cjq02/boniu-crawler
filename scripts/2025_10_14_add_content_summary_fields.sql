-- 为 ims_mdkeji_im_boniu_forum_post 表添加内容摘要字段
-- 添加时间: 2025-01-27

-- 添加 content_summary 字段 (原始内容摘要)
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary` varchar(200) DEFAULT NULL COMMENT '内容摘要' 
AFTER `content`;

-- 添加 content_summary_en 字段 (英文内容摘要)
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary_en` varchar(200) DEFAULT NULL COMMENT '英文内容摘要' 
AFTER `content_en`;

-- 添加 content_summary_zh 字段 (中文内容摘要)
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_summary_zh` varchar(200) DEFAULT NULL COMMENT '中文内容摘要' 
AFTER `content_zh`;

-- 验证字段是否添加成功
-- DESCRIBE `ims_mdkeji_im_boniu_forum_post`;
