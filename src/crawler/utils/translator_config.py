"""
翻译配置加载器
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class TranslatorConfig:
    """翻译配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config/translator.yaml
        """
        if config_path is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            config_path = project_root / "config" / "translator.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        获取指定翻译服务提供商的配置
        
        Args:
            provider: 翻译服务提供商名称
            
        Returns:
            配置字典
        """
        translator_config = self._config.get('translator', {})
        return translator_config.get(provider, {})
    
    def get_default_provider(self) -> str:
        """获取默认翻译服务提供商"""
        translator_config = self._config.get('translator', {})
        return translator_config.get('default_provider', 'baidu')
    
    def get_settings(self) -> Dict[str, Any]:
        """获取翻译设置"""
        translator_config = self._config.get('translator', {})
        return translator_config.get('settings', {})
    
    def get_baidu_config(self) -> Dict[str, Any]:
        """获取百度翻译配置"""
        return self.get_provider_config('baidu')
    
    def get_google_config(self) -> Dict[str, Any]:
        """获取谷歌翻译配置"""
        return self.get_provider_config('google')
    
    def update_config(self, provider: str, **kwargs):
        """
        更新配置
        
        Args:
            provider: 翻译服务提供商
            **kwargs: 要更新的配置项
        """
        if 'translator' not in self._config:
            self._config['translator'] = {}
        
        if provider not in self._config['translator']:
            self._config['translator'][provider] = {}
        
        self._config['translator'][provider].update(kwargs)
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"保存配置文件失败: {e}")


# 全局配置实例
_config_instance = None


def get_config() -> TranslatorConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = TranslatorConfig()
    return _config_instance


def create_translator_from_config(provider: Optional[str] = None):
    """
    从配置文件创建翻译器
    
    Args:
        provider: 翻译服务提供商，如果为None则使用默认配置
        
    Returns:
        翻译器实例
    """
    from .translator import Translator
    
    config = get_config()
    
    if provider is None:
        provider = config.get_default_provider()
    
    provider_config = config.get_provider_config(provider)
    
    return Translator(provider, **provider_config)
