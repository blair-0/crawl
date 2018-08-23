#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/23 12:52
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : main.py
# @Software : PyCharm

import urllib, re

def download(url,
             user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/68.0.3440.106 Safari/537.36',
             num_retries=2):
    print('Downloading:', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
        html = urllib.request.urlopen(request).read().decode()
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