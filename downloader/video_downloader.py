"""视频下载器"""

import os
from pathlib import Path
from typing import Optional, Callable
import yt_dlp
from utils import logger
from utils.helpers import sanitize_filename


class VideoDownloader:
    """视频下载器"""

    def __init__(self, output_dir: str = None, proxy: str = None):
        self.output_dir = Path(output_dir or Path(__file__).parent.parent / "downloads")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        logger.info(f"下载目录: {self.output_dir}")

    def download(self, url: str, filename: str = None, 
                 progress_callback: Callable = None) -> Optional[str]:
        """下载视频 - 使用yt-dlp智能解析"""
        try:
            # 如果是详情页URL，先解析出真实视频URL
            if '/voddetail/' in url:
                logger.info(f"检测到详情页URL，正在解析真实视频地址...")
                real_url = self._resolve_detail_url(url)
                if real_url:
                    url = real_url
                    logger.info(f"解析成功，真实URL: {url}")
                else:
                    logger.error(f"无法从详情页解析出视频URL")
                    return None

            output_path = self._get_output_path(url, filename)
            
            ydl_opts = {
                'outtmpl': str(output_path),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._create_progress_hook(progress_callback)],
                'merge_output_format': 'mp4',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'ignoreerrors': True,
                'no_check_certificates': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://www.shyanhuai.com/',
                },
            }

            # 设置代理
            if self.proxy:
                ydl_opts['proxy'] = self.proxy
            
            # 对m3u8链接使用ffmpeg下载（更可靠）
            if '.m3u8' in url:
                return self._download_m3u8(url, filename, progress_callback)

            logger.info(f"开始下载: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先尝试获取视频信息
                try:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        logger.info(f"视频标题: {info.get('title', 'Unknown')}")
                        logger.info(f"视频格式: {info.get('ext', 'Unknown')}")
                except Exception as e:
                    logger.debug(f"获取信息失败: {e}")
                
                # 下载视频
                ydl.download([url])

            # 查找下载的文件
            downloaded_file = self._find_downloaded_file(output_path)
            if downloaded_file:
                logger.info(f"下载完成: {downloaded_file}")
                return str(downloaded_file)
            
            logger.error(f"下载失败: 未找到文件")
            return None

        except Exception as e:
            logger.error(f"下载失败 {url}: {e}")
            return None

    def download_with_info(self, video_info: dict, 
                           progress_callback: Callable = None) -> Optional[str]:
        """使用视频信息下载"""
        url = video_info.get('url')
        title = video_info.get('title', 'video')
        filename = sanitize_filename(title)
        return self.download(url, filename, progress_callback)

    def _get_output_path(self, url: str, filename: str = None) -> Path:
        """获取输出路径"""
        if filename:
            return self.output_dir / f"{filename}.%(ext)s"
        
        # 从URL生成文件名
        from urllib.parse import urlparse, unquote
        parsed = urlparse(url)
        path = unquote(parsed.path)
        basename = os.path.basename(path)
        
        if basename and '.' in basename:
            name = basename.rsplit('.', 1)[0]
            return self.output_dir / f"{name}.%(ext)s"
        
        # 使用URL哈希作为文件名
        from utils.helpers import generate_hash
        hash_name = generate_hash(url)
        return self.output_dir / f"{hash_name}.%(ext)s"

    def _find_downloaded_file(self, output_path: Path) -> Optional[Path]:
        """查找下载的文件"""
        parent = output_path.parent
        
        # 排除的文件
        skip_files = {'.DS_Store', 'Thumbs.db', '.localized'}
        
        # 查找最近修改的视频文件
        video_extensions = {'.mp4', '.webm', '.mkv', '.flv', '.avi', '.mov', '.m4v'}
        
        video_files = []
        for f in parent.iterdir():
            if f.is_file() and f.name not in skip_files:
                if f.suffix.lower() in video_extensions:
                    video_files.append(f)
        
        if video_files:
            return max(video_files, key=lambda p: p.stat().st_mtime)
        
        # 如果没找到视频文件，查找任何非隐藏文件
        non_hidden = [f for f in parent.iterdir() 
                     if f.is_file() and not f.name.startswith('.') and f.name not in skip_files]
        if non_hidden:
            return max(non_hidden, key=lambda p: p.stat().st_mtime)
        
        return None

    def _create_progress_hook(self, callback: Callable = None):
        """创建进度回调"""
        def hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0 and callback:
                    progress = int(downloaded / total * 100)
                    callback(progress, downloaded, total)
                # 打印下载进度
                if total > 0:
                    percent = int(downloaded / total * 100)
                    speed = d.get('speed', 0) or 0
                    logger.info(f"下载进度: {percent}% | 速度: {speed/1024:.1f} KB/s")
            elif d['status'] == 'finished':
                if callback:
                    callback(100, 0, 0)
                logger.info("下载完成，正在处理...")
        return hook

    def _download_m3u8(self, m3u8_url: str, filename: str = None, 
                       progress_callback: Callable = None) -> Optional[str]:
        """使用ffmpeg下载m3u8视频（自动选择最高画质）"""
        import subprocess
        import json
        
        # 1. 检查是否是master playlist（包含多画质）
        actual_url = self._select_best_quality(m3u8_url)
        
        if filename:
            safe_name = sanitize_filename(filename)
            output_path = self.output_dir / f"{safe_name}.mp4"
        else:
            from utils.helpers import generate_hash
            hash_name = generate_hash(m3u8_url)
            output_path = self.output_dir / f"{hash_name}.mp4"
        
        # 2. 获取视频总时长
        total_seconds = self._get_m3u8_duration(actual_url)
        
        # 3. 写入进度文件供shell脚本读取
        progress_file = self.output_dir.parent / "data" / "dl_progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_info = {
            "total_seconds": total_seconds,
            "total_display": self._format_duration(total_seconds),
            "output_path": str(output_path),
            "status": "downloading"
        }
        with open(progress_file, 'w') as f:
            json.dump(progress_info, f)
        
        logger.info(f"下载m3u8: {actual_url} (时长: {self._format_duration(total_seconds)})")
        
        cmd = [
            'ffmpeg', '-y',
            '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-referer', 'https://www.shyanhuai.com/',
            '-i', actual_url,
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            '-movflags', '+faststart',
            str(output_path)
        ]
        
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            _, stderr = proc.communicate()
            
            progress_info["status"] = "done"
            with open(progress_file, 'w') as f:
                json.dump(progress_info, f)
            
            if proc.returncode == 0 and output_path.exists():
                size_mb = output_path.stat().st_size / (1024*1024)
                res_info = self._get_video_resolution(str(output_path))
                logger.info(f"下载完成: {output_path} ({size_mb:.1f}MB) {res_info}")
                if progress_callback:
                    progress_callback(100, 0, 0)
                return str(output_path)
            else:
                logger.error(f"ffmpeg下载失败: {stderr.decode()[-200:]}")
                return None
        except Exception as e:
            logger.error(f"ffmpeg执行失败: {e}")
            return None

    def _get_m3u8_duration(self, m3u8_url: str) -> int:
        """获取m3u8视频总时长（秒）"""
        import requests
        import re as re_mod
        
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.shyanhuai.com/'}
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        try:
            resp = requests.get(m3u8_url, headers=headers, timeout=15, proxies=proxies)
            total = sum(float(m.group(1)) for m in re_mod.finditer(r'#EXTINF:([\d.]+)', resp.text))
            if total > 0:
                return int(total)
            # master playlist → 递归
            if '#EXT-X-STREAM-INF' in resp.text:
                for i, line in enumerate(resp.text.strip().split('\n')):
                    if '#EXT-X-STREAM-INF' in line:
                        lines = resp.text.strip().split('\n')
                        if i + 1 < len(lines):
                            sub = lines[i + 1].strip()
                            if not sub.startswith('http'):
                                from urllib.parse import urlparse
                                p = urlparse(m3u8_url)
                                sub = f"{p.scheme}://{p.netloc}{'/'.join(p.path.rsplit('/',1)[:1])}/{sub}"
                            return self._get_m3u8_duration(sub)
            return 0
        except:
            return 0

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if seconds <= 0: return "未知"
        h, m, s = seconds//3600, (seconds%3600)//60, seconds%60
        return f"{h}h{m:02d}m" if h > 0 else f"{m}m{s:02d}s"

    def _select_best_quality(self, m3u8_url: str) -> str:
        """解析master playlist，选择最高画质"""
        import requests
        import re as re_mod
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.shyanhuai.com/',
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        try:
            resp = requests.get(m3u8_url, headers=headers, timeout=15, proxies=proxies)
            content = resp.text
            
            # 如果不是master playlist（没有STREAM-INF），直接返回
            if '#EXT-X-STREAM-INF' not in content:
                logger.info("单画质m3u8，直接下载")
                return m3u8_url
            
            # 解析所有画质选项
            qualities = []
            lines = content.strip().split('\n')
            for i, line in enumerate(lines):
                if '#EXT-X-STREAM-INF' in line:
                    # 提取BANDWIDTH和RESOLUTION
                    bw_match = re_mod.search(r'BANDWIDTH=(\d+)', line)
                    res_match = re_mod.search(r'RESOLUTION=(\d+x\d+)', line)
                    bandwidth = int(bw_match.group(1)) if bw_match else 0
                    resolution = res_match.group(1) if res_match else 'unknown'
                    
                    # 下一行是URL
                    if i + 1 < len(lines):
                        stream_url = lines[i + 1].strip()
                        qualities.append({
                            'bandwidth': bandwidth,
                            'resolution': resolution,
                            'url': stream_url,
                        })
            
            if not qualities:
                return m3u8_url
            
            # 按带宽排序，选最高画质
            qualities.sort(key=lambda x: x['bandwidth'], reverse=True)
            
            logger.info(f"可用画质:")
            for q in qualities:
                logger.info(f"  {q['resolution']} ({q['bandwidth']//1000}kbps)")
            
            best = qualities[0]
            logger.info(f"选择最高画质: {best['resolution']} ({best['bandwidth']//1000}kbps)")
            
            # 构建完整URL
            if best['url'].startswith('http'):
                return best['url']
            else:
                # 相对路径，拼接base URL
                from urllib.parse import urlparse
                parsed = urlparse(m3u8_url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                path_base = '/'.join(parsed.path.rsplit('/', 1)[0:1])
                return f"{base}{path_base}/{best['url']}"
                
        except Exception as e:
            logger.warning(f"解析画质失败，使用原始URL: {e}")
            return m3u8_url

    def _get_video_resolution(self, filepath: str) -> str:
        """获取视频实际分辨率"""
        import subprocess
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                 '-show_entries', 'stream=width,height', '-of', 'csv=p=0', filepath],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return ""

    def _resolve_detail_url(self, detail_url: str) -> Optional[str]:
        """从详情页解析真实视频URL (m3u8/mp4)"""
        import re
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': detail_url,
        }
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        try:
            # 1. 访问详情页，找播放链接
            resp = requests.get(detail_url, headers=headers, timeout=20, proxies=proxies)
            
            play_link = None
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if '/vodplay/' in href:
                    play_link = href
                    break
            
            if not play_link:
                logger.error("详情页未找到播放链接")
                return None
            
            # 构建完整播放页URL
            from urllib.parse import urlparse
            parsed = urlparse(detail_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            play_url = base + play_link if not play_link.startswith('http') else play_link
            
            # 2. 访问播放页
            logger.info(f"播放页: {play_url}")
            play_resp = requests.get(play_url, headers=headers, timeout=20, proxies=proxies)
            text = play_resp.text
            
            # 3. 从 player_aaaa 配置中提取真实URL
            # 先找 player_aaaa 块，再从中提取 url
            player_idx = text.find('player_aaaa')
            if player_idx >= 0:
                chunk = text[player_idx:player_idx+500]
                url_match = re.search(r'url":"(.*?)"', chunk)
                if url_match:
                    raw_url = url_match.group(1).replace('\\/', '/')
                    if raw_url.startswith('http'):
                        logger.info(f"找到真实URL: {raw_url}")
                        return raw_url
            
            # 备用: 直接搜索 m3u8 链接
            m3u8_match = re.search(r'https?://[^"\'<>\s]*\.m3u8[^"\'<>\s]*', text)
            if m3u8_match:
                url = m3u8_match.group(0).replace('\\/', '/')
                logger.info(f"备用方案找到m3u8: {url}")
                return url
            
            logger.error("播放页未找到m3u8/mp4链接")
            return None
            
        except Exception as e:
            logger.error(f"解析详情页失败: {e}")
            return None

    def get_download_info(self, url: str) -> dict:
        """获取下载信息（不下载）"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            if self.proxy:
                ydl_opts['proxy'] = self.proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'filesize': info.get('filesize'),
                    'format': info.get('format'),
                    'ext': info.get('ext'),
                    'url': info.get('url'),
                    'webpage_url': info.get('webpage_url'),
                }
        except Exception as e:
            logger.error(f"获取下载信息失败 {url}: {e}")
            return {}
