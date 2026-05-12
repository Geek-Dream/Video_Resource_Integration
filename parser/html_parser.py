"""HTML页面解析器"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests
from utils import logger


class HTMLParser:
    """HTML页面解析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def extract_video_links(self, url: str) -> List[Dict[str, str]]:
        """从页面提取所有视频相关链接"""
        links = []
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 提取所有链接
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                if self._is_video_link(href):
                    links.append({'url': href, 'text': text})

            # 提取iframe
            for iframe in soup.find_all('iframe', src=True):
                links.append({'url': iframe['src'], 'text': 'iframe'})

        except Exception as e:
            logger.error(f"提取链接失败 {url}: {e}")

        return links

    def extract_meta_info(self, url: str) -> Dict[str, Any]:
        """提取页面元信息"""
        meta = {}
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 标题
            title_tag = soup.find('title')
            if title_tag:
                meta['title'] = title_tag.get_text(strip=True)

            # OG标签
            for og in soup.find_all('meta', property=re.compile(r'^og:')):
                prop = og.get('property', '').replace('og:', '')
                meta[f'og_{prop}'] = og.get('content', '')

            # 描述
            desc = soup.find('meta', attrs={'name': 'description'})
            if desc:
                meta['description'] = desc.get('content', '')

        except Exception as e:
            logger.error(f"提取元信息失败 {url}: {e}")

        return meta

    def _is_video_link(self, url: str) -> bool:
        """判断是否为视频链接"""
        video_patterns = [
            r'\.mp4', r'\.m3u8', r'\.webm', r'\.mkv',
            r'youtube\.com/watch', r'youtu\.be/',
            r'vimeo\.com/', r'archive\.org/'
        ]
        return any(re.search(p, url, re.I) for p in video_patterns)
