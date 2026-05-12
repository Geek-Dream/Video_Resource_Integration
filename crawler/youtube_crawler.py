"""YouTube爬虫"""

from typing import List, Dict, Any
from .base_crawler import BaseCrawler
from utils import logger
from utils.helpers import format_duration


class YouTubeCrawler(BaseCrawler):
    """YouTube公开视频爬虫"""

    def __init__(self):
        super().__init__()
        self.name = "YouTube"

    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索YouTube视频（使用yt-dlp）"""
        videos = []
        try:
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
                'default_search': 'ytsearch',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(
                    f"ytsearch{limit}:{keyword}",
                    download=False
                )

                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            video = self._parse_entry(entry)
                            if video:
                                videos.append(video)

            logger.info(f"[YouTube] 搜索 '{keyword}' 找到 {len(videos)} 个视频")

        except Exception as e:
            logger.error(f"[YouTube] 搜索失败: {e}")

        return videos

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取YouTube视频详细信息"""
        try:
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._parse_entry(info)

        except Exception as e:
            logger.error(f"[YouTube] 获取视频信息失败 {url}: {e}")
            return {}

    def _parse_entry(self, entry: dict) -> Dict[str, Any]:
        """解析视频条目"""
        if not entry:
            return {}

        duration = entry.get('duration', 0) or 0
        return {
            'title': entry.get('title', 'Unknown'),
            'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
            'cover_url': entry.get('thumbnail'),
            'duration': int(duration),
            'duration_text': format_duration(int(duration)),
            'source': 'youtube',
            'video_type': 'mp4',
            'file_size': 0,
            'description': entry.get('description'),
            'author': entry.get('uploader') or entry.get('channel')
        }
