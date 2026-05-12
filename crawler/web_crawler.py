"""国内视频网站爬虫"""

from pathlib import Path
from typing import List, Dict, Any
from .base_crawler import BaseCrawler
from parser.video_parser import VideoParser
from utils import logger


class WebCrawler(BaseCrawler):
    """国内视频网站爬虫"""

    SITES_FILE = Path(__file__).parent.parent / "data" / "sites.json"

    def __init__(self, proxy: str = None):
        super().__init__()
        self.name = "Web"
        self.parser = VideoParser()
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        self._load_sites()

    def _load_sites(self):
        """从sites.json加载网站配置"""
        import json
        if self.SITES_FILE.exists():
            try:
                self.VIDEO_SITES = json.load(open(self.SITES_FILE, encoding='utf-8'))
            except:
                self.VIDEO_SITES = self._default_sites()
        else:
            self.VIDEO_SITES = self._default_sites()
        # 确保默认写入
        if not self.VIDEO_SITES:
            self.VIDEO_SITES = self._default_sites()
            self._save_sites()

    def _save_sites(self):
        """保存网站配置"""
        import json
        self.SITES_FILE.parent.mkdir(parents=True, exist_ok=True)
        json.dump(self.VIDEO_SITES, open(self.SITES_FILE, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)

    @staticmethod
    def _default_sites():
        return [
            {"name": "碟调网", "base": "https://www.shyanhuai.com",
             "search": "https://www.shyanhuai.com/vodsearch/-------------.html?wd={keyword}", "method": "get"},
        ]

    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """在指定网站搜索视频"""
        videos = []
        
        for site in self.VIDEO_SITES:
            try:
                site_videos = self._search_site(site, keyword, limit)
                videos.extend(site_videos)
                logger.info(f"[{site['name']}] 找到 {len(site_videos)} 个结果")
            except Exception as e:
                logger.debug(f"[{site['name']}] 搜索失败: {e}")

        # 去重（同名同源只保留一个）
        seen = set()
        unique_videos = []
        for v in videos:
            key = (v['title'], v['source'])
            if key not in seen:
                seen.add(key)
                unique_videos.append(v)
        
        # 过滤：只保留标题包含关键词任一字符的结果
        def is_related(video):
            title = video.get('title', '')
            # 完全包含关键词
            if keyword in title or keyword.replace(' ', '') in title.replace(' ', ''):
                return True
            # 关键词的每个字都在标题中出现（允许顺序不同）
            if all(c in title for c in keyword if c.strip()):
                return True
            return False
        
        filtered = [v for v in unique_videos if is_related(v)]
        
        # 如果过滤后没有结果，返回原始结果（避免空结果）
        if not filtered:
            filtered = unique_videos
        
        # 按关键词相关性排序
        def relevance(video):
            title = video.get('title', '')
            if keyword == title:
                return 0
            elif keyword in title:
                return 1
            else:
                return 2
        
        filtered.sort(key=relevance)
        
        logger.info(f"[Web] 搜索 '{keyword}' 共找到 {len(filtered)} 个视频")
        return filtered[:limit]

    def _search_site(self, site: dict, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """在单个网站搜索"""
        videos = []
        
        try:
            method = site.get('method', site.get('search_method', 'get'))
            search_url = site['search']
            
            if method == 'post':
                resp = self._make_request(search_url, method='post', 
                                          data={'wd': keyword}, timeout=15)
            else:
                search_url = search_url.format(keyword=keyword)
                resp = self._make_request(search_url, timeout=15)

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找视频详情链接
            detail_links = soup.find_all('a', href=lambda x: x and '/voddetail/' in x)
            
            seen_urls = set()
            for link in detail_links:
                if len(videos) >= limit:
                    break
                    
                href = link.get('href', '')
                # 优先用 title 属性
                title_attr = link.get('title', '')
                text = title_attr or link.get_text(strip=True)
                
                # 如果没有title属性，跳过格式描述类文本
                if not title_attr:
                    import re
                    if re.match(r'^(HD|TC|BD|SD|正片)(中字|国语|粤语|英语)?$', text):
                        continue
                    if not text or len(text) < 2:
                        continue
                
                skip_words = ['播放', '更多', '首页', '已完结', '更新至']
                if any(text.startswith(w) for w in skip_words):
                    continue
                if text and (text[0].isdigit() or '已完结' in text or '更新至' in text):
                    continue
                
                full_url = site['base'] + href if not href.startswith('http') else href
                
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                videos.append({
                    'title': text,
                    'url': full_url,
                    'cover_url': None,
                    'duration': 0,
                    'duration_text': '00:00:00',
                    'source': site['name'],
                    'video_type': 'unknown',
                    'file_size': 0,
                    'description': None,
                    'author': None
                })

        except Exception as e:
            logger.debug(f"访问 {site['name']} 失败: {e}")

        return videos

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            return self.parser.parse_direct_url(url)
        except Exception as e:
            logger.error(f"[Web] 获取视频信息失败 {url}: {e}")
            return {}

    def resolve_real_url(self, detail_url: str) -> str:
        """从详情页提取真实视频播放URL（m3u8/mp4）
        
        流程: detail页 → 播放页 → JS中的m3u8/mp4 URL
        """
        import re
        
        try:
            # 1. 访问详情页，找播放链接
            logger.info(f"[解析] 访问详情页: {detail_url}")
            resp = self._make_request(detail_url, timeout=20)
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 查找播放页链接 (/vodplay/xxx-1-1.html)
            play_link = None
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if '/vodplay/' in href:
                    play_link = href
                    break
            
            if not play_link:
                logger.warning(f"[解析] 未找到播放链接")
                return None
            
            # 构建完整播放页URL
            from urllib.parse import urlparse
            parsed = urlparse(detail_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            play_url = base + play_link if not play_link.startswith('http') else play_link
            
            # 2. 访问播放页，提取m3u8/mp4 URL
            logger.info(f"[解析] 访问播放页: {play_url}")
            play_resp = self._make_request(play_url, timeout=20)
            
            # 从JS中提取: var player_aaaa={"url":"https://xxx.m3u8",...}
            patterns = [
                r'"url"\s*:\s*"(https?://[^"]*\.m3u8[^"]*)"',
                r'"url"\s*:\s*"(https?://[^"]*\.mp4[^"]*)"',
                r'"url"\s*:\s*"(https?://[^"]*video[^"]*)"',
                r'(https?://[^"\']*\.m3u8[^"\']*)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, play_resp.text)
                if match:
                    real_url = match.group(1).replace('\\/', '/')
                    logger.info(f"[解析] 找到真实URL: {real_url}")
                    return real_url
            
            logger.warning(f"[解析] 未找到m3u8/mp4链接")
            return None
            
        except Exception as e:
            logger.error(f"[解析] 解析失败: {e}")
            return None

    def crawl_page(self, url: str) -> List[Dict[str, Any]]:
        """爬取单个页面的视频"""
        return self.parser.parse_html_page(url)
