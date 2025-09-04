"""
测试网站访问
"""

import requests
import time

def test_website():
    """测试网站访问"""
    url = "https://bbs.boniu123.cc/forum-89-1.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"正在访问: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('content-type', 'N/A')}")
        print(f"内容长度: {len(response.content)} 字节")
        
        # 检查响应头
        print("\n响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # 尝试解码内容
        try:
            content = response.content.decode('utf-8')
            print(f"\nUTF-8解码成功，内容长度: {len(content)} 字符")
            print("内容预览:")
            print(content[:500])
        except UnicodeDecodeError:
            try:
                content = response.content.decode('gbk')
                print(f"\nGBK解码成功，内容长度: {len(content)} 字符")
                print("内容预览:")
                print(content[:500])
            except UnicodeDecodeError:
                print("\n无法解码内容，可能是压缩或加密")
                print("原始内容预览:")
                print(response.content[:100])
        
        # 保存原始内容
        with open("data/raw_response.bin", "wb") as f:
            f.write(response.content)
        print("\n原始响应已保存到 data/raw_response.bin")
        
    except Exception as e:
        print(f"访问失败: {e}")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    test_website()
