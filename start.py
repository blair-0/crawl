#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2018/8/31 13:45
# @Author   : YZH
# @Email    : you_zhihong@aliyun.com
# @File     : start.py
# @Software : PyCharm
import itertools
import urllib.parse
import coin

def crawl(url):
    for page in itertools.count(1):
        page_url = urllib.parse.urljoin(url, '/list_{}.html'.format(page))
        html = coin.CoinPager(page_url, 'coin_list')
        c = coin.CoinParser(html)
        c.get_coin_url()
        for k,v in c.page_coin_urls.items():
            coin_html = coin.CoinPager(urllib.parse.urljoin(html.seed_url, v))
            coin_c = coin.CoinParser(coin_html)
            coin_c.set_type('coin_info')
            coin_c.get_coin_info()
            coin_c.set_type('coin_timeline')
            coin_c.get_coin_timeline()
            coin_c.set_type('coin_markets')
            coin_c.get_coin_markets()
            coin_des_html = coin.CoinPager(urllib.parse.urljoin(html.seed_url, coin_c.coin_des_url), 'coin_des')
            coin_des_c = coin.CoinParser(coin_des_html)
            coin_des_c.get_coin_des()
            print(coin_c.coin_id)
            print(coin_c.coin_hl_price)
            print(coin_des_c.coin_des)
            print(coin_c.coin_whitepaper_url)
            print(coin_c.coin_sites)
            print(coin_c.qr_code)
            print(coin_c.coin_timeline)
            print(coin_c.coin_markets)
            print('-' * 80)
