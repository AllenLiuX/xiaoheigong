import os
import requests
from lxml import etree
import pandas as pd
import re
import json
from selenium import webdriver
import time
import datetime


# %%
import config
import public_fun


def handle(search_word, page, s_date):
    '''
    获取搜索结果中的文章url
    :param search_word: 搜素关键词
    :param page: 页数
    :return:
    '''
    #     headers=  {
    #     'Accept': 'application/json, text/javascript, */*; q=0.01',
    #     'Accept-Encoding': 'gzip, deflate',
    #     'Accept-Language': 'zh-CN,zh;q=0.9',
    #     'Connection': 'keep-alive',
    #     'Content-Length': '84',
    #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #     'Cookie': 'Hm_lvt_45cdb9a58c4dd401ed07126f3c04d3c4=1600778518; awbYHQXTK=hWXM8jexf8P1LNW3PFuVLBgok//nLLJ+nomeP5Asslw/aUaMi+6U/DxZ1GX80rC5VmNz4wCg0JQsIajjZ2tIWw==; Hm_lpvt_45cdb9a58c4dd401ed07126f3c04d3c4=1600779082',
    #     'Host': 'abc.aiweibang.com',
    #     'Origin': 'http://abc.aiweibang.com',
    #     'Referer': 'http://abc.aiweibang.com/daily/news/0?hour=12&search=true&kw=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    #     'X-Requested-With': 'XMLHttpRequest'
    # }
    url = 'https://www.ifenxi.com/api/csp/search/content?content={}&pageNum={}&pageSize=10'.format(search_word, page)
    index_url2 = 'https://www.ifenxi.com/trend/{}'
    res = requests.get(url=url, headers=config.HEADERS)
    data = json.loads(res.text)
    result = []
    if data['status'] == 200:
        pages = data['data']['pages']
        for d in data['data']['list']:
            e_date = d['date'].replace('年', '-').replace('月', '-').replace('日', '')
            if public_fun.calc_date(s_date=s_date, e_date=e_date):
                result.append(index_url2.format(d['content_id']))
        return result, pages
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''


def get_data(url, search_word, max_text):
    json_result = {'source': 'afx', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEW', 'title': ''}
    path = os.path.join(config.SAVE_PATH, search_word, 'news', 'ifenxi')
    res = requests.get(url=url, headers=config.HEADERS)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="trend-content__main"]//text()'))
    if len(content_text) > max_text:
        try:
            doc_id = url.split('/')[-1]  # 文章ID
            title = html.xpath('//*[@class="meeting-banner__body-content-title"]')[0]  # 文章标题
            description = html.xpath('//*[@class="trend-content__main"]')[0]  # 文章内容
            html_list = [title, description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            json_result['date'] = public_fun.filter_space_json(
                html.xpath('//*[@class="trend-content__main-date"]//span/text()')[0]
                    .replace('年', '-').replace('月', '-').replace('日', ''))
            if html.xpath('//*[@class="trend-content__main-body-right-report"]'):
                json_result['download_url'] = 'https://www.ifenxi.com/api/csp/content/download/report/{}'.format(doc_id)
            else:
                json_result['download_url'] = ''
            try:
                json_result['org_name'] = public_fun.filter_space_json(
                    html.xpath('//*[@class="trend-content__main-editor"]//span//text()')[0])
            except:
                json_result['org_name'] = ''
            json_result['title'] = public_fun.filter_space_json(
                html.xpath('//*[@class="meeting-banner__body-content-title"]/text()')[0])
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足', max_text)


def main(search_word, max_art, max_text, s_date):
    '''
    铅笔道爬虫入口函数
    :param search_word:搜索关键词
    :return: None
    '''
    s_date = public_fun.reduce_date(s_date)
    page = 1
    url2_list = []
    while page:
        one_page_url, pages = handle(search_word=search_word, page=page, s_date=s_date)
        url2_list += one_page_url
        if len(url2_list) < max_art and page < int(pages):
            page += 1
        else:
            page = 0
    url2_list = url2_list[:5] if config.DEBUG else url2_list
    for url2 in url2_list:
        get_data(url=url2, search_word=search_word, max_text=max_text)


if __name__ == '__main__':
    p0 = '人工智能'
    p1 = 10
    p2 = 500
    p3 = '2'
    r2 = main(search_word=p0, max_art=p1, max_text=p2, s_date=p3)
