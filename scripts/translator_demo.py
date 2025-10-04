#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译工具使用示例
"""

import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.crawler.utils.translator import Translator, create_translator, translate_text
from src.crawler.utils.translator_config import create_translator_from_config


def demo_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 使用默认配置创建百度翻译器
    translator = Translator("baidu", 
                          app_id="20251002002468098", 
                          secret_key="h1Xn1ChdNWG7Xw15fbgy")
    
    # 翻译单个文本
    text = "Hello, world!"
    result = translator.translate(text, "auto", "zh")
    print(f"原文: {text}")
    print(f"译文: {result}")
    print()
    
    # 批量翻译
    texts = ["Hello", "World", "Python", "Programming"]
    results = translator.batch_translate(texts, "auto", "zh")
    print("批量翻译:")
    for original, translated in zip(texts, results):
        print(f"  {original} -> {translated}")
    print()


def demo_quick_translate():
    """快速翻译示例"""
    print("=== 快速翻译示例 ===")
    
    # 使用便捷函数
    result = translate_text("Good morning!", "auto", "zh", "baidu",
                          app_id="20251002002468098",
                          secret_key="h1Xn1ChdNWG7Xw15fbgy")
    print(f"快速翻译: Good morning! -> {result}")
    print()


def demo_config_file():
    """配置文件示例"""
    print("=== 配置文件示例 ===")
    
    try:
        # 使用配置文件创建翻译器
        translator = create_translator_from_config()
        
        result = translator.translate("How are you?", "auto", "zh")
        print(f"使用配置文件的翻译: How are you? -> {result}")
        
    except Exception as e:
        print(f"配置文件示例失败: {e}")
    print()


def demo_language_detection():
    """语言检测示例"""
    print("=== 语言检测示例 ===")
    
    translator = Translator("baidu", 
                          app_id="20251002002468098", 
                          secret_key="h1Xn1ChdNWG7Xw15fbgy")
    
    test_texts = [
        "Hello, world!",
        "你好，世界！",
        "Bonjour le monde!",
        "Hola mundo!"
    ]
    
    for text in test_texts:
        detected = translator.detect_language(text)
        translated = translator.translate(text, "auto", "zh")
        print(f"原文: {text}")
        print(f"检测语言: {detected}")
        print(f"翻译: {translated}")
        print()


def demo_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    # 使用错误的配置
    translator = Translator("baidu", app_id="wrong_id", secret_key="wrong_key")
    
    # 翻译失败时会返回原文
    result = translator.translate("This should fail", "auto", "zh")
    print(f"错误处理测试: {result}")
    print()


if __name__ == "__main__":
    print("翻译工具演示")
    print("=" * 50)
    
    try:
        demo_basic_usage()
        demo_quick_translate()
        demo_config_file()
        demo_language_detection()
        demo_error_handling()
        
        print("演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
