# 翻译功能实现文档

## 实现概述

本文档详细说明了爬虫系统中翻译功能的实现细节。

## 架构设计

```
┌─────────────────────────────────────────────────┐
│            爬虫系统（BoniuCrawler）              │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  1. 爬取帖子数据                         │  │
│  │     - 标题（title）                      │  │
│  │     - 内容（content）                    │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  2. 翻译数据                             │  │
│  │     - 调用翻译器（Translator）           │  │
│  │     - 生成title_en和content_en           │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  3. 保存到数据库                         │  │
│  │     - 原始中文字段                       │  │
│  │     - 翻译后的英文字段                   │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│        历史数据翻译（HistoryDataTranslator）     │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  1. 查询未翻译数据                       │  │
│  │     - title_en为空的记录                 │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  2. 批量翻译                             │  │
│  │     - 分批处理                           │  │
│  │     - 延迟控制                           │  │
│  └──────────────────────────────────────────┘  │
│                     ↓                           │
│  ┌──────────────────────────────────────────┐  │
│  │  3. 更新数据库                           │  │
│  │     - 批量更新翻译字段                   │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 核心组件

### 1. 翻译器（Translator）

**文件**: `src/crawler/utils/translator.py`

**功能**:
- 支持百度翻译和谷歌翻译API
- 自动语言检测
- 错误处理和重试
- 批量翻译支持

**关键方法**:
```python
def translate(text: str, from_lang: str = "auto", to_lang: str = "zh") -> str
def batch_translate(texts: list, from_lang: str = "auto", to_lang: str = "zh") -> list
def detect_language(text: str) -> str
```

### 2. 翻译配置管理（TranslatorConfig）

**文件**: `src/crawler/utils/translator_config.py`

**功能**:
- 加载配置文件
- 管理API密钥
- 提供便捷的配置访问接口

**关键方法**:
```python
def get_provider_config(provider: str) -> Dict[str, Any]
def get_default_provider() -> str
def create_translator_from_config(provider: Optional[str] = None)
```

### 3. 爬虫集成（BoniuCrawler）

**文件**: `src/crawler/sites/boniu/crawler.py`

**修改内容**:

#### 初始化翻译器
```python
def __init__(self):
    # ... 其他初始化代码 ...
    
    # 初始化翻译器
    try:
        self.translator = create_translator_from_config()
        self.enable_translation = True
        if self.logger:
            self.logger.info("翻译器初始化成功")
    except Exception as e:
        self.translator = None
        self.enable_translation = False
        if self.logger:
            self.logger.warning(f"翻译器初始化失败: {e}，翻译功能已禁用")
```

#### 翻译方法
```python
def _translate_text(self, text: str, from_lang: str = "zh", to_lang: str = "en") -> str:
    """翻译文本"""
    if not self.enable_translation or not self.translator or not text:
        return ""
    
    try:
        result = self.translator.translate(text, from_lang, to_lang)
        return result
    except Exception as e:
        if self.logger:
            self.logger.error(f"翻译失败: {e}")
        return ""
```

#### 插入数据时自动翻译
```python
def _insert_posts(self, posts: List[Dict[str, Any]], overwrite: bool = False) -> int:
    # ... 其他代码 ...
    
    # 翻译标题和内容
    title = (p.get('title') or '')[:255]
    content = (p.get('content') or '')[:65535]
    
    title_en = p.get('title_en') or ''
    content_en = p.get('content_en') or ''
    
    # 如果没有提供翻译，尝试自动翻译
    if self.enable_translation and title and not title_en:
        title_en = self._translate_text(title, 'zh', 'en')
    
    if self.enable_translation and content and not content_en:
        content_to_translate = content[:1000] if len(content) > 1000 else content
        content_en = self._translate_text(content_to_translate, 'zh', 'en')
    
    # ... 保存到数据库 ...
```

### 4. 历史数据翻译（HistoryDataTranslator）

**文件**: `scripts/translate_history_data.py`

**功能**:
- 查询未翻译的记录
- 批量翻译历史数据
- 更新数据库
- 提供统计信息

**关键方法**:
```python
def get_untranslated_posts(limit: int = None, offset: int = 0) -> List[Dict[str, Any]]
def translate_text(text: str, from_lang: str = "zh", to_lang: str = "en") -> str
def update_translated_posts(posts: List[Dict[str, Any]]) -> int
def translate_batch(batch_size: int = 10, delay: float = 1.0, max_records: int = None) -> int
def get_translation_statistics() -> Dict[str, int]
```

### 5. CLI命令集成

**文件**: `src/cli/main.py`

**新增命令**:

#### crawl命令（已有，增强了翻译功能）
```bash
python main.py crawl --env dev --pages 2
```

#### translate命令（新增）
```bash
python main.py translate --env dev --batch-size 10 --delay 1.0
```

## 数据库设计

### 新增字段

```sql
-- 英文标题字段
title_en VARCHAR(255) DEFAULT NULL COMMENT '英文标题'

-- 英文内容字段
content_en TEXT DEFAULT NULL COMMENT '英文内容'

