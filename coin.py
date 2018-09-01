#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/31 13:44
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : coin.py.py
# @Software : PyCharm

from base import Downloader
from base import Myparser
from bs4 import SoupStrainer
import urllib.parse

class CoinPager(Downloader):
    def __init__(self,
                 url,
                 type,
                 userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/68.0.3440.106 Safari/537.36',
                 proxies=None,
                 caFile=None):
        Downloader.__init__(self, url, userAgent, proxies, caFile)
        self.page_type = type

    def set_type(self, type):
        self.page_type = type


class CoinParser(Myparser):
    def __init__(self, html, filter=None):
        Myparser.__init__(self, html, filter)
        self.page_type = html.page_type
        self.page_coin_urls = {}
        self.coin_hl_price = {}
        self.coin_sites = []

    def get_coin_url(self):
        if self.page_type == 'coin_list':
            self.filter = SoupStrainer("table", id="table")
            self.renew_soup(self.filter)
            # 获取每个coin详情页URL
            for tag in self.soup.select('tbody tr'):
                self.page_coin_urls[tag['id']] = tag.a['href']
            print(self.page_coin_urls)
            print(len(self.page_coin_urls))

    def get_coin_info(self):
        if self.page_type == 'coin_info':
            self.filter = SoupStrainer("div", id="baseInfo")
            self.renew_soup(self.filter)
            # 获取24小时最高价、最低价
            for tag in self.soup.select("div.lowHeight div"):
                self.coin_hl_price[tag.contents[0]] = tag.span.string
            # 获取coin 描述页URL
            self.coin_des_url = self.soup.select("div.des a")[0]["href"]
            print(self.coin_hl_price)
            print(self.coin_des_url)
            for tag in self.soup.select("div.secondPark li"):
                if "白皮书" in tag.select("span.tit")[0].text:
                    self.coin_whitepaper_url = tag.select("span.value")[0].text
                if "网站" in tag.select("span.tit")[0].text:
                    for tag_a in tag.select("span.value")[0].find_all('a'):
                        self.coin_sites.append(tag_a['href'])

            print(self.coin_whitepaper_url)
            print(self.coin_sites)


    def get_coin_des(self):
        if self.page_type == 'coin_des':
            self.filter = SoupStrainer("div", class_="artBox")
            self.renew_soup(self.filter)
            self.coin_des = self.soup.text
            print(self.coin_des)

    def get_coin_timeline(self):
        if self.page_type == 'coin_':
            pass

    def get_coin_tickerlist(self):
        pass