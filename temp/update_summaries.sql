-- 一次性脚本：为现有数据生成摘要字段
-- 为 ims_mdkeji_im_boniu_forum_post 表中的现有数据生成 content_summary、content_summary_en、content_summary_zh 字段

-- 更新原始内容摘要（截取前200字符）
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `content_summary` = LEFT(`content`, 200)
WHERE `content` IS NOT NULL AND `content` != '';

-- 更新中文内容摘要（截取前200字符）
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `content_summary_zh` = LEFT(`content_zh`, 200)
WHERE `content_zh` IS NOT NULL AND `content_zh` != '';

-- 更新英文内容摘要（截取前200字符）
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `content_summary_en` = LEFT(`content_en`, 200)
WHERE `content_en` IS NOT NULL AND `content_en` != '';

-- 对于没有原始内容但有中文内容的记录，使用中文内容作为原始摘要
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `content_summary` = LEFT(`content_zh`, 200)
WHERE (`content` IS NULL OR `content` = '') 
  AND `content_zh` IS NOT NULL AND `content_zh` != ''
  AND (`content_summary` IS NULL OR `content_summary` = '');

-- 对于没有中文内容但有原始内容的记录，使用原始内容作为中文摘要
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `content_summary_zh` = LEFT(`content`, 200)
WHERE (`content_zh` IS NULL OR `content_zh` = '') 
  AND `content` IS NOT NULL AND `content` != ''
  AND (`content_summary_zh` IS NULL OR `content_summary_zh` = '');

-- 更新 updated_at 字段
UPDATE `ims_mdkeji_im_boniu_forum_post` 
SET `updated_at` = NOW()
WHERE `content_summary` IS NOT NULL AND `content_summary` != '';

-- 查看更新统计
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN content_summary IS NOT NULL AND content_summary != '' THEN 1 ELSE 0 END) as has_summary,
    SUM(CASE WHEN content_summary_zh IS NOT NULL AND content_summary_zh != '' THEN 1 ELSE 0 END) as has_summary_zh,
    SUM(CASE WHEN content_summary_en IS NOT NULL AND content_summary_en != '' THEN 1 ELSE 0 END) as has_summary_en
FROM `ims_mdkeji_im_boniu_forum_post`;

-- 查看一些示例记录
SELECT 
    id, 
    forum_post_id, 
    LEFT(title, 50) as title_preview,
    LEFT(content_summary, 100) as summary_preview,
    LEFT(content_summary_zh, 100) as summary_zh_preview,
    LEFT(content_summary_en, 100) as summary_en_preview
FROM `ims_mdkeji_im_boniu_forum_post`
WHERE content_summary IS NOT NULL AND content_summary != ''
ORDER BY id
LIMIT 10;
