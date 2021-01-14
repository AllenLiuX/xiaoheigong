import json
import os
import re
import time
from datetime import datetime

import requests
from fake_useragent import UserAgent
from lxml import etree

import Backend.storage.mongodb as mg
import config
import public_fun
from definitions import ROOT_DIR
from utils import bwlist
from utils.errors import updateError


def get_pdf_urls(search_keyword, page):
    """
    获取搜索结果中的文章url
    :param search_keyword: 搜素关键词
    :param page: 页数
    :return: [list of 文章 urls],
    """
    index_url2 = 'https://www.huxiu.com/article/{}.html'
    url = 'https://search-api.huxiu.com/api/article?platform=www&s={}&sort=&page={}&pagesize=20'.format(search_keyword,
                                                                                                        page)
    header = {'user-agent': str(UserAgent().random)}
    res = requests.post(url=url, headers=header)

    try:
        data = json.loads(res.text)
        result = []
        pages = data['data']['total_pages']
        for d in data['data']['datalist']:
            timeArray = time.localtime(d['dateline'])
            date = time.strftime("%Y-%m-%d", timeArray)
            if public_fun.calc_date(date) and not d['is_video_article']:  # 时间过滤且不说视文章
                result.append(index_url2.format(d['aid']))
        print('--------Found %d articles from huxiu--------' % len(result))
        return result, pages
    except:
        updateError("ResponseError: Empty response when downloading from huxiu. Status code: " + str(res.status_code))
        return [], None


def download_articles(url, search_keyword, min_word_count, get_pdf, summary):
    """
    1. 网站来源 “source”（白鲸出海“bjch”/未来智库“wlzk”……）
    2. 文章ID “doc_id”（在所爬取的网页的id）
    3. 发表日期 “date”（格式：20200129）
    4. 下载url “download_url”
    5. 作者/机构 “org_name”（如 xx券商/xx证券)
    6. 页数/字数 “page_num”/ “word_count”，如果有pdf文件就用页数，没有就用字数
    7. 资料种类 “doc_type”（研报： “EXTERNAL_REPORT”/咨询： “NEWS”）
    8. 文章标题 “title” ("中芯国际：首次公开发行股票并在科创板上市招股说明书")
    :param summary: the summary file
    :param get_pdf: 是否要创建html文件
    :param min_word_count: 最少字数限制
    :param search_keyword: 搜索关键词
    :param url:url2 文章内容链接
    :return:
    """
    json_result = {'source': 'huxiu',
                   'doc_id': '',
                   'date': '',
                   'download_url': '',
                   'org_name': '',
                   'doc_type': 'NEWS',
                   'title': '',
                   'oss_path': '',
                   'has_pdf': 'html',
                   'content': '',
                   'filtered': 0,
                   'search_keyword': search_keyword}
    path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'html', 'huxiu')
    header = {'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=header)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="article__bottom-content__right fl"]//text()'))

    if len(content_text) > min_word_count:
        doc_id = re.findall('\d+', string=url)[0]  # 文章ID

        # Blacklist
        blacklist = bwlist.BWList(search_keyword, 'black')
        blacklist_exist = blacklist.bwlist_exist()

        if blacklist_exist and blacklist.in_bwlist(doc_id, 'huxiu'):
            return

        # whitelist by database
        id_match_res = mg.show_datas('articles', query={'doc_id': str(doc_id),
                                                        'search_keyword': search_keyword})  # new whitelist --vincent
        if id_match_res:
            print('article #' + str(doc_id) + ' is already in database. Skipped.')
            return

        try:
            description = html.xpath('//*[@id="article_read"]')[0]  # 文章内容
            html_list = [description]
            html_result = public_fun.filter_space_html(html_list)

            json_result['doc_id'] = doc_id
            json_result['date'] = html.xpath('//*[@class="article__time"]/text()')[0].split()[0]
            json_result['download_url'] = url
            json_result['org_name'] = html.xpath('//*[@class="author-info__username"]/text()')[0]
            json_result['title'] = html.xpath('//*[@class="article__title"]/text()')[0]
            json_result['content'] = content_text

            # Downloading
            print('Downloading article %s' % doc_id)
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)

            if get_pdf:
                public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)

            summary['data'].append(json_result.copy())
        except Exception as e:
            updateError(
                'Download Error: Error occurred when downloading article from huxiu. \n' + str(e.__traceback__.tb_lineno) + ": " + str(e))
    else:
        print('文章字数不足' + str(min_word_count), url)


def run(search_keyword, min_word_count, get_pdf):
    """
    铅笔道爬虫入口函数
    :param min_word_count: 最少字数限制
    :param search_keyword:搜索关键词
    :return: None
    """
    print('--------Begin searching articles from huxiu--------')
    os.chdir(ROOT_DIR)

    page = 1
    url2_list = []
    summary = {}

    summary.update({'source': '36kr'})
    summary.update({'has_pdf': 'html'})
    summary.update({'search_keyword': search_keyword})
    summary.update({'search_time': str(datetime.now().date())})
    summary.update({'data': []})

    while page:
        one_page_url, pages = get_pdf_urls(search_keyword=search_keyword, page=page)
        if pages is None:
            return
        url2_list += one_page_url
        if len(url2_list) < 100 and page < int(pages):
            page += 1
        else:
            page = 0

    url2_list = url2_list[:3] if config.DEBUG else url2_list
    for url2 in url2_list:
        download_articles(url=url2, search_keyword=search_keyword, min_word_count=min_word_count, get_pdf=get_pdf,
                          summary=summary)

    with open(os.path.join('cache', search_keyword, 'html', 'huxiu', 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

    print('--------Finished downloading articles from huxiu--------')


if __name__ == '__main__':
    s_w = '腾讯'
    run(search_keyword=s_w, min_word_count=0, get_pdf=True)
