import os
import requests
from lxml import etree
import json
import time
import config
import public_fun


def handle(search_word, page, s_date):
    '''
    获取搜索结果中的文章url
    :param search_word: 搜素关键词
    :param page: 页数
    :return:
    '''
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '84',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'Hm_lvt_45cdb9a58c4dd401ed07126f3c04d3c4=1600778518; awbYHQXTK=hWXM8jexf8P1LNW3PFuVLBgok//nLLJ+nomeP5Asslw/aUaMi+6U/DxZ1GX80rC5VmNz4wCg0JQsIajjZ2tIWw==; Hm_lpvt_45cdb9a58c4dd401ed07126f3c04d3c4=1600779082',
        'Host': 'abc.aiweibang.com',
        'Origin': 'http://abc.aiweibang.com',
        'Referer': 'http://abc.aiweibang.com/daily/news/0?hour=12&search=true&kw=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    form_data = {
        'PageIndex': page,
        'PageSize': '20',
        'KeyWord': search_word,
        'Date': time.strftime("%Y-%m-%d", time.localtime())
    }
    # index_url2 = 'https://www.huxiu.com/article/{}.html'
    url = 'http://abc.aiweibang.com/daily/news_list'
    res = requests.post(url=url, headers=headers, data=form_data)
    data = json.loads(res.text)
    result = []
    if res.status_code != 404:
        pages = page + 1 if data['HasNextPage'] == True else False
        for d in data['Datas']:
            # timeArray = time.localtime(d['dateline']) #时间戳转换时间
            # date = time.strftime("%Y-%m-%d", timeArray)
            if public_fun.calc_date(s_date=s_date, e_date=d['PublicTimeFmt'].split()[0]) and '网易新闻' in d['SourceName']:
                result.append(d['Url'])
        return result, pages
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''


def get_data(url, search_word, max_text):
    '''
    1. 网站来源 “source”（白鲸出海“bjch”/未来智库“wlzk”……）
    2. 文章ID “doc_id”（在所爬取的网页的id）
    3. 发表日期 “date”（格式：20200129）
    4. 下载url “download_url”
    5. 作者/机构 “org_name”（如 xx券商/xx证券)
    6. 页数/字数 “page_num”/ “word_count”，如果有pdf文件就用页数，没有就用字数
    7. 资料种类 “doc_type”（研报： “EXTERNAL_REPORT”/咨询： “NEWS”）
    8. 文章标题 “title” ("中芯国际：首次公开发行股票并在科创板上市招股说明书")
    :param search_word: 搜索关键词
    :param url:url2 文章内容链接
    :return:
    '''
    # url = 'https:' + url if url.startswith('//') else url
    json_result = {'source': 'awb', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEW', 'title': ''}
    path = os.path.join(config.SAVE_PATH, search_word, 'news', 'aiweibang')
    res = requests.get(url=url, headers=config.HEADERS)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="post_text"]//text()'))
    if len(content_text) > max_text:
        try:
            doc_id = url.split('/')[-1].replace('.html', '')  # 文章ID
            description = html.xpath('//*[@class="post_body"]')[0]  # 文章内容
            html_list = [description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            json_result['date'] = public_fun.filter_space_json(html.xpath('//*[@class="post_time_source"]/text()')[0])[
                                  :10]
            json_result['download_url'] = url
            json_result['org_name'] = public_fun.filter_space_json(html.xpath('//*[@id="ne_article_source"]/text()')[0])
            json_result['title'] = public_fun.filter_space_json(
                html.xpath('///*[@class="post_content_main"]/h1/text()')[0])
            public_fun.write_down_json(path=path, filename=doc_id[-10:] + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id[-10:] + '.html', text=html_result)
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
    page = 1
    url2_list = []
    while page:
        one_page_url, pages = handle(search_word=search_word, page=page, s_date=s_date)
        url2_list += one_page_url
        if len(url2_list) < max_art and page < int(pages):
            page += 1
        else:
            page = 0
    # return url2_list
    url2_list = url2_list[:5] if config.DEBUG else url2_list
    for url2 in url2_list:
        get_data(url=url2, search_word=search_word, max_text=max_text)


if __name__ == '__main__':
    max_art = 100
    max_text = 500
    s_date = '2018-01-01'
    s_w = '人工智能'
    r2 = main(search_word=s_w, max_art=max_art, max_text=max_text, s_date=s_date)
