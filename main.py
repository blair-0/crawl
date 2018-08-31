#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/23 12:52
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : main.py
# @Software : PyCharm

import urllib.robotparser, urllib.request, urllib.request, urllib.parse
import ssl
import re
import itertools
import datetime
import time
import sys

# 需要安装第三方库beautifulsoup4 和lxml（作为解析器，速度比html.parser快）
# 需要安装chardet，加速字符编码检测
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urllib.parse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()


'''
class MyHTMLParser(urllib.parse.HTMLParser):
    def __init__(self, seed_url):
        HTMLParser.__init__(self)
        # 存放每页每个币种和对应的URL
        self.seed_url = seed_url
        self.coin_url = {}
        # 是否进入了"id=table"的表格，里面包含币种列表
        self.coin_table_tag = False
        # 是否是表格中每行的第一个<a></a>标签，里面包含币种对应的url
        self.first_a = False

    def handle_starttag(self, tag, attrs):
        if ('id', 'table') in attrs:
            print('get table')
            self.coin_table_tag = True
        if self.coin_table_tag and tag == 'tr':
            for attr in attrs:
                if attr[0] == 'id':
                    self.coin_id = attr[1]
                    self.first_a = True
        if self.first_a and tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    print('add {}'.format(self.coin_id))
                    self.coin_url[self.coin_id] = urllib.parse.urljoin(self.seed_url, attr[1])

    def handle_endtag(self, tag):
        if self.coin_table_tag and tag == 'table':
            self.coin_table_tag = False
        if self.first_a and tag == 'a':
            self.first_a = False
'''
class MyHTMLParser():
    def __init__(self, html_doc):
        self.html_doc = html_doc
        self.page_coin_urls = {}
        self.table_id = SoupStrainer("table", id="table")
        self.div_baseInfo = SoupStrainer("div" id="baseInfo")
        self.div_tickerlist = SoupStrainer("div" id="tickerlist")
        self.div_timeLineBox = SoupStrainer("div" id="timeLineBox")

    def get_coin_url(self):
        self.soup = BeautifulSoup(self.html_doc, "lxml", parse_only=self.table_id)
        for tag in self.soup.select('tr'):
            self.page_coin_urls[tag['id']] = tag.a['href']

    def get_coin_info(self):
        self.soup = BeautifulSoup(self.html_doc, "lxml", parse_only=self.div_baseInfo)
        for tag in soup.select("div.lowHeight div"):
            self.coin_info[tag.contents[0]] = tag.span.string
        self.coin_info['des_url'] = soup.select("div.des a")[0]["href"]


    def get_coin_price(self):
        pass


def download(url,
             user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/68.0.3440.106 Safari/537.36',
             num_retries=2,
             proxy=None,
             ca_file=None):
    # 后面有设置全局的ProxyHandler，这里重置为初始的，否则robotparser会报代理证书问题
    urllib.request.install_opener(urllib.request.build_opener(urllib.request.BaseHandler()))
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(url, 'robots.txt'))
    rp.read()
    # robots.txt检查，只显示警告信息，不做实际处理
    if not rp.can_fetch(user_agent, url):
        print('Blocked by robots.txt: {}'.format(url))
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    if proxy:
        print('use proxy')
        proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy_params))
        urllib.request.install_opener(opener)
    if ca_file:
        print('use ca')
        ssl_ctx = ssl.SSLContext()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        ssl_ctx.load_verify_locations(ca_file)
    else:
        ssl_ctx = None
    print('Downloading:', url)
    try:
        # python3 中返回的是bytes类型，为了后面方便处理，在此处decode
        html = urllib.request.urlopen(request, context=ssl_ctx).read().decode()
    except urllib.error.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # 返回 5xx 错误则重试
                return download(url, user_agent, num_retries-1)
    return html

def crawl_sitemap(url):
    sitemap = download(url)
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    for link in links:
        html = download(link)

    return html

def iter_url(url, proxy=None, ca_file=None, delay=0):
    coin_urls = {}
    throttle = Throttle(delay)
    for page in itertools.count(1):
        page_url = urllib.parse.urljoin(url, '/list_{}.html'.format(page))
        throttle.wait(page_url)
        # 此proxy地址为XX-net地址，CA.crt是goagent的CA证书
        #html = download(page_url, proxy="http://192.168.1.148:8087", ca_file='./data/CA.crt')
        html = download(page_url, proxy=proxy, ca_file=ca_file)
        parse = MyHTMLParser(html)
        parse.get_coin_url()
        print(parse.page_coin_urls)
        if not parse.page_coin_urls:
            print(page)
            break
        coin_urls.update(parse.page_coin_urls)
    print(coin_urls)
    print(len(coin_urls))
    for coin_id, coin_url in coin_urls:
        coin_page = download(urllib.parse.urljoin(url, coin_url))
        parse = MyHTMLParser(coin_page)
        parse.get_coin_info()
        des_page = download(urllib.parse.urljoin(url, parse.coin_info['des_url']))


# 默认为1000，使用BeautifulSoup时可能会报异常
sys.setrecursionlimit(2000)