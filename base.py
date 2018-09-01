#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/31 13:43
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : base.py
# @Software : PyCharm

import requests
import urllib.robotparser
import urllib.parse
from bs4 import BeautifulSoup

class Downloader:
    def __init__(self, url,
                 userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/68.0.3440.106 Safari/537.36',
                 proxies=None,
                 caFile=None,):
        # 获取链接根地址
        self.url = url
        self.url_element = urllib.parse.urlparse(url)
        self.seed_url = '{0}://{1}'.format(self.url_element[0], self.url_element[1])
        # robots检查
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urllib.parse.urljoin(self.seed_url, 'robots.txt'))
        rp.read()
        if not rp.can_fetch(userAgent, url):
            print('Blocked by robots.txt: {}'.format(url))
            exit(110)
        self.headers = {'user-agent': userAgent}
        self.download(url, self.headers, proxies, caFile)

    def download(self, url, headers, proxies=None, caFile=None, timeout=3):
        self.r = requests.get(url, headers=headers, proxies=proxies, verify=caFile, timeout=timeout)
        self.html_doc = self.r.text

class Myparser:
    def __init__(self, html, filter=None):
        self.html = html
        self.renew_soup(filter)

    def renew_soup(self, filter):
        self.filter = filter
        self.soup = BeautifulSoup(self.html.html_doc, parse_only=self.filter, features="lxml")
