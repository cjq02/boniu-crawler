"""
翻译工具类
支持百度翻译和谷歌翻译API
默认使用百度翻译
"""

import hashlib
import random
import time
import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


class Translator:
    """翻译工具类"""
    
    def __init__(self, provider: str = "baidu", **kwargs):
        """
        初始化翻译器
        
        Args:
            provider: 翻译服务提供商 ("baidu" 或 "google")
            **kwargs: 其他配置参数
        """
        self.provider = provider.lower()
        self.config = kwargs
        
        if self.provider == "baidu":
            self._init_baidu()
        elif self.provider == "google":
            self._init_google()
        else:
            raise ValueError(f"不支持的翻译服务提供商: {provider}")
    
    def _init_baidu(self):
        """初始化百度翻译配置"""
        self.app_id = self.config.get('app_id', '20251002002468098')
        self.secret_key = self.config.get('secret_key', 'h1Xn1ChdNWG7Xw15fbgy')
        self.api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        
        if not self.app_id or not self.secret_key:
            raise ValueError("百度翻译需要提供 app_id 和 secret_key")
    
    def _init_google(self):
        """初始化谷歌翻译配置"""
        self.api_key = self.config.get('api_key')
        self.api_url = "https://translation.googleapis.com/language/translate/v2"
        
        if not self.api_key:
            raise ValueError("谷歌翻译需要提供 api_key")
    
    def translate(self, text: str, from_lang: str = "auto", to_lang: str = "zh") -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            from_lang: 源语言 (百度: auto/zh/en等, 谷歌: auto/zh/en等)
            to_lang: 目标语言 (百度: zh/en等, 谷歌: zh/en等)
            
        Returns:
            翻译结果
        """
        if not text.strip():
            return text
        
        try:
            if self.provider == "baidu":
                return self._translate_baidu(text, from_lang, to_lang)
            elif self.provider == "google":
                return self._translate_google(text, from_lang, to_lang)
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text  # 翻译失败时返回原文
    
    def _translate_baidu(self, text: str, from_lang: str, to_lang: str) -> str:
        """百度翻译实现"""
        # 生成签名
        salt = str(int(time.time() * 1000))
        sign_str = self.app_id + text + salt + self.secret_key
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.app_id,
            'salt': salt,
            'sign': sign
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                raise Exception(f"百度翻译API错误: {error_msg}")
            
            if 'trans_result' in result and result['trans_result']:
                return result['trans_result'][0]['dst']
            else:
                return text
                
        except requests.RequestException as e:
            raise Exception(f"百度翻译请求失败: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"百度翻译响应解析失败: {e}")
    
    def _translate_google(self, text: str, from_lang: str, to_lang: str) -> str:
        """谷歌翻译实现"""
        params = {
            'key': self.api_key,
            'q': text,
            'source': from_lang,
            'target': to_lang,
            'format': 'text'
        }
        
        try:
            response = requests.post(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                error_msg = result['error'].get('message', '未知错误')
                raise Exception(f"谷歌翻译API错误: {error_msg}")
            
            if 'data' in result and 'translations' in result['data']:
                translations = result['data']['translations']
                if translations:
                    return translations[0]['translatedText']
            
            return text
            
        except requests.RequestException as e:
            raise Exception(f"谷歌翻译请求失败: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"谷歌翻译响应解析失败: {e}")
    
    def batch_translate(self, texts: list, from_lang: str = "auto", to_lang: str = "zh") -> list:
        """
        批量翻译
        
        Args:
            texts: 要翻译的文本列表
            from_lang: 源语言
            to_lang: 目标语言
            
        Returns:
            翻译结果列表
        """
        results = []
        for text in texts:
            translated = self.translate(text, from_lang, to_lang)
            results.append(translated)
        return results
    
    def detect_language(self, text: str) -> str:
        """
        检测语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的语言代码
        """
        if self.provider == "baidu":
            return self._detect_language_baidu(text)
        elif self.provider == "google":
            return self._detect_language_google(text)
        else:
            return "auto"
    
    def _detect_language_baidu(self, text: str) -> str:
        """百度语言检测"""
        # 百度翻译API的语言检测
        try:
            result = self._translate_baidu(text, "auto", "zh")
            # 这里简化处理，实际应该调用百度语言检测API
            return "auto"
        except:
            return "auto"
    
    def _detect_language_google(self, text: str) -> str:
        """谷歌语言检测"""
        try:
            # 使用谷歌翻译API的语言检测功能
            params = {
                'key': self.api_key,
                'q': text
            }
            
            response = requests.post(
                "https://translation.googleapis.com/language/translate/v2/detect",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if 'data' in result and 'detections' in result['data']:
                detections = result['data']['detections'][0]
                if detections:
                    return detections[0]['language']
            
            return "auto"
        except:
            return "auto"


# 便捷函数
def create_translator(provider: str = "baidu", **kwargs) -> Translator:
    """
    创建翻译器实例的便捷函数
    
    Args:
        provider: 翻译服务提供商
        **kwargs: 配置参数
        
    Returns:
        翻译器实例
    """
    return Translator(provider, **kwargs)


def translate_text(text: str, from_lang: str = "auto", to_lang: str = "zh", 
                   provider: str = "baidu", **kwargs) -> str:
    """
    快速翻译文本的便捷函数
    
    Args:
        text: 要翻译的文本
        from_lang: 源语言
        to_lang: 目标语言
        provider: 翻译服务提供商
        **kwargs: 配置参数
        
    Returns:
        翻译结果
    """
    translator = create_translator(provider, **kwargs)
    return translator.translate(text, from_lang, to_lang)


# 默认配置
DEFAULT_BAIDU_CONFIG = {
    'app_id': '20251002002468098',
    'secret_key': 'h1Xn1ChdNWG7Xw15fbgy'
}

# 使用示例
if __name__ == "__main__":
    # 使用百度翻译
    translator = Translator("baidu", **DEFAULT_BAIDU_CONFIG)
    
    # 翻译文本
    result = translator.translate("Hello, world!", "auto", "zh")
    print(f"翻译结果: {result}")
    
    # 批量翻译
    texts = ["Hello", "World", "Python"]
    results = translator.batch_translate(texts, "auto", "zh")
    print(f"批量翻译结果: {results}")
    
    # 使用配置文件创建翻译器
    try:
        from .translator_config import create_translator_from_config
        config_translator = create_translator_from_config()
        result = config_translator.translate("Hello, world!", "auto", "zh")
        print(f"使用配置文件的翻译结果: {result}")
    except ImportError:
        print("配置文件模块未找到，跳过配置测试")
