# %%

import os
import requests
from lxml import etree
import pandas as pd
import re
import json
from selenium import webdriver
import time
import datetime
import config
import public_fun


# %%

def handle(url):
    res = requests.get(url=url, headers=config.HEADERS)
    if res.status_code != 404:
        res.encoding = res.apparent_encoding
        html = etree.HTML(res.text)
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''
    urls = html.xpath('//*[@class="search-result"]/li/a/@href')
    try:
        index_next_page = 'http://www.767stock.com/searchall{}'
        next_href = index_next_page.format(html.xpath('//*[@class="next page-numbers"]/@href')[0])
    except:
        next_href = ''
    result = [urls[n] for n in range(len(urls))]  # 通过时间过滤url2
    return result, next_href


def get_data(url, search_word, max_text):
    json_result = {'source': 'lqzk', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEW', 'title': ''}
    path = os.path.join(config.SAVE_PATH, search_word, 'news', '767stock')  # 路径
    res = requests.get(url=url, headers=config.HEADERS)
    res.encoding = res.apparent_encoding
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="entry-content"]//text()'))  # 正文内容

    if len(content_text) > max_text:
        try:
            # ==============================html=========================
            doc_id = url.split('/')[-1].replace('.html', '')  # 文章ID
            description = html.xpath('//*[@class="entry-content"]')[0]  # 文章内容 html
            html_list = [description]
            html_result = public_fun.filter_space_html(html_list)
            # ==============================json=========================
            json_result['doc_id'] = doc_id
            json_result['date'] = public_fun.filter_space_json(
                html.xpath('//*[@class="entry-date"]/text()')[0])
            json_result['download_url'] = html.xpath('//*[@class="btn-download"]/@href')[0]
            json_result['org_name'] = public_fun.filter_space_json(
                html.xpath('//*[@class="categories-links"]/a/text()'))
            json_result['title'] = public_fun.filter_space_json(html.xpath('//*[@class="entry-title"]/text()'))
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足', max_text, url)


def main(search_word, s_date, max_art, max_text):
    s_date = public_fun.reduce_date(s_date)
    url1 = 'http://www.767stock.com/searchall?s_key={}'.format(search_word)  # 文章url列表
    url2_list = []  # 文章内容url
    while url1:
        one_page_url, next_page = handle(url=url1)
        url2_list += one_page_url
        if next_page and len(url2_list) < max_art:
            url1 = next_page
        else:
            url1 = ''
    url2_list = url2_list[:5] if config.DEBUG else url2_list  # 取十条测试数据
    for url2 in url2_list:
        get_data(url=url2, search_word=search_word, max_text=max_text)


if __name__ == '__main__':
    p1 = '人工智能'
    p2 = '2'
    p3 = 10
    p4 = 500
    r2 = main(search_word=p1, s_date=p2, max_art=p3, max_text=p4)
