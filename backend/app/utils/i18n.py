import json
import os
from typing import Dict, Any
from pathlib import Path

class I18n:
    def __init__(self, locale: str = "zh-CN"):
        self.locale = locale
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Any]:
        """加载翻译文件"""
        translations = {}
        locales_dir = Path(__file__).parent.parent.parent / "locales"
        
        for file_name in os.listdir(locales_dir):
            if file_name.endswith('.json'):
                lang_code = file_name.replace('.json', '')
                file_path = locales_dir / file_name
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Failed to load translation file {file_path}: {e}")
                    translations[lang_code] = {}
        
        return translations
    
    def set_locale(self, locale: str):
        """设置语言"""
        if locale in self.translations:
            self.locale = locale
        else:
            self.locale = "en-US"  # 默认英文
    
    def t(self, key: str, **kwargs) -> str:
        """翻译函数"""
        keys = key.split('.')
        translation = self.translations.get(self.locale, {})
        
        try:
            for k in keys:
                translation = translation[k]
            
            # 替换参数
            if kwargs:
                for key, value in kwargs.items():
                    translation = translation.replace(f"{{{key}}}", str(value))
            
            return translation
        except (KeyError, TypeError):
            # 如果找不到翻译，尝试英文
            if self.locale != "en-US":
                en_translation = self.translations.get("en-US", {})
                try:
                    for k in keys:
                        en_translation = en_translation[k]
                    return en_translation
                except (KeyError, TypeError):
                    pass
            return key  # 返回原始key

# 全局i18n实例
i18n = I18n()

def get_i18n(lang: str = None):
    """获取i18n实例"""
    if lang:
        instance = I18n(lang)
        return instance
    return i18n