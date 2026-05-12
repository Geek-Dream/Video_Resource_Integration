"""工具函数模块"""

import hashlib
import re
from urllib.parse import urlparse


def generate_hash(url: str) -> str:
    """生成URL的唯一哈希值"""
    return hashlib.md5(url.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """清理文件名中的非法字符"""
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    return re.sub(illegal_chars, '_', filename).strip()


def format_duration(seconds: int) -> str:
    """将秒数格式化为 HH:MM:SS"""
    if not seconds or seconds < 0:
        return "00:00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def extract_domain(url: str) -> str:
    """从URL中提取域名"""
    parsed = urlparse(url)
    return parsed.netloc


def is_valid_url(url: str) -> bool:
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_video_extension(url: str) -> str:
    """从URL中提取视频扩展名"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    if '.m3u8' in path:
        return 'm3u8'
    elif '.mp4' in path:
        return 'mp4'
    elif '.webm' in path:
        return 'webm'
    elif '.mkv' in path:
        return 'mkv'
    return 'unknown'
