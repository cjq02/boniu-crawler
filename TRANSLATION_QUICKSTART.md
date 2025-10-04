# 翻译功能快速开始

## 🚀 快速开始（3步搞定）

### 第1步：添加数据库字段

```bash
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < scripts/add_translation_fields.sql
```

### 第2步：爬取新数据（自动翻译）

```bash
# 开发环境
python main.py crawl --env dev --pages 2

# 生产环境
python main.py crawl --env prd --pages 5
```

### 第3步：翻译历史数据

```bash
# 查看统计
python scripts/translate_history_data.py --stats

# 翻译历史数据
python scripts/translate_history_data.py --batch-size 10 --delay 1.0
```

## 📋 常用命令

### 1. 爬取并自动翻译新数据
```bash
python main.py crawl --env dev --pages 3
```

### 2. 查看翻译统计
```bash
python scripts/translate_history_data.py --stats
```

### 3. 翻译历史数据（推荐配置）
```bash
# 小批量测试（翻译100条）
python scripts/translate_history_data.py --max-records 100 --batch-size 10 --delay 1.0

# 大批量翻译（翻译所有）
python scripts/translate_history_data.py --batch-size 20 --delay 1.5
```

### 4. 使用CLI命令
```bash
# 翻译历史数据
python main.py translate --env dev --batch-size 10 --delay 1.0

# 只看统计
python main.py translate --env dev --stats
```

## ⚙️ 配置文件

配置文件位置：`config/translator.yaml`

```yaml
translator:
  default_provider: "baidu"
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
```

## 📊 查看结果

### 数据库查询
```sql
-- 查看翻译统计
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN title_en IS NOT NULL AND title_en != '' THEN 1 ELSE 0 END) as translated
FROM ims_mdkeji_im_boniu_forum_post;

-- 查看翻译结果
SELECT forum_post_id, title, title_en, LEFT(content, 50) as content, LEFT(content_en, 50) as content_en
FROM ims_mdkeji_im_boniu_forum_post 
WHERE title_en IS NOT NULL AND title_en != ''
LIMIT 10;
```

## ⚠️ 注意事项

1. **首次使用**: 先执行SQL脚本添加字段
2. **测试先行**: 用 `--max-records 10` 先测试
3. **控制频率**: 使用适当的 `--delay` 参数避免API限制
4. **监控日志**: 查看 `logs/` 目录下的日志文件

## 🔧 故障排除

### 问题：中文乱码
```bash
chcp 65001
```

### 问题：翻译失败
- 检查网络连接
- 验证API密钥
- 查看日志文件

### 问题：数据库连接失败
- 检查 `env.dev` 或 `env.prd` 配置
- 确认数据库服务运行正常

## 📚 详细文档

- 完整文档: [docs/translation_guide.md](docs/translation_guide.md)
- 翻译工具: [docs/translator.md](docs/translator.md)
- API文档: [docs/api.md](docs/api.md)

## ✅ 功能清单

- ✅ 自动翻译新爬取的数据
- ✅ 批量翻译历史数据
- ✅ 支持百度翻译API
- ✅ 智能错误处理
- ✅ 可配置的翻译参数
- ✅ CLI命令支持
- ✅ 翻译统计功能

就是这么简单！🎉
