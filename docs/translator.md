# 翻译工具使用说明

## 概述

翻译工具类支持百度翻译和谷歌翻译API，默认使用百度翻译。提供了简单易用的接口来进行文本翻译。

## 功能特性

- 支持百度翻译API和谷歌翻译API
- 自动语言检测
- 批量翻译
- 错误处理和重试机制
- 配置文件支持
- 便捷函数接口

## 安装依赖

```bash
pip install requests pyyaml
```

## 快速开始

### 基本使用

```python
from src.crawler.utils.translator import Translator

# 创建百度翻译器
translator = Translator("baidu", 
                       app_id="20251002002468098", 
                       secret_key="h1Xn1ChdNWG7Xw15fbgy")

# 翻译文本
result = translator.translate("Hello, world!", "auto", "zh")
print(result)  # 输出: 你好，世界！
```

### 使用便捷函数

```python
from src.crawler.utils.translator import translate_text

# 快速翻译
result = translate_text("Good morning!", "auto", "zh", "baidu",
                       app_id="20251002002468098",
                       secret_key="h1Xn1ChdNWG7Xw15fbgy")
print(result)
```

### 使用配置文件

```python
from src.crawler.utils.translator_config import create_translator_from_config

# 从配置文件创建翻译器
translator = create_translator_from_config()
result = translator.translate("Hello!", "auto", "zh")
```

## 配置说明

### 配置文件 (config/translator.yaml)

```yaml
translator:
  default_provider: "baidu"
  
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    api_url: "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
  google:
    api_key: "your_google_api_key"
    api_url: "https://translation.googleapis.com/language/translate/v2"
    
  settings:
    default_from_lang: "auto"
    default_to_lang: "zh"
    timeout: 10
    retry_count: 3
    retry_interval: 1
```

## API 参考

### Translator 类

#### 初始化

```python
Translator(provider="baidu", **kwargs)
```

**参数:**
- `provider`: 翻译服务提供商 ("baidu" 或 "google")
- `**kwargs`: 配置参数

#### 方法

##### translate(text, from_lang="auto", to_lang="zh")

翻译单个文本。

**参数:**
- `text`: 要翻译的文本
- `from_lang`: 源语言代码 (默认: "auto")
- `to_lang`: 目标语言代码 (默认: "zh")

**返回:** 翻译结果字符串

##### batch_translate(texts, from_lang="auto", to_lang="zh")

批量翻译文本列表。

**参数:**
- `texts`: 要翻译的文本列表
- `from_lang`: 源语言代码
- `to_lang`: 目标语言代码

**返回:** 翻译结果列表

##### detect_language(text)

检测文本语言。

**参数:**
- `text`: 要检测的文本

**返回:** 检测到的语言代码

### 便捷函数

#### create_translator(provider="baidu", **kwargs)

创建翻译器实例的便捷函数。

#### translate_text(text, from_lang="auto", to_lang="zh", provider="baidu", **kwargs)

快速翻译文本的便捷函数。

## 语言代码

### 百度翻译支持的语言代码

- `auto`: 自动检测
- `zh`: 中文
- `en`: 英语
- `jp`: 日语
- `kor`: 韩语
- `fra`: 法语
- `spa`: 西班牙语
- `th`: 泰语
- `ara`: 阿拉伯语
- `ru`: 俄语
- `pt`: 葡萄牙语
- `de`: 德语
- `it`: 意大利语
- `el`: 希腊语
- `nl`: 荷兰语
- `pl`: 波兰语
- `bul`: 保加利亚语
- `est`: 爱沙尼亚语
- `dan`: 丹麦语
- `fin`: 芬兰语
- `cs`: 捷克语
- `rom`: 罗马尼亚语
- `slo`: 斯洛文尼亚语
- `swe`: 瑞典语
- `hu`: 匈牙利语
- `cht`: 繁体中文
- `vie`: 越南语

### 谷歌翻译支持的语言代码

- `auto`: 自动检测
- `zh`: 中文
- `en`: 英语
- `ja`: 日语
- `ko`: 韩语
- `fr`: 法语
- `es`: 西班牙语
- `th`: 泰语
- `ar`: 阿拉伯语
- `ru`: 俄语
- `pt`: 葡萄牙语
- `de`: 德语
- `it`: 意大利语
- `el`: 希腊语
- `nl`: 荷兰语
- `pl`: 波兰语
- `bg`: 保加利亚语
- `et`: 爱沙尼亚语
- `da`: 丹麦语
- `fi`: 芬兰语
- `cs`: 捷克语
- `ro`: 罗马尼亚语
- `sl`: 斯洛文尼亚语
- `sv`: 瑞典语
- `hu`: 匈牙利语
- `vi`: 越南语

## 使用示例

### 示例1: 基本翻译

```python
from src.crawler.utils.translator import Translator

# 创建翻译器
translator = Translator("baidu", 
                       app_id="20251002002468098", 
                       secret_key="h1Xn1ChdNWG7Xw15fbgy")

# 翻译英文到中文
result = translator.translate("Hello, world!", "en", "zh")
print(result)  # 你好，世界！

# 翻译中文到英文
result = translator.translate("你好，世界！", "zh", "en")
print(result)  # Hello, world!
```

### 示例2: 批量翻译

```python
# 批量翻译
texts = ["Hello", "World", "Python", "Programming"]
results = translator.batch_translate(texts, "en", "zh")
for original, translated in zip(texts, results):
    print(f"{original} -> {translated}")
```

### 示例3: 语言检测

```python
# 检测语言
text = "Bonjour le monde!"
detected = translator.detect_language(text)
print(f"检测到的语言: {detected}")

# 自动翻译
result = translator.translate(text, "auto", "zh")
print(f"翻译结果: {result}")
```

### 示例4: 错误处理

```python
# 翻译失败时会返回原文
translator = Translator("baidu", app_id="wrong", secret_key="wrong")
result = translator.translate("This will fail", "auto", "zh")
print(result)  # 输出原文: This will fail
```

## 运行演示

```bash
python scripts/translator_demo.py
```

## 注意事项

1. 确保网络连接正常
2. 百度翻译API需要有效的app_id和secret_key
3. 谷歌翻译API需要有效的api_key
4. 翻译结果可能因网络状况而有所不同
5. 建议在生产环境中添加适当的错误处理和重试机制

## 故障排除

### 常见问题

1. **API密钥错误**: 检查配置文件中的API密钥是否正确
2. **网络连接问题**: 确保网络连接正常，可以访问翻译API
3. **请求频率限制**: 如果遇到频率限制，可以添加延迟或使用重试机制
4. **编码问题**: 确保文本编码为UTF-8

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 现在会显示详细的调试信息
translator = Translator("baidu", app_id="...", secret_key="...")
result = translator.translate("Hello", "auto", "zh")
```
