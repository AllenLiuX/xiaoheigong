import os
import requests
from lxml import etree
import re
import json
import time
import config
import public_fun
from fake_useragent import UserAgent
from definitions import ROOT_DIR


def handle(search_keyword, page):
    """
    获取搜索结果中的文章url
    :param search_keyword: 搜素关键词
    :param page: 页数
    :return:
    """
    index_url2 = 'https://www.huxiu.com/article/{}.html'
    url = 'https://search-api.huxiu.com/api/article?platform=www&s={}&sort=&page={}&pagesize=20'.format(search_keyword,
                                                                                                        page)
    header = {'user-agent': str(UserAgent().random)}
    res = requests.post(url=url, headers=header)
    data = json.loads(res.text)
    result = []
    if data['success']:
        pages = data['data']['total_pages']
        for d in data['data']['datalist']:
            timeArray = time.localtime(d['dateline'])
            date = time.strftime("%Y-%m-%d", timeArray)
            if public_fun.calc_date(date) and not d['is_video_article']:  # 时间过滤且不说视文章
                result.append(index_url2.format(d['aid']))
        return result, pages
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''


def get_data(url, search_keyword, min_word_count):
    """
    1. 网站来源 “source”（白鲸出海“bjch”/未来智库“wlzk”……）
    2. 文章ID “doc_id”（在所爬取的网页的id）
    3. 发表日期 “date”（格式：20200129）
    4. 下载url “download_url”
    5. 作者/机构 “org_name”（如 xx券商/xx证券)
    6. 页数/字数 “page_num”/ “word_count”，如果有pdf文件就用页数，没有就用字数
    7. 资料种类 “doc_type”（研报： “EXTERNAL_REPORT”/咨询： “NEWS”）
    8. 文章标题 “title” ("中芯国际：首次公开发行股票并在科创板上市招股说明书")
    :param min_word_count: 最少字数限制
    :param search_keyword: 搜索关键词
    :param url:url2 文章内容链接
    :return:
    """
    json_result = {'source': 'qbd', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEWS', 'title': ''}
    path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'news', 'huxiu')
    header = {'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=header)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="article__bottom-content__right fl"]//text()'))
    if len(content_text) > min_word_count:
        try:
            doc_id = re.findall('\d+', string=url)[0]  # 文章ID
            description = html.xpath('//*[@id="article_read"]')[0]  # 文章内容
            html_list = [description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            json_result['date'] = html.xpath('//*[@class="article__time"]/text()')[0].split()[0].replace('-', '')
            json_result['download_url'] = url
            json_result['org_name'] = html.xpath('//*[@class="author-info__username"]/text()')[0]
            json_result['title'] = html.xpath('//*[@class="article__title"]/text()')[0]
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足3000', url)


def run(search_keyword, min_word_count=3000):
    """
    铅笔道爬虫入口函数
    :param min_word_count: 最少字数限制
    :param search_keyword:搜索关键词
    :return: None
    """
    print('--------Begin searching articles from huxiu--------')
    page = 1
    url2_list = []
    while page:
        one_page_url, pages = handle(search_keyword=search_keyword, page=page)
        url2_list += one_page_url
        if len(url2_list) < 100 and page < int(pages):
            page += 1
        else:
            page = 0
    url2_list = url2_list[:1] if config.DEBUG else url2_list
    for url2 in url2_list:
        get_data(url=url2, search_keyword=search_keyword, min_word_count=min_word_count)
    print('--------Finished searching articles from huxiu--------')


if __name__ == '__main__':
    s_w = '人工智能'
    run(search_keyword=s_w, min_word_count=3000)
