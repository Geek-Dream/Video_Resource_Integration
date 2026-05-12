"""数据库管理器"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import Video, DownloadTask, db, init_db
from utils.helpers import generate_hash
from utils import logger


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        init_db()
        logger.info("数据库初始化完成")

    def add_video(self, video_data: Dict[str, Any]) -> Optional[Video]:
        """添加视频记录（自动去重）"""
        url_hash = generate_hash(video_data['url'])
        
        # 检查是否已存在
        existing = Video.get_or_none(Video.url_hash == url_hash)
        if existing:
            # 如果新标题更好（不是格式描述），更新旧记录
            new_title = video_data.get('title', '')
            if new_title and len(new_title) > len(existing.title):
                existing.title = new_title
                existing.save()
                logger.debug(f"更新标题: {new_title}")
            return existing
            return existing
        
        try:
            video = Video.create(
                url_hash=url_hash,
                title=video_data.get('title', 'Unknown'),
                url=video_data['url'],
                cover_url=video_data.get('cover_url'),
                duration=video_data.get('duration', 0),
                duration_text=video_data.get('duration_text', '00:00:00'),
                source=video_data.get('source', 'unknown'),
                video_type=video_data.get('video_type', 'unknown'),
                file_size=video_data.get('file_size', 0),
                description=video_data.get('description'),
                author=video_data.get('author')
            )
            logger.info(f"添加视频: {video.title}")
            return video
        except Exception as e:
            logger.error(f"添加视频失败: {e}")
            return None

    def get_video(self, url_hash: str) -> Optional[Video]:
        """获取视频记录"""
        return Video.get_or_none(Video.url_hash == url_hash)

    def search_videos(self, keyword: str, limit: int = 50) -> List[Video]:
        """搜索视频"""
        return list(
            Video.select()
            .where(Video.title.contains(keyword))
            .limit(limit)
        )

    def get_all_videos(self, limit: int = 100, offset: int = 0) -> List[Video]:
        """获取所有视频"""
        return list(
            Video.select()
            .order_by(Video.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

    def get_videos_by_source(self, source: str, limit: int = 50) -> List[Video]:
        """按来源获取视频"""
        return list(
            Video.select()
            .where(Video.source == source)
            .limit(limit)
        )

    def update_download_status(self, url_hash: str, is_downloaded: bool, download_path: str = None):
        """更新下载状态"""
        Video.update(
            is_downloaded=is_downloaded,
            download_path=download_path,
            updated_at=datetime.now()
        ).where(Video.url_hash == url_hash).execute()

    def add_download_task(self, url_hash: str) -> DownloadTask:
        """添加下载任务"""
        task, created = DownloadTask.get_or_create(
            video=url_hash,
            defaults={'status': 'pending'}
        )
        return task

    def update_task_status(self, task_id: int, status: str, progress: int = 0, error: str = None):
        """更新任务状态"""
        DownloadTask.update(
            status=status,
            progress=progress,
            error_message=error,
            updated_at=datetime.now()
        ).where(DownloadTask.id == task_id).execute()

    def get_pending_tasks(self) -> List[DownloadTask]:
        """获取待处理任务"""
        return list(
            DownloadTask.select()
            .where(DownloadTask.status == 'pending')
        )

    def get_video_count(self) -> int:
        """获取视频总数"""
        return Video.select().count()

    def delete_video(self, url_hash: str) -> bool:
        """删除视频记录"""
        deleted = Video.delete().where(Video.url_hash == url_hash).execute()
        return deleted > 0

    def export_json(self, filepath: str):
        """导出为JSON"""
        import json
        videos = list(Video.select().dicts())
        for v in videos:
            v['created_at'] = str(v['created_at'])
            v['updated_at'] = str(v['updated_at'])
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        logger.info(f"导出JSON: {filepath}")
