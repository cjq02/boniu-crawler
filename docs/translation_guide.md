# 翻译功能使用指南

## 功能概述

爬虫系统已集成自动翻译功能，可以将爬取到的中文标题和内容翻译成英文，并保存到数据库的 `title_en` 和 `content_en` 字段。

## 功能特性

- ✅ 自动翻译新爬取的数据
- ✅ 批量翻译历史数据
- ✅ 支持百度翻译API
- ✅ 智能错误处理和重试
- ✅ 可配置的翻译参数

## 数据库准备

### 1. 添加翻译字段

在数据库中执行以下SQL语句添加翻译字段：

```bash
mysql -h HOST -u USER -p DATABASE < scripts/add_translation_fields.sql
```

或者手动执行：

```sql
-- 添加英文标题字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `title_en` VARCHAR(255) DEFAULT NULL COMMENT '英文标题' 
AFTER `title`;

-- 添加英文内容字段
ALTER TABLE `ims_mdkeji_im_boniu_forum_post` 
ADD COLUMN `content_en` TEXT DEFAULT NULL COMMENT '英文内容' 
AFTER `content`;

-- 添加索引
CREATE INDEX `idx_title_en` ON `ims_mdkeji_im_boniu_forum_post` (`title_en`);
```

## 使用方法

### 方法1: 自动翻译新数据

爬虫在爬取新数据时会自动翻译标题和内容：

```bash
# 使用开发环境配置
python main.py crawl --env dev --pages 2

# 使用生产环境配置
python main.py crawl --env prd --pages 5
```

**特点：**
- 爬取新帖子时自动翻译
- 翻译失败不影响数据保存
- 翻译日志会记录在日志文件中

### 方法2: 翻译历史数据

#### 查看统计信息

```bash
python scripts/translate_history_data.py --stats
```

输出示例：
```
翻译统计信息
============================================================
总记录数: 1000
已翻译: 200 (20.0%)
未翻译: 800
```

#### 批量翻译

```bash
# 基本用法（翻译所有未翻译的数据）
python scripts/translate_history_data.py

# 指定批次大小和延迟
python scripts/translate_history_data.py --batch-size 20 --delay 2.0

# 限制最大翻译记录数
python scripts/translate_history_data.py --max-records 100

# 指定数据表
python scripts/translate_history_data.py --table ims_mdkeji_im_boniu_forum_post
```

#### 使用CLI命令

```bash
# 查看统计信息
python main.py translate --env dev --stats

# 翻译历史数据
python main.py translate --env dev --batch-size 10 --delay 1.0

# 限制翻译数量
python main.py translate --env prd --max-records 50
```

## 配置说明

### 翻译器配置

配置文件位置：`config/translator.yaml`

```yaml
translator:
  default_provider: "baidu"
  
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    api_url: "https://fanyi-api.baidu.com/api/trans/vip/translate"
  
  settings:
    default_from_lang: "zh"
    default_to_lang: "en"
    timeout: 10
```

### 参数说明

#### 翻译脚本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--batch-size` | 每批处理的记录数 | 10 |
| `--delay` | 批次之间的延迟时间（秒） | 1.0 |
| `--max-records` | 最大处理记录数 | 无限制 |
| `--table` | 数据表名称 | ims_mdkeji_im_boniu_forum_post |
| `--stats` | 只显示统计信息 | False |

## 翻译逻辑

### 1. 标题翻译
- 完整翻译标题文本
- 翻译结果保存到 `title_en` 字段
- 最大长度：255字符

### 2. 内容翻译
- 对于长文本（>1000字符），只翻译前1000字符
- 翻译结果保存到 `content_en` 字段
- 最大长度：65535字符（TEXT类型）

### 3. 错误处理
- 翻译失败时，字段保存为空字符串
- 不影响数据保存流程
- 错误信息记录在日志中

## 使用示例

### 示例1: 爬取并自动翻译新数据

```bash
# 1. 启动爬虫（自动翻译）
python main.py crawl --env dev --pages 3

# 2. 查看日志
tail -f logs/$(date +%Y/%m/%d).log
```

### 示例2: 翻译历史数据

