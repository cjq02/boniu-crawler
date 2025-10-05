# 圈子数据翻译功能使用指南

## 🎯 功能概述

圈子数据翻译功能可以将 `ims_mdkeji_im_circle` 表中的 `msg` 字段翻译为中文和英文，并保存到 `msg_zh` 和 `msg_en` 字段。

## 📋 数据库结构

### 新增字段
- `msg_zh` TEXT - 中文消息
- `msg_en` TEXT - 英文消息

### 字段用途
- `msg` - 保存原文（原始数据）
- `msg_zh` - 保存中文翻译
- `msg_en` - 保存英文翻译

## 🚀 使用方法

### 1. 添加数据库字段（首次使用）

```bash
# 执行SQL脚本
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_circle_translation_fields.sql
```

或手动执行SQL：
```sql
-- 添加中文消息字段
ALTER TABLE `ims_mdkeji_im_circle` 
ADD COLUMN `msg_zh` TEXT DEFAULT NULL COMMENT '中文消息' 
AFTER `msg`;

-- 添加英文消息字段
ALTER TABLE `ims_mdkeji_im_circle` 
ADD COLUMN `msg_en` TEXT DEFAULT NULL COMMENT '英文消息' 
AFTER `msg_zh`;

-- 添加索引
CREATE INDEX `idx_msg_zh` ON `ims_mdkeji_im_circle` (`msg_zh`(255));
CREATE INDEX `idx_msg_en` ON `ims_mdkeji_im_circle` (`msg_en`(255));
```

### 2. 查看翻译统计

```bash
# 查看圈子翻译统计
python main.py translate-circle --env dev --stats
```

### 3. 翻译圈子数据

```bash
# 自动翻译圈子数据
python main.py translate-circle --env dev --max-records 10 --batch-size 5 --auto

# 翻译所有圈子数据
python main.py translate-circle --env dev --batch-size 20 --delay 1.5 --auto
```

### 4. 直接使用翻译脚本

```bash
# 查看统计
python scripts/translate_circle_data.py --stats

# 自动翻译
python scripts/translate_circle_data.py --max-records 10 --batch-size 5 --auto
```

## 📊 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--batch-size` | 每批处理的记录数 | 10 | `--batch-size 20` |
| `--delay` | 批次之间的延迟时间（秒） | 1.0 | `--delay 2.0` |
| `--max-records` | 最大处理记录数 | 无限制 | `--max-records 100` |
| `--table` | 数据表名称 | ims_mdkeji_im_circle | `--table your_table` |
| `--stats` | 只显示统计信息 | False | `--stats` |
| `--auto` | 自动模式，不需要用户确认 | False | `--auto` |

## 🔄 翻译流程

### 数据处理流程
```
原文数据 → 中文字段 → 英文翻译
msg → msg_zh → msg_en
```

### 翻译逻辑
1. **原文保存**: 爬取的数据保存到 `msg`
2. **中文处理**: 如果没有 `msg_zh`，将原文作为中文
3. **英文翻译**: 从中文翻译为英文，保存到 `msg_en`

## 📊 数据库查询

### 查看翻译统计
```sql
-- 查看圈子翻译统计
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN msg_zh IS NOT NULL AND msg_zh != '' AND msg_en IS NOT NULL AND msg_en != '' THEN 1 ELSE 0 END) as translated
FROM ims_mdkeji_im_circle;
```

### 查看翻译结果
```sql
-- 查看圈子翻译结果
SELECT id, msg, msg_zh, msg_en, created_at
FROM ims_mdkeji_im_circle 
WHERE msg_zh IS NOT NULL AND msg_zh != '' AND msg_en IS NOT NULL AND msg_en != ''
ORDER BY created_at DESC
LIMIT 10;
```

## 🎯 使用示例

### 示例1: 首次使用
```bash
# 1. 添加数据库字段
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_circle_translation_fields.sql

# 2. 查看统计
python main.py translate-circle --env dev --stats

# 3. 测试翻译
python main.py translate-circle --env dev --max-records 5 --batch-size 2 --auto
```

### 示例2: 批量翻译
```bash
# 翻译所有圈子数据
python main.py translate-circle --env dev --batch-size 20 --delay 1.5 --auto
```

### 示例3: 生产环境使用
```bash
# 生产环境翻译
python main.py translate-circle --env prd --batch-size 50 --delay 2.0 --auto
```

## ⚙️ 配置说明

### 翻译器配置
使用相同的翻译器配置 `config/translator.yaml`：

```yaml
translator:
  default_provider: "baidu"
  
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    api_url: "https://fanyi-api.baidu.com/api/trans/vip/translate"
```

## 🔧 故障排除

### 问题1: 数据库连接失败
- 检查环境变量配置
- 确认数据库服务正常运行

### 问题2: 翻译失败
- 检查网络连接
- 验证API密钥
- 查看日志文件

### 问题3: 字段不存在
- 确认已执行SQL脚本添加字段
- 检查表名是否正确

## 📚 相关文档

- [翻译功能使用指南](translation_guide.md)
- [翻译功能快速开始](../TRANSLATION_QUICKSTART.md)
- [翻译工具文档](translator.md)

## ✅ 功能特性

- ✅ 支持圈子数据翻译
- ✅ 自动中文和英文翻译
- ✅ 批量处理支持
- ✅ 智能错误处理
- ✅ 统计功能
- ✅ CLI命令支持
- ✅ 按创建时间排序翻译

圈子数据翻译功能已准备就绪！🎉
