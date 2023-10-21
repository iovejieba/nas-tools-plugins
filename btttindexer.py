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

class Bttt(_IPluginModule):
    # 插件名称
    module_name = "Bttt"
    # 插件描述
    module_desc = "BT天堂搜索器"
    # 插件图标
    module_icon = "chinesesubfinder.png"
    # 主题色
    module_color = "#83BE39"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "me"
    # 作者主页
    author_url = "https://github.com/jxxghp"
    # 插件配置项ID前缀
    module_config_prefix = "btttindexer_"
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
            "id": "Bttt",
            "name": "Bttt",
            "domain": "https://www.bt-tt.com/",
            "encoding": "UTF-8",
            "parser": "Bttt",
            "public": True,
            "proxy": True,
            "language": "zh"
        }
    _req = None
    _base_url = "https://www.bt-tt.com/"
    _search_url = "https://www.bt-tt.com/e/search/"
    _indexer_id = "Bttt"

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
        log.info(str(kwargs))
        log.warn(f"【Indexer】信息：{self._indexer_id} https://www.bt-tt.com/e/search")
        post_data = {
            "show": "title,newstext",
            "keyboard": kwargs["keyword"],
            "searchtype": "影视搜索"
        }
        res = self._req.post(url=self._search_url, data=post_data)
        if not res or res.status_code != 200:
            return torrents
        # print(res.content.decode("UTF-8"))
        html_doc = PyQuery(res.content)
        sub_urls = html_doc("div.m-film > ul > li")
        for sub_t in sub_urls:
            sub_item = PyQuery(sub_t)
            sub_url = self._attr(sub_item("strong > div.txt > h3 > a"), "href")
            detail_sub = self._base_url + sub_url
            detail_ret = self._req.get_res(url=detail_sub)
            if not detail_ret or detail_ret.status_code != 200:
                continue
            # print(detail_ret.content.decode("UTF-8"))
            detail_doc = PyQuery(detail_ret.content)
            t_list = detail_doc("div.bot > tr > td > a")
            for t_t in t_list:
                t_item = PyQuery(t_t)
                title = self._text(t_item)
                enclosure = self._attr(t_item, "href")
                size = ""
                seeders = ""
                peers = ""
                page_url = detail_sub
                torrent = {'indexer': self._indexer_id,
                            'title': title,
                            'enclosure': enclosure,
                            'size': size,
                            'seeders': seeders,
                            'peers': peers,
                            'freeleech': True,
                            'downloadvolumefactor': 0.0,
                            'uploadvolumefactor': 1.0,
                            'page_url': page_url,
                            'imdbid': ""}
                torrents.append(torrent)
        return torrents

