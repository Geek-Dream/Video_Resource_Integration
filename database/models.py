"""数据库模型定义"""

from datetime import datetime
from pathlib import Path
from peewee import (
    SqliteDatabase, Model, CharField, TextField,
    IntegerField, DateTimeField, BooleanField, AutoField
)

# 数据库路径
db_path = Path(__file__).parent.parent / "data" / "videos.db"
db_path.parent.mkdir(exist_ok=True)

db = SqliteDatabase(str(db_path), pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64,
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0
})


class BaseModel(Model):
    """基础模型类"""
    class Meta:
        database = db


class Video(BaseModel):
    """视频资源表"""
    id = AutoField()
    url_hash = CharField(max_length=32, unique=True, index=True)
    title = CharField(max_length=500)
    url = TextField()
    cover_url = TextField(null=True)
    duration = IntegerField(default=0)
    duration_text = CharField(max_length=20, default="00:00:00")
    source = CharField(max_length=50)  # youtube, archive, vimeo, direct
    video_type = CharField(max_length=20)  # mp4, m3u8, webm
    file_size = IntegerField(default=0)
    description = TextField(null=True)
    author = CharField(max_length=200, null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    is_downloaded = BooleanField(default=False)
    download_path = CharField(max_length=500, null=True)

    class Meta:
        table_name = 'videos'


class DownloadTask(BaseModel):
    """下载任务表"""
    id = AutoField()
    video = CharField(max_length=32)  # url_hash
    status = CharField(max_length=20, default='pending')  # pending, downloading, completed, failed
    progress = IntegerField(default=0)
    file_path = CharField(max_length=500, null=True)
    error_message = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'download_tasks'


def init_db():
    """初始化数据库"""
    db.connect(reuse_if_open=True)
    db.create_tables([Video, DownloadTask], safe=True)
