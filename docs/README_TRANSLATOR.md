# 翻译工具使用说明

## 问题解决：中文乱码

如果您在Windows系统上遇到中文乱码问题，请按以下步骤解决：

### 方法1：设置PowerShell编码
```powershell
chcp 65001
```

### 方法2：使用Python脚本时设置编码
在Python脚本开头添加：
```python
# -*- coding: utf-8 -*-
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## 快速开始

### 1. 基本使用
```python
from src.crawler.utils.translator import Translator

# 创建翻译器
translator = Translator("baidu", 
                       app_id="20251002002468098", 
                       secret_key="h1Xn1ChdNWG7Xw15fbgy")

# 翻译文本
result = translator.translate("Hello, world!", "auto", "zh")
print(result)  # 输出: 你好，世界！
```

### 2. 批量翻译
```python
texts = ["Hello", "World", "Python"]
results = translator.batch_translate(texts, "en", "zh")
for original, translated in zip(texts, results):
    print(f"{original} -> {translated}")
```

### 3. 快速翻译函数
```python
from src.crawler.utils.translator import translate_text

result = translate_text("Good morning!", "auto", "zh", "baidu",
                       app_id="20251002002468098",
                       secret_key="h1Xn1ChdNWG7Xw15fbgy")
print(result)
```

## 运行演示

```bash
# 运行演示脚本
python scripts/translator_demo.py

# 运行测试
python tests/unit/test_translator.py
```

## 功能特性

- ✅ 支持百度翻译和谷歌翻译API
- ✅ 自动语言检测
- ✅ 批量翻译
- ✅ 错误处理和重试机制
- ✅ 配置文件支持
- ✅ 便捷函数接口
- ✅ 中文显示正常

## 配置说明

配置文件位置：`config/translator.yaml`

```yaml
translator:
  default_provider: "baidu"
  
  baidu:
    app_id: "20251002002468098"
    secret_key: "h1Xn1ChdNWG7Xw15fbgy"
    
  google:
    api_key: "your_google_api_key"
```

## 注意事项

1. 确保网络连接正常
2. 百度翻译API需要有效的app_id和secret_key
3. 如果遇到编码问题，请按照上述方法设置编码
4. 翻译结果可能因网络状况而有所不同

## 故障排除

### 中文乱码问题
- 在PowerShell中运行 `chcp 65001`
- 在Python脚本中设置UTF-8编码
- 确保终端支持UTF-8编码

### API错误
- 检查API密钥是否正确
- 确保网络连接正常
- 查看错误信息进行调试

翻译工具已经准备就绪，可以正常使用！
