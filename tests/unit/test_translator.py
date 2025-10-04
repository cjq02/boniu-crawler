# -*- coding: utf-8 -*-
"""
翻译工具测试
"""

import pytest
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.crawler.utils.translator import Translator, translate_text


class TestTranslator:
    """翻译工具测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.translator = Translator("baidu", 
                                   app_id="20251002002468098", 
                                   secret_key="h1Xn1ChdNWG7Xw15fbgy")
    
    def test_translate_english_to_chinese(self):
        """测试英文翻译为中文"""
        result = self.translator.translate("Hello", "en", "zh")
        assert result is not None
        assert len(result) > 0
        print(f"Hello -> {result}")
    
    def test_translate_chinese_to_english(self):
        """测试中文翻译为英文"""
        result = self.translator.translate("你好", "zh", "en")
        assert result is not None
        assert len(result) > 0
        print(f"你好 -> {result}")
    
    def test_auto_detect_language(self):
        """测试自动语言检测"""
        result = self.translator.translate("Hello", "auto", "zh")
        assert result is not None
        assert len(result) > 0
        print(f"自动检测 Hello -> {result}")
    
    def test_batch_translate(self):
        """测试批量翻译"""
        texts = ["Hello", "World", "Python"]
        results = self.translator.batch_translate(texts, "en", "zh")
        assert len(results) == len(texts)
        for i, result in enumerate(results):
            assert result is not None
            print(f"{texts[i]} -> {result}")
    
    def test_empty_text(self):
        """测试空文本"""
        result = self.translator.translate("", "auto", "zh")
        assert result == ""
    
    def test_whitespace_text(self):
        """测试空白文本"""
        result = self.translator.translate("   ", "auto", "zh")
        assert result == "   "
    
    def test_error_handling(self):
        """测试错误处理"""
        # 使用错误的配置
        bad_translator = Translator("baidu", app_id="wrong", secret_key="wrong")
        result = bad_translator.translate("Hello", "auto", "zh")
        # 翻译失败时应该返回原文
        assert result == "Hello"
    
    def test_quick_translate_function(self):
        """测试快速翻译函数"""
        result = translate_text("Good morning!", "auto", "zh", "baidu",
                              app_id="20251002002468098",
                              secret_key="h1Xn1ChdNWG7Xw15fbgy")
        assert result is not None
        assert len(result) > 0
        print(f"快速翻译: Good morning! -> {result}")


if __name__ == "__main__":
    # 运行测试
    test = TestTranslator()
    test.setup_method()
    
    print("开始翻译工具测试...")
    print("=" * 50)
    
    try:
        test.test_translate_english_to_chinese()
        test.test_translate_chinese_to_english()
        test.test_auto_detect_language()
        test.test_batch_translate()
        test.test_empty_text()
        test.test_whitespace_text()
        test.test_error_handling()
        test.test_quick_translate_function()
        
        print("=" * 50)
        print("所有测试通过！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
