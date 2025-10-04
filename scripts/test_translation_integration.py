#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译功能集成
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

def test_translator():
    """测试翻译器"""
    print("=" * 60)
    print("测试1: 翻译器初始化")
    print("=" * 60)
    
    from src.crawler.utils.translator_config import create_translator_from_config
    
    try:
        translator = create_translator_from_config()
        print("✅ 翻译器初始化成功")
        
        # 测试翻译
        test_text = "你好，世界！"
        result = translator.translate(test_text, "zh", "en")
        print(f"翻译测试: {test_text} -> {result}")
        
    except Exception as e:
        print(f"❌ 翻译器初始化失败: {e}")
        return False
    
    return True


def test_crawler_integration():
    """测试爬虫集成"""
    print("\n" + "=" * 60)
    print("测试2: 爬虫翻译功能集成")
    print("=" * 60)
    
    try:
        from src.crawler.sites.boniu.crawler import BoniuCrawler
        
        crawler = BoniuCrawler()
        print(f"✅ 爬虫初始化成功")
        print(f"   翻译功能状态: {'已启用' if crawler.enable_translation else '未启用'}")
        
        if crawler.enable_translation:
            # 测试翻译方法
            test_text = "测试标题"
            result = crawler._translate_text(test_text, "zh", "en")
            print(f"   翻译方法测试: {test_text} -> {result}")
        
    except Exception as e:
        print(f"❌ 爬虫集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """主函数"""
    print("\n翻译功能集成测试")
    print("=" * 60)
    
    results = []
    
    # 测试翻译器
    results.append(("翻译器", test_translator()))
    
    # 测试爬虫集成
    results.append(("爬虫集成", test_crawler_integration()))
    
    # 显示结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！翻译功能已成功集成！")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
