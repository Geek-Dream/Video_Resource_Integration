"""视频信息解析器"""

import re
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import requests
from utils import logger
from utils.helpers import format_duration, get_video_extension


class VideoParser:
    """视频信息解析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def parse_direct_url(self, url: str, title: str = None) -> Dict[str, Any]:
        """解析直接视频链接"""
        video_type = get_video_extension(url)
        return {
            'title': title or self._extract_title_from_url(url),
            'url': url,
            'cover_url': None,
            'duration': 0,
            'duration_text': '00:00:00',
            'source': 'direct',
            'video_type': video_type,
            'file_size': 0,
            'description': None,
            'author': None
        }

    def parse_html_page(self, url: str) -> list:
        """从HTML页面提取视频资源"""
        videos = []
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 查找video标签
            for video_tag in soup.find_all('video'):
                video_info = self._extract_from_video_tag(video_tag, url)
                if video_info:
                    videos.append(video_info)

            # 查找source标签
            for source_tag in soup.find_all('source'):
                src = source_tag.get('src')
                if src and self._is_video_url(src):
                    videos.append(self.parse_direct_url(src))

            # 查找iframe中的视频
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src')
                if src and self._is_video_url(src):
                    videos.append(self.parse_direct_url(src))

            # 正则提取页面中的视频链接
            video_urls = re.findall(
                r'https?://[^\s<>"]+\.(?:mp4|m3u8|webm|mkv)',
                resp.text
            )
            for vurl in set(video_urls):
                videos.append(self.parse_direct_url(vurl))

        except Exception as e:
            logger.error(f"解析页面失败 {url}: {e}")

        return videos

    def _extract_from_video_tag(self, tag, base_url: str) -> Optional[Dict[str, Any]]:
        """从video标签提取信息"""
        src = tag.get('src')
        if not src:
            source = tag.find('source')
            if source:
                src = source.get('src')
        
        if not src:
            return None

        if not src.startswith('http'):
            from urllib.parse import urljoin
            src = urljoin(base_url, src)

        poster = tag.get('poster')
        title = tag.get('title') or tag.get('data-title')

        return {
            'title': title or self._extract_title_from_url(src),
            'url': src,
            'cover_url': poster,
            'duration': 0,
            'duration_text': '00:00:00',
            'source': 'direct',
            'video_type': get_video_extension(src),
            'file_size': 0,
            'description': None,
            'author': None
        }

    def _is_video_url(self, url: str) -> bool:
        """判断是否为视频URL"""
        video_patterns = ['.mp4', '.m3u8', '.webm', '.mkv', '.flv', '.avi']
        url_lower = url.lower()
        return any(p in url_lower for p in video_patterns)

    def _extract_title_from_url(self, url: str) -> str:
        """从URL中提取标题"""
        from urllib.parse import urlparse, unquote
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = path.split('/')[-1]
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        return filename or 'Unknown'
