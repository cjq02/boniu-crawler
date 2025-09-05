"""pytest配置文件"""

import pytest
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_html():
    """示例HTML数据"""
    return """
    <html>
        <head><title>测试页面</title></head>
        <body>
            <tr>
                <td><a href="thread-123-1-1.html" class="s xst">测试帖子</a></td>
                <td><a href="space-uid-1.html" class="username">测试用户</a></td>
                <td><span class="replayNum">10</span></td>
                <td><span class="viewNum">100</span></td>
            </tr>
        </body>
    </html>
    """


@pytest.fixture
def sample_post_data():
    """示例帖子数据"""
    return {
        'id': '123',
        'title': '测试帖子',
        'url': 'https://bbs.boniu123.cc/thread-123-1-1.html',
        'username': '测试用户',
        'avatar_url': None,
        'publish_time': '2024-01-01 12:00:00',
        'reply_count': 10,
        'view_count': 100,
        'images': [],
        'category': '游戏包网',
        'is_sticky': False,
        'is_essence': False,
        'crawl_time': '2024-01-01 12:00:00'
    }
