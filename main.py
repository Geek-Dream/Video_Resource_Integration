#!/usr/bin/env python3
"""
视频资源聚合器 - 主程序
"""

import sys
import json
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

from database.manager import DatabaseManager
from crawler import YouTubeCrawler, ArchiveCrawler, VimeoCrawler, WebCrawler
from downloader import VideoDownloader
from utils import logger

console = Console()


class VideoAggregator:
    """视频资源聚合器"""

    def __init__(self, proxy: str = None):
        self.db = DatabaseManager()
        self.proxy = proxy
        self.crawlers = {
            'youtube': YouTubeCrawler(),
            'archive': ArchiveCrawler(),
            'vimeo': VimeoCrawler(),
            'web': WebCrawler(proxy=proxy),
        }
        self.downloader = VideoDownloader(proxy=proxy)

    def search(self, keyword: str, sources: list = None, limit: int = 20) -> list:
        """搜索视频"""
        all_videos = []
        sources = sources or list(self.crawlers.keys())

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            for source in sources:
                if source not in self.crawlers:
                    continue

                task = progress.add_task(f"搜索 {source}...", total=None)
                
                try:
                    crawler = self.crawlers[source]
                    videos = crawler.search(keyword, limit)
                    
                    # 保存到数据库
                    for video in videos:
                        saved = self.db.add_video(video)
                        if saved:
                            all_videos.append(saved)
                    
                    progress.update(task, completed=True, description=f"[green]✓ {source}: {len(videos)} 个结果[/green]")
                except Exception as e:
                    progress.update(task, completed=True, description=f"[red]✗ {source}: {e}[/red]")

        return all_videos

    def search_all(self, keyword: str, limit: int = 20) -> list:
        """搜索所有来源"""
        return self.search(keyword, limit=limit)

    def list_videos(self, source: str = None, limit: int = 50) -> list:
        """列出视频"""
        if source:
            return self.db.get_videos_by_source(source, limit)
        return self.db.get_all_videos(limit)

    def download_video(self, url_hash: str) -> Optional[str]:
        """下载视频"""
        video = self.db.get_video(url_hash)
        if not video:
            console.print(f"[red]未找到视频: {url_hash}[/red]")
            return None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"下载 {video.title}...", total=100)

            def on_progress(percent, downloaded, total):
                progress.update(task, completed=percent)

            path = self.downloader.download(video.url, progress_callback=on_progress)
            
            if path:
                self.db.update_download_status(url_hash, True, path)
                progress.update(task, completed=100, description=f"[green]✓ 下载完成: {path}[/green]")
            else:
                progress.update(task, description=f"[red]✗ 下载失败[/red]")

        return path

    def export_json(self, filepath: str = "videos.json"):
        """导出JSON"""
        self.db.export_json(filepath)
        console.print(f"[green]已导出到: {filepath}[/green]")


# CLI 命令
@click.group()
@click.version_option(version='1.0.0')
def cli():
    """视频资源聚合器 - 搜索和下载公开视频资源"""
    pass


@cli.command()
@click.argument('keyword')
@click.option('-s', '--source', type=click.Choice(['youtube', 'archive', 'vimeo', 'web', 'all']), default='all', help='搜索来源')
@click.option('-l', '--limit', default=20, help='结果数量限制')
@click.option('-d', '--domestic', is_flag=True, help='仅搜索国内源（跳过YouTube/Vimeo/Archive）')
@click.option('-p', '--proxy', help='代理地址（如 http://127.0.0.1:1080）')
@click.option('--pipe', is_flag=True, help='管道输出格式（title|url|source）')
def search(keyword, source, limit, domestic, proxy, pipe):
    """搜索视频"""
    aggregator = VideoAggregator(proxy=proxy)
    
    if domestic:
        videos = aggregator.search(keyword, ['web'], limit)
    elif source == 'all':
        videos = aggregator.search_all(keyword, limit)
    else:
        videos = aggregator.search(keyword, [source], limit)

    if not videos:
        if not pipe:
            console.print("[yellow]未找到结果[/yellow]")
        return

    if pipe:
        import logging
        logging.disable(logging.CRITICAL)
        # 静默loguru - 移除默认handler
        import loguru
        loguru.logger.remove()
        # 静默Rich console
        import io
        console.file = io.StringIO()
        for video in videos:
            print(f"{video.title}|{video.url}|{video.source}")
        return


