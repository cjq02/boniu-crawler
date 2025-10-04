# 翻译功能更新总结

## 🎯 更新内容

### 数据库结构调整

#### 新增字段
- `title_zh` VARCHAR(255) - 中文标题
- `content_zh` TEXT - 中文内容  
- `title_en` VARCHAR(255) - 英文标题
- `content_en` TEXT - 英文内容

#### 字段用途
- `title` / `content` - 保存原文（原始数据）
- `title_zh` / `content_zh` - 保存中文翻译
- `title_en` / `content_en` - 保存英文翻译

### 翻译逻辑调整

#### 数据流程
```
原文数据 → 中文字段 → 英文翻译
title/content → title_zh/content_zh → title_en/content_en
```

#### 处理逻辑
1. **原文保存**: 爬取的数据保存到 `title` 和 `content`
2. **中文处理**: 如果没有 `title_zh`/`content_zh`，将原文作为中文
3. **英文翻译**: 从中文翻译为英文，保存到 `title_en`/`content_en`

## 📋 更新的文件

### 1. 数据库脚本
- `scripts/add_translation_fields.sql` - 添加4个翻译字段

### 2. 爬虫代码
- `src/crawler/sites/boniu/crawler.py` - 更新插入逻辑和翻译处理

### 3. 翻译脚本
- `scripts/translate_history_data.py` - 更新查询和更新逻辑

### 4. 文档
- `README.md` - 更新使用说明和数据库结构

## 🚀 使用方法

### 首次使用
```bash
# 1. 添加数据库字段
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_translation_fields.sql

# 2. 查看统计
python main.py translate --env dev --stats

# 3. 测试翻译
python main.py translate --env dev --max-records 1 --auto
```

### 日常使用
```bash
# 爬取新数据（自动翻译）
python main.py crawl --env dev --pages 2

# 翻译历史数据
python main.py translate --env dev --batch-size 10 --auto
```

## 📊 数据存储结构

### 字段说明
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `title` | VARCHAR(255) | 原文标题 | "【加Gleezy賬號：b69037】小花 163" |
| `content` | TEXT | 原文内容 | "单亲妈妈短期下海..." |
| `title_zh` | VARCHAR(255) | 中文标题 | "【加Gleezy賬號：b69037】小花 163" |
| `content_zh` | TEXT | 中文内容 | "单亲妈妈短期下海..." |
| `title_en` | VARCHAR(255) | 英文标题 | "【 Add Gleezy account: b69037 】 Xiaohua 163" |
| `content_en` | TEXT | 英文内容 | "Single mother short-term..." |

### 查询示例
```sql
-- 查看翻译统计
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN title_zh IS NOT NULL AND title_zh != '' AND title_en IS NOT NULL AND title_en != '' THEN 1 ELSE 0 END) as translated
FROM ims_mdkeji_im_boniu_forum_post;

-- 查看翻译结果
SELECT forum_post_id, title, title_zh, title_en, LEFT(content, 50) as content, LEFT(content_zh, 50) as content_zh, LEFT(content_en, 50) as content_en
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_zh IS NOT NULL AND title_zh != '' AND title_en IS NOT NULL AND title_en != ''
LIMIT 10;
```

## ✅ 测试结果

### 功能测试
- ✅ 数据库字段添加成功
- ✅ 翻译器初始化正常
- ✅ 翻译功能正常工作
- ✅ 数据保存正确
- ✅ 统计功能正常

### 测试输出示例
```
翻译统计信息
============================================================
总记录数: 119
已翻译: 1 (0.84%)
未翻译: 118

翻译结果:
标题: 【加Gleezy賬號：b69037】小花 163 #單親媽媽短期下海 
-> 【 Add Gleezy account: b69037 】 Xiaohua 163 # Single mother short-term
内容: 1034 字符 -> 2368 字符
```

## 🎉 功能优势

### 1. 数据完整性
- 保留原文数据不变
- 支持多语言存储
- 便于数据追溯和对比

### 2. 翻译灵活性
- 支持中英文双语存储
- 可单独更新某种语言
- 支持增量翻译

### 3. 查询便利性
- 可查询原文、中文、英文
- 支持多语言搜索
- 便于国际化应用

## 📚 相关文档

- [翻译功能使用指南](docs/translation_guide.md)
- [翻译功能快速开始](TRANSLATION_QUICKSTART.md)
- [翻译工具文档](docs/translator.md)
- [翻译功能实现文档](docs/translation_implementation.md)

## 🔧 注意事项

1. **首次使用**: 必须先执行SQL脚本添加字段
2. **数据备份**: 建议在添加字段前备份数据库
3. **翻译质量**: 长文本只翻译前1000字符
4. **API限制**: 注意翻译API的频率限制
5. **索引优化**: 已添加相关索引提高查询性能

翻译功能更新完成！🎉
