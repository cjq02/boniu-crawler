"""工具模块单元测试"""

import pytest
from src.crawler.utils.parser import clean_text, extract_number, extract_url, is_valid_url
from src.crawler.utils.storage import generate_filename, chunk_list, remove_duplicates


class TestParserUtils:
    """解析工具测试"""
    
    def test_clean_text(self):
        """测试文本清理"""
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("") == ""
        assert clean_text(None) == ""
        assert clean_text("\n\t  test  \n\t") == "test"
    
    def test_extract_number(self):
        """测试数字提取"""
        assert extract_number("123") == 123.0
        assert extract_number("abc123def") == 123.0
        assert extract_number("12.5") == 12.5
        assert extract_number("no number") is None
        assert extract_number("") is None
        assert extract_number(None) is None
    
    def test_extract_url(self):
        """测试URL提取"""
        assert extract_url("Visit https://example.com for more info") == "https://example.com"
        assert extract_url("http://test.com") == "http://test.com"
        assert extract_url("no url here") is None
        assert extract_url("") is None
        assert extract_url(None) is None
    
    def test_is_valid_url(self):
        """测试URL验证"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://test.com/path") is True
        assert is_valid_url("invalid-url") is False
        assert is_valid_url("") is False


class TestStorageUtils:
    """存储工具测试"""
    
    def test_generate_filename(self):
        """测试文件名生成"""
        filename = generate_filename("test", "json")
        assert filename.startswith("test_")
        assert filename.endswith(".json")
        assert len(filename) > 10  # 包含时间戳
    
    def test_chunk_list(self):
        """测试列表分块"""
        lst = [1, 2, 3, 4, 5]
        chunks = chunk_list(lst, 2)
        assert chunks == [[1, 2], [3, 4], [5]]
        
        chunks = chunk_list(lst, 3)
        assert chunks == [[1, 2, 3], [4, 5]]
        
        chunks = chunk_list(lst, 10)
        assert chunks == [[1, 2, 3, 4, 5]]
    
    def test_remove_duplicates(self):
        """测试去重"""
        lst = [1, 2, 2, 3, 3, 3]
        assert remove_duplicates(lst) == [1, 2, 3]
        
        lst = [{"id": 1}, {"id": 2}, {"id": 1}]
        result = remove_duplicates(lst, "id")
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
