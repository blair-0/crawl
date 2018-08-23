#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/23 12:52
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : main.py
# @Software : PyCharm

import urllib

def download(url, num_retries=2):
    print('Downloading:', url)
    try:
        html = urllib.request.urlopen(url).read()
    except urllib.error.URLError as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # 返回 5xx 错误则重试
                return download(url, num_retries-1)
    return html