```bash
# 1. 查看当前翻译状态
python scripts/translate_history_data.py --stats

# 2. 翻译前100条记录（测试）
python scripts/translate_history_data.py --max-records 100 --batch-size 10

# 3. 再次查看统计
python scripts/translate_history_data.py --stats

# 4. 翻译所有剩余数据
python scripts/translate_history_data.py --batch-size 20 --delay 1.5
```

### 示例3: 生产环境批量翻译

```bash
# 使用生产环境配置
python main.py translate --env prd --batch-size 50 --delay 2.0 --max-records 1000
```

## 性能优化建议

### 1. 批次大小
- **小批次（5-10）**: 适合测试和调试
- **中批次（20-50）**: 适合常规翻译
- **大批次（50-100）**: 适合大规模翻译，注意API限制

### 2. 延迟时间
- **短延迟（0.5-1.0秒）**: 快速翻译，注意API频率限制
- **中延迟（1.0-2.0秒）**: 平衡速度和稳定性
- **长延迟（2.0-5.0秒）**: 避免API限制，更稳定

### 3. 翻译策略
- 优先翻译热门帖子
- 分批翻译，避免一次性处理过多数据
- 在低峰期执行大批量翻译

## 监控和维护

### 查看翻译进度

```bash
# 查看统计信息
python scripts/translate_history_data.py --stats
```

### 查看翻译日志

```bash
# 查看今天的日志
tail -f logs/$(date +%Y/%m/%d).log | grep "翻译"

# 查看错误日志
tail -f logs/$(date +%Y/%m/%d).log | grep "翻译失败"
```

### 数据库查询

```sql
-- 查看翻译统计
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN title_en IS NOT NULL AND title_en != '' THEN 1 ELSE 0 END) as translated,
    SUM(CASE WHEN title_en IS NULL OR title_en = '' THEN 1 ELSE 0 END) as untranslated
FROM ims_mdkeji_im_boniu_forum_post;

-- 查看最近翻译的记录
SELECT forum_post_id, title, title_en, updated_at 
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_en IS NOT NULL AND title_en != ''
ORDER BY updated_at DESC 
LIMIT 10;

-- 查看未翻译的记录
SELECT forum_post_id, title 
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_en IS NULL OR title_en = ''
LIMIT 10;
```

## 故障排除

### 问题1: 翻译失败

**症状**: 日志显示"翻译失败"

**解决方案**:
1. 检查网络连接
2. 验证API密钥是否正确
3. 检查API配额是否用完
4. 查看详细错误日志

### 问题2: 翻译速度慢

**症状**: 翻译进度缓慢

**解决方案**:
1. 增加批次大小
2. 减少延迟时间
3. 检查网络状况
4. 考虑使用多线程（需要修改代码）

### 问题3: 数据库连接失败

**症状**: 无法连接到数据库

**解决方案**:
1. 检查环境变量配置
2. 验证数据库连接信息
3. 确保数据库服务正常运行
4. 检查防火墙设置

### 问题4: 中文乱码

**症状**: 输出显示乱码

**解决方案**:
1. 在PowerShell中执行 `chcp 65001`
2. 确保终端支持UTF-8编码
3. 使用脚本内置的编码处理

## API限制说明

### 百度翻译API限制

- **标准版**:
  - QPS: 10次/秒
  - 字符限制: 6000字符/次
  - 月配额: 根据套餐

- **建议配置**:
  - 批次大小: 10-20
  - 延迟时间: 1-2秒
  - 避免并发请求

## 最佳实践

1. **测试先行**: 先用小批次测试翻译效果
2. **分批处理**: 不要一次性翻译所有数据
3. **监控日志**: 及时发现和处理错误
4. **定期备份**: 翻译前备份数据库
5. **错峰执行**: 在低峰期进行大批量翻译
6. **验证结果**: 定期抽查翻译质量

## 注意事项

⚠️ **重要提示**:

1. 翻译会消耗API配额，请注意控制翻译量
2. 长文本只翻译前1000字符，完整翻译需修改代码
3. 翻译失败的记录不会重试，需手动处理
4. 建议在测试环境充分测试后再在生产环境使用
5. 定期检查翻译质量，必要时调整翻译策略

## 技术支持

如有问题，请查看：
- 日志文件: `logs/YYYY/MM/DD.log`
- 配置文件: `config/translator.yaml`
- 翻译工具文档: `docs/translator.md`
- 主项目文档: `README.md`
