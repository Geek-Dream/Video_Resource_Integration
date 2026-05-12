"""Internet Archive爬虫"""

from typing import List, Dict, Any
from .base_crawler import BaseCrawler
from utils import logger
from utils.helpers import format_duration


class ArchiveCrawler(BaseCrawler):
    """Internet Archive公开视频爬虫"""

    BASE_URL = "https://archive.org/advancedsearch.php"
    API_URL = "https://archive.org/metadata"

    def __init__(self):
        super().__init__()
        self.name = "Archive"

    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索Internet Archive视频"""
        videos = []
        try:
            params = {
                'q': f'{keyword} AND mediatype:movies',
                'fl[]': 'identifier,title,description,creator,runtime',
                'sort[]': 'downloads desc',
                'rows': limit,
                'page': 1,
                'output': 'json'
            }

            resp = self._make_request(self.BASE_URL, params=params)
            data = resp.json()

            for doc in data.get('response', {}).get('docs', []):
                video = self._parse_doc(doc)
                if video:
                    videos.append(video)

            logger.info(f"[Archive] 搜索 '{keyword}' 找到 {len(videos)} 个视频")

        except Exception as e:
            logger.error(f"[Archive] 搜索失败: {e}")

        return videos

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取Archive视频详细信息"""
        try:
            # 从URL提取identifier
            identifier = self._extract_identifier(url)
            if not identifier:
                return {}

            resp = self._make_request(f"{self.API_URL}/{identifier}")
            data = resp.json()

            metadata = data.get('metadata', {})
            files = data.get('files', [])

            # 查找视频文件
            video_file = self._find_video_file(files)
            if not video_file:
                return {}

            video_url = f"https://archive.org/download/{identifier}/{video_file['name']}"

            return {
                'title': metadata.get('title', ['Unknown'])[0] if isinstance(metadata.get('title'), list) else metadata.get('title', 'Unknown'),
                'url': video_url,
                'cover_url': f"https://archive.org/services/img/{identifier}",
                'duration': self._parse_duration(metadata.get('runtime', ['0'])[0] if isinstance(metadata.get('runtime'), list) else metadata.get('runtime', '0')),
                'duration_text': metadata.get('runtime', ['00:00:00'])[0] if isinstance(metadata.get('runtime'), list) else metadata.get('runtime', '00:00:00'),
                'source': 'archive',
                'video_type': video_file.get('format', 'mp4').lower(),
                'file_size': int(video_file.get('size', 0)),
                'description': metadata.get('description', [''])[0] if isinstance(metadata.get('description'), list) else metadata.get('description', ''),
                'author': metadata.get('creator', ['Unknown'])[0] if isinstance(metadata.get('creator'), list) else metadata.get('creator', 'Unknown')
            }

        except Exception as e:
            logger.error(f"[Archive] 获取视频信息失败 {url}: {e}")
            return {}

    def _parse_doc(self, doc: dict) -> Dict[str, Any]:
        """解析搜索结果条目"""
        identifier = doc.get('identifier')
        if not identifier:
            return {}

        return {
            'title': doc.get('title', 'Unknown'),
            'url': f"https://archive.org/details/{identifier}",
            'cover_url': f"https://archive.org/services/img/{identifier}",
            'duration': self._parse_duration(doc.get('runtime', '0')),
            'duration_text': doc.get('runtime', '00:00:00'),
            'source': 'archive',
            'video_type': 'mp4',
            'file_size': 0,
            'description': doc.get('description', ''),
            'author': doc.get('creator', 'Unknown')
        }

    def _find_video_file(self, files: list) -> dict:
        """查找视频文件"""
        video_formats = ['.mp4', '.ogv', '.avi', '.mov', '.mkv']
        for f in files:
            name = f.get('name', '').lower()
            if any(name.endswith(fmt) for fmt in video_formats):
                return f
        return {}

    def _extract_identifier(self, url: str) -> str:
        """从URL提取identifier"""
        import re
        match = re.search(r'archive\.org/details/([^/]+)', url)
        return match.group(1) if match else None

    def _parse_duration(self, runtime: str) -> int:
        """解析时长字符串为秒数"""
        try:
            parts = str(runtime).split(':')
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return int(runtime)
        except:
            return 0