@cli.command('list')
@click.option('-s', '--source', help='按来源筛选')
@click.option('-l', '--limit', default=50, help='显示数量')
def list_videos(source, limit):
    """列出已保存的视频"""
    aggregator = VideoAggregator()
    videos = aggregator.list_videos(source, limit)

    if not videos:
        console.print("[yellow]数据库为空[/yellow]")
        return

    table = Table(title="已保存的视频")
    table.add_column("哈希", style="cyan", width=10)
    table.add_column("标题", style="white", max_width=40)
    table.add_column("来源", style="green", width=10)
    table.add_column("时长", style="yellow", width=10)
    table.add_column("已下载", style="magenta", width=8)

    for video in videos:
        downloaded = "✓" if video.is_downloaded else "✗"
        table.add_row(
            video.url_hash[:8],
            video.title[:40] + "..." if len(video.title) > 40 else video.title,
            video.source,
            video.duration_text,
            downloaded
        )

    console.print(table)


@cli.command()
@click.argument('hash_or_url')
@click.option('-p', '--proxy', help='代理地址（如 http://127.0.0.1:1080）')
@click.option('--name', help='输出文件名（不含扩展名）')
def download(hash_or_url, proxy, name):
    """下载视频 - 支持哈希ID或直接URL"""
    aggregator = VideoAggregator(proxy=proxy)
    
    # 如果是URL，直接下载
    if hash_or_url.startswith('http://') or hash_or_url.startswith('https://'):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("下载中...", total=100)
            def on_progress(percent, downloaded, total):
                progress.update(task, completed=percent)
            path = aggregator.downloader.download(hash_or_url, filename=name, progress_callback=on_progress)
            if path:
                progress.update(task, completed=100, description=f"[green]✓ 下载完成: {path}[/green]")
            else:
                progress.update(task, description=f"[red]✗ 下载失败[/red]")
        return
    
    # 否则当哈希ID查找
    videos = aggregator.db.get_all_videos(limit=1000)
    target = None
    for v in videos:
        if v.url_hash.startswith(hash_or_url) or str(v.id) == hash_or_url:
            target = v
            break
    
    if not target:
        console.print(f"[red]未找到视频: {hash_or_url}[/red]")
        return

    aggregator.download_video(target.url_hash)


@cli.command()
@click.argument('url')
def info(url):
    """获取视频信息"""
    aggregator = VideoAggregator()
    
    with console.status("正在获取视频信息..."):
        for crawler in aggregator.crawlers.values():
            try:
                video_info = crawler.get_video_info(url)
                if video_info:
                    console.print(Panel(
                        f"[bold]标题:[/bold] {video_info.get('title')}\n"
                        f"[bold]来源:[/bold] {video_info.get('source')}\n"
                        f"[bold]时长:[/bold] {video_info.get('duration_text')}\n"
                        f"[bold]作者:[/bold] {video_info.get('author', 'Unknown')}\n"
                        f"[bold]链接:[/bold] {video_info.get('url')}",
                        title="视频信息"
                    ))
                    return
            except Exception:
                continue
    
    console.print("[red]无法获取视频信息[/red]")


@cli.command()
@click.argument('filepath', default='videos.json')
def export(filepath):
    """导出为JSON"""
    aggregator = VideoAggregator()
    aggregator.export_json(filepath)


@cli.command()
def stats():
    """显示统计信息"""
    aggregator = VideoAggregator()
    total = aggregator.db.get_video_count()
    
    sources = {}
    for source in ['youtube', 'archive', 'vimeo', 'web']:
        count = len(aggregator.db.get_videos_by_source(source))
        if count > 0:
            sources[source] = count

    console.print(Panel(
        f"[bold]视频总数:[/bold] {total}\n" +
        "\n".join(f"[bold]{k}:[/bold] {v}" for k, v in sources.items()),
        title="统计信息"
    ))


@cli.command()
def clear():
    """清空数据库"""
    import os
    db_path = Path(__file__).parent / "data" / "videos.db"
    if db_path.exists():
        os.remove(db_path)
        console.print("[green]数据库已清空[/green]")
    else:
        console.print("[yellow]数据库不存在[/yellow]")


@cli.command()
@click.argument('url')
def crawl(url):
    """爬取网页视频"""
    aggregator = VideoAggregator()
    
    with console.status(f"正在爬取 {url}..."):
        crawler = aggregator.crawlers['web']
        videos = crawler.crawl_page(url)
        
        for video in videos:
            aggregator.db.add_video(video)

    console.print(f"[green]找到 {len(videos)} 个视频，已保存到数据库[/green]")


if __name__ == '__main__':
    cli()
