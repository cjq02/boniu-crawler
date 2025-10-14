# 摘要字段生成脚本说明

本目录包含用于为现有数据生成摘要字段的一次性脚本。

## 脚本文件说明

### 1. `generate_summaries.py` - 完整版Python脚本
- **功能**: 完整的摘要生成脚本，包含详细的日志记录和验证
- **特点**: 
  - 详细的进度显示
  - 完整的日志记录
  - 结果验证功能
  - 错误处理机制
- **适用场景**: 生产环境或需要详细日志的场景

### 2. `quick_summary_update.py` - 快速版Python脚本
- **功能**: 快速生成摘要字段的简化脚本
- **特点**:
  - 简洁的输出
  - 快速执行
  - 基本的统计信息
- **适用场景**: 开发环境或快速测试

### 3. `update_summaries.sql` - SQL脚本
- **功能**: 直接通过SQL语句更新摘要字段
- **特点**:
  - 执行速度快
  - 不依赖Python环境
  - 包含统计查询
- **适用场景**: 数据库管理员直接操作

## 使用方法

### 方法1: 使用Python脚本（推荐）

```bash
# 进入项目根目录
cd D:\me\epiboly\fuye\projects\boniu-crawler

# 使用完整版脚本
python temp/generate_summaries.py

# 或使用快速版脚本
python temp/quick_summary_update.py
```

### 方法2: 使用SQL脚本

```bash
# 连接MySQL数据库
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE

# 执行SQL脚本
source temp/update_summaries.sql;
```

## 脚本功能说明

### 摘要生成逻辑
1. **原始摘要** (`content_summary`): 截取 `content` 字段的前200个字符
2. **中文摘要** (`content_summary_zh`): 截取 `content_zh` 字段的前200个字符
3. **英文摘要** (`content_summary_en`): 截取 `content_en` 字段的前200个字符

### 智能处理
- 如果原始内容为空但有中文内容，使用中文内容作为原始摘要
- 如果中文内容为空但有原始内容，使用原始内容作为中文摘要
- 自动更新 `updated_at` 字段

### 更新范围
- 只更新有内容的记录（`content`、`content_zh`、`content_en` 任一不为空）
- 批量更新，提高执行效率
- 包含统计信息显示

## 执行前准备

1. **确保数据库字段已添加**:
   ```sql
   -- 如果还没有添加摘要字段，先执行
   source scripts/add_content_summary_fields.sql;
   ```

2. **检查环境配置**:
   - 确保数据库连接配置正确
   - 确保有足够的数据库权限

## 执行后验证

执行完成后，可以通过以下SQL查询验证结果：

```sql
-- 查看摘要统计
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN content_summary IS NOT NULL AND content_summary != '' THEN 1 ELSE 0 END) as has_summary,
    SUM(CASE WHEN content_summary_zh IS NOT NULL AND content_summary_zh != '' THEN 1 ELSE 0 END) as has_summary_zh,
    SUM(CASE WHEN content_summary_en IS NOT NULL AND content_summary_en != '' THEN 1 ELSE 0 END) as has_summary_en
FROM `ims_mdkeji_im_boniu_forum_post`;

-- 查看示例记录
SELECT 
    id, 
    forum_post_id, 
    LEFT(title, 50) as title,
    LEFT(content_summary, 100) as summary,
    LEFT(content_summary_zh, 100) as summary_zh,
    LEFT(content_summary_en, 100) as summary_en
FROM `ims_mdkeji_im_boniu_forum_post`
WHERE content_summary IS NOT NULL AND content_summary != ''
ORDER BY id
LIMIT 10;
```

## 注意事项

1. **备份数据**: 执行前建议备份数据库
2. **执行时间**: 根据数据量大小，执行时间可能较长
3. **字符长度**: 摘要字段限制为200字符，超长内容会被截断
4. **重复执行**: 脚本可以重复执行，不会产生重复数据

## 故障排除

如果执行过程中遇到问题：

1. **数据库连接失败**: 检查数据库配置和网络连接
2. **权限不足**: 确保数据库用户有UPDATE权限
3. **字段不存在**: 先执行 `add_content_summary_fields.sql` 添加字段
4. **内存不足**: 对于大量数据，可以考虑分批处理

## 清理

执行完成后，可以删除这些临时脚本文件：

```bash
rm temp/generate_summaries.py
rm temp/quick_summary_update.py
rm temp/update_summaries.sql
rm temp/README_summary_scripts.md
rm temp/generate_summaries.log  # 如果生成了日志文件
```