-- 索引
CREATE INDEX idx_title_en ON ims_mdkeji_im_boniu_forum_post (title_en);
```

### 表结构
```
ims_mdkeji_im_boniu_forum_post
├── forum_post_id (主键)
├── title (中文标题)
├── title_en (英文标题) ← 新增
├── content (中文内容)
├── content_en (英文内容) ← 新增
├── ... (其他字段)
```

## 翻译流程

### 流程1: 爬取时自动翻译

```
1. 爬虫爬取帖子数据
   ↓
2. 检查翻译器是否启用
   ↓
3. 如果启用，翻译title和content
   ↓
4. 保存原始数据和翻译结果到数据库
   ↓
5. 记录日志
```

### 流程2: 批量翻译历史数据

```
1. 查询未翻译的记录（title_en为空）
   ↓
2. 分批读取数据
   ↓
3. 对每条记录进行翻译
   ↓
4. 批量更新到数据库
   ↓
5. 延迟后处理下一批
   ↓
6. 显示进度和统计
```

## 配置说明

### 配置文件: config/translator.yaml

```yaml
translator:
  # 默认翻译服务提供商
  default_provider: "baidu"
  
  # 百度翻译配置
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    api_url: "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
  # 谷歌翻译配置
  google:
    api_key: ""
    api_url: "https://translation.googleapis.com/language/translate/v2"
    
  # 通用设置
  settings:
    default_from_lang: "auto"
    default_to_lang: "zh"
    timeout: 10
    retry_count: 3
    retry_interval: 1
```

## 错误处理

### 1. 翻译失败处理

```python
# 翻译失败时返回空字符串，不影响数据保存
try:
    result = self.translator.translate(text, from_lang, to_lang)
    return result
except Exception as e:
    if self.logger:
        self.logger.error(f"翻译失败: {e}")
    return ""
```

### 2. API限制处理

```python
# 批量翻译时添加延迟
for i, post in enumerate(posts, 1):
    # 翻译...
    if i < len(posts):
        time.sleep(0.5)  # 每条记录之间延迟0.5秒

# 批次之间延迟
time.sleep(delay)  # 可配置的延迟时间
```

### 3. 数据库异常处理

```python
try:
    affected = executemany(sql, rows)
    print(f"更新了 {affected} 条记录")
except Exception as e:
    print(f"数据库更新失败: {e}")
```

## 性能优化

### 1. 长文本处理

对于长文本（>1000字符），只翻译前1000字符：

```python
content_to_translate = content[:1000] if len(content) > 1000 else content
content_en = self._translate_text(content_to_translate, 'zh', 'en')
```

### 2. 批量处理

使用批量SQL更新减少数据库交互：

```python
sql = "UPDATE ... WHERE forum_post_id = %s"
executemany(sql, rows)  # 批量执行
```

### 3. 延迟控制

通过可配置的延迟避免API频率限制：

```python
time.sleep(delay)  # 批次之间延迟
time.sleep(0.5)    # 记录之间延迟
```

## 测试验证

### 测试脚本

**文件**: `scripts/test_translation_integration.py`

**测试内容**:
1. 翻译器初始化测试
2. 翻译功能测试
3. 爬虫集成测试
4. 翻译方法测试

**运行方式**:
```bash
python scripts/test_translation_integration.py
```

## 监控和日志

### 日志记录

```python
# 翻译器初始化日志
self.logger.info("翻译器初始化成功")

# 翻译过程日志
self.logger.info(f"翻译标题: {title[:50]} -> {title_en[:50]}")
self.logger.info(f"翻译内容: {len(content)} 字符")

# 错误日志
self.logger.error(f"翻译失败: {e}")
```

### 日志位置

```
logs/
└── YYYY/
    └── MM/
        └── DD.log
```

## 扩展性设计

### 1. 支持多种翻译服务

通过配置文件切换翻译服务提供商：

```yaml
translator:
  default_provider: "baidu"  # 或 "google"
```

### 2. 可插拔的翻译器

爬虫通过配置文件加载翻译器，支持动态切换：

```python
self.translator = create_translator_from_config()
```

### 3. 灵活的翻译策略

可以根据需要调整翻译策略：
- 完整翻译或部分翻译
- 同步翻译或异步翻译
- 立即翻译或延迟翻译

## 依赖关系

```
BoniuCrawler
    ↓
create_translator_from_config()
    ↓
TranslatorConfig
    ↓
Translator (baidu/google)
    ↓
Translation API
```

## 未来改进方向

1. **异步翻译**: 使用异步IO提高翻译效率
2. **缓存机制**: 对已翻译的文本进行缓存
3. **质量检查**: 添加翻译质量评估
4. **多语言支持**: 支持翻译成多种语言
5. **智能分段**: 对长文本进行智能分段翻译
6. **并发处理**: 使用多线程或多进程加速翻译

## 相关文档

- [翻译功能使用指南](translation_guide.md)
- [快速开始](../TRANSLATION_QUICKSTART.md)
- [翻译工具文档](translator.md)
- [API文档](api.md)
