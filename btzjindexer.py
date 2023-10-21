import os.path
from functools import lru_cache

from app.plugins import EventHandler
from app.plugins.modules._base import _IPluginModule
from app.indexer.indexerConf import IndexerConf
from app.utils import RequestUtils
from app.utils.types import MediaType, EventType
from config import Config
import log
from pyquery import PyQuery
from string import Template
import re

class Btzj(_IPluginModule):
    # 插件名称
    module_name = "Btzj"
    # 插件描述
    module_desc = "BT之家搜索器"
    # 插件图标
    module_icon = "chinesesubfinder.png"
    # 主题色
    module_color = "#83BE39"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "me"
    # 作者主页
    author_url = "https://github.com/PterX/nas-tools-plugins"
    # 插件配置项ID前缀
    module_config_prefix = "btzjindexer_"
    # 加载顺序
    module_order = 3
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _save_tmp_path = None
    _host = None
    _api_key = None
    _remote_path = None
    _local_path = None
    _remote_path2 = None
    _local_path2 = None
    _remote_path3 = None
    _local_path3 = None
    _indexer = {
            "id": "Btzj",
            "name": "Btzj",
            "domain": "https://bt529.com/",
            "encoding": "UTF-8",
            "parser": "Btzj",
            "public": True,
            "proxy": True,
            "language": "zh"
        }
    _req = None
    _base_url = "https://bt529.com/"
    _indexer_id = "Btzj"

    def init_config(self, config: dict = None):
        self._save_tmp_path = Config().get_temp_path()
        if not os.path.exists(self._save_tmp_path):
            os.makedirs(self._save_tmp_path)
        import requests
        session = requests.session()
        self._req = RequestUtils(proxies=Config().get_proxies(), session=session, timeout=10)

    def get_state(self):
        return True

    @staticmethod
    def get_fields():
        return []

    def stop_service(self):
        pass

    def get_indexers(self):
        return [IndexerConf(datas=self._indexer,
                           siteid=self._indexer_id)]

    def _text(self, item):
        if not item:
            return ""
        return item.text()
    
    def _attr(self, item, attr):
        if not item:
            return ""
        return item.attr(attr)

    def search(self, *args, **kwargs):
        torrents = []
        keyword = kwargs["keyword"]
        search_url = f"https://bt529.com/search-index-keyword-{keyword}.htm"
        log.warn(f"【Indexer】信息：{self._indexer_id} {search_url}")
        res = self._req.get_res(url=search_url)
        if not res or res.status_code != 200:
            return torrents
        # print(res.content.decode("UTF-8"))
        html_doc = PyQuery(res.content)
        sub_urls = html_doc("a.subject_link")
        for sub_t in sub_urls:
            sub_item = PyQuery(sub_t)
            title = self._text(sub_item)
            # log.info(title)
            detail_sub = self._attr(sub_item, "href")
            if not detail_sub.startswith("http://") and not detail_sub.startswith("https://"):
                detail_sub = self._base_url + detail_sub
            # log.info(detail_sub)
            detail_ret = self._req.get_res(url=detail_sub)
            if not detail_ret or detail_ret.status_code != 200:
                continue
            detail_doc = PyQuery(detail_ret.content)
            attach_sub = self._attr(detail_doc("div.attachlist > table > tr > td > a"), "href")
            if not attach_sub:
                continue
            if not attach_sub.startswith("http://") and not attach_sub.startswith("https://"):
                attach_sub = self._base_url + attach_sub
            # log.info(attach_sub)
            attach_ret = self._req.get_res(url=attach_sub)
            if not attach_ret or attach_ret.status_code != 200:
                continue
            attach_doc = PyQuery(attach_ret.content)
            enclosure = self._attr(attach_doc("dl > dd > a"), "href")
            if not enclosure:
                continue
            if not enclosure.startswith("http://") and not enclosure.startswith("https://"):
                enclosure = self._base_url + enclosure
            log.info(enclosure)
            torrent = {
                'indexer': self._indexer_id,
                'title': title,
                'enclosure': enclosure,
                'size': "",
                'seeders': "",
                'peers': "",
                'freeleech': True,
                'downloadvolumefactor': 0.0,
                'uploadvolumefactor': 1.0,
                'page_url': detail_sub,
                'imdbid': ""
            }
            torrents.append(torrent)
        return torrents

