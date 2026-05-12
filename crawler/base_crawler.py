"""爬虫基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from utils import logger


class BaseCrawler(ABC):
    """爬虫基类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.name = self.__class__.__name__

    @abstractmethod
    def search(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索视频"""
        pass

    @abstractmethod
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取视频详细信息"""
        pass

    def _make_request(self, url: str, params: dict = None, timeout: int = 15,
                      method: str = 'get', data: dict = None) -> requests.Response:
        """发送请求"""
        try:
            if method == 'post':
                resp = self.session.post(url, data=data, timeout=timeout)
            else:
                resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.error(f"[{self.name}] 请求失败 {url}: {e}")
            raise
