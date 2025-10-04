-- 添加翻译字段到博牛论坛帖子表
-- 数据库: wq889111_mdkeji
-- 表: ims_mdkeji_im_boniu_forum_post

-- 添加 title_zh 字段（中文标题）
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_zh` VARCHAR(255) DEFAULT NULL COMMENT '中文标题' 
AFTER `title`;

-- 添加 content_zh 字段（中文内容）
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_zh` TEXT DEFAULT NULL COMMENT '中文内容' 
AFTER `content`;

-- 添加 title_en 字段（英文标题）
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_en` VARCHAR(255) DEFAULT NULL COMMENT '英文标题' 
AFTER `title_zh`;

-- 添加 content_en 字段（英文内容）
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_en` TEXT DEFAULT NULL COMMENT '英文内容' 
AFTER `content_zh`;

-- 添加索引以提高查询性能
CREATE INDEX `idx_title_zh` ON `ims_mdkeji_im_boniu_forum_post` (`title_zh`);
CREATE INDEX `idx_title_en` ON `ims_mdkeji_im_boniu_forum_post` (`title_en`);

-- 查看表结构
DESCRIBE `ims_mdkeji_im_boniu_forum_post`;
