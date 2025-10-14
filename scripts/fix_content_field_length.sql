-- 修复content字段长度限制问题
-- 将TEXT类型改为LONGTEXT类型，支持存储更长的内容

-- 修改content字段为LONGTEXT
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
MODIFY COLUMN `content` LONGTEXT COMMENT '帖子内容';

-- 修改content_en字段为LONGTEXT
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
MODIFY COLUMN `content_en` LONGTEXT COMMENT '英文内容';

-- 修改content_zh字段为LONGTEXT
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
MODIFY COLUMN `content_zh` LONGTEXT COMMENT '中文内容';

-- 显示修改后的字段信息
DESCRIBE `ims_mdkeji_im_boniu_forum_post`;

-- 显示字段类型对比
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'ims_mdkeji_im_boniu_forum_post' 
    AND COLUMN_NAME IN ('content', 'content_en', 'content_zh');
