import requests
from lxml import etree
import re
import public_fun
import os
import config
from definitions import ROOT_DIR
from fake_useragent import UserAgent


def handle(url):
    """
    获取搜索结果的url
    :param url: 搜索页+关键词
    :return: result [url1, url2, ...]   next_page:href
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'PHPSESSID=f5pbqgnne76q3g1iih7negoln7; UM_distinctid=1747610c8df414-0de223f07fc9bc-f7b1332-1fa400-1747610c8e085c; CNZZDATA1271043741=874702121-1599707561-%7C1599707561; _ga=GA1.2.1978657859.1599708646; _gid=GA1.2.81853126.1599708646; Hm_lvt_87f4295096911356c216471e93f4f79b=1599708646; Hm_lpvt_87f4295096911356c216471e93f4f79b=1599708876; SERVERID=96b3c19190467e9ce466041807d49236|1599708888|1599708646',
        'referer': 'https://www.iyiou.com/search?p=%E4%B8%AD%E8%8A%AF%E5%9B%BD%E9%99%85',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=headers)
    if res.status_code != 404:
        html = etree.HTML(res.text)
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''
    urls = html.xpath('//div[@class="text fl"]/a/@href')
    times = html.xpath('//div[@class="time"]/text()')
    try:
        next_href = html.xpath('//a[@class="next"]/@href')[0]
    except:
        next_href = ''
    if len(urls) != len(times):
        print('链接长度:', len(urls), '时间长度:', len(times))
        return False
    else:
        result = [urls[n] for n in range(len(urls)) if
                  public_fun.calc_date(times[n]) and urls[n].startswith('https://www.iyiou.com/p')]
    return result, next_href


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
    :param url:
    :return:
    """
    print(url)
    json_result = {'source': 'yo', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEWS', 'title': ''}
    path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'news', 'iyiou')
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'PHPSESSID=f5pbqgnne76q3g1iih7negoln7; UM_distinctid=1747610c8df414-0de223f07fc9bc-f7b1332-1fa400-1747610c8e085c; CNZZDATA1271043741=874702121-1599707561-%7C1599707561; _ga=GA1.2.1978657859.1599708646; _gid=GA1.2.81853126.1599708646; Hm_lvt_87f4295096911356c216471e93f4f79b=1599708646; Hm_lpvt_87f4295096911356c216471e93f4f79b=1599708876; SERVERID=96b3c19190467e9ce466041807d49236|1599708888|1599708646',
        'referer': 'https://www.iyiou.com/search?p=%E4%B8%AD%E8%8A%AF%E5%9B%BD%E9%99%85',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=headers)
    html = etree.HTML(res.text)
    content = html.xpath('//div[@id="post_content"]')[0]
    content_text = public_fun.filter_space_json(html.xpath('//div[@id="post_content"]//text()'))
    if len(content_text) > min_word_count:
        try:
            doc_id = re.findall('\d+', string=url)[0]  # 文章ID
            post_title = html.xpath('//h1[@id="post_title"]')[0]
            post_info = html.xpath('//div[@id="post_info"]')[0]
            post_brief = html.xpath('//div[@id="post_brief"]')[0]
            post_thumbnail = html.xpath('//div[@id="post_thumbnail"]')[0]
            post_description = html.xpath('//div[@id="post_description"]')[0]
            html_list = [post_title, post_info, post_brief, post_thumbnail, post_description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            date = html.xpath('.//div[@id="post_date"]/text()')[0].split()[0]
            json_result['date'] = date[0:4] + date[5:7] + date[8:10]
            json_result['download_url'] = url
            try:
                json_result['org_name'] = public_fun.filter_space_json(html.xpath('//div[@id="post_author"]/a/text()'))
            except:
                json_result['org_name'] = ''
            json_result['title'] = html.xpath('//h1[@id="post_title"]/text()')[0]
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)


def run(search_keyword, min_word_count=3000):
    """
    亿欧爬虫入口函数
    :param min_word_count: 最少字数限制
    :param search_keyword:搜索关键词
    :return:
    """
    print('--------Begin searching articles from iyiou--------')
    url1 = 'https://www.iyiou.com/search?p={}'.format(search_keyword)  # 文章url列表
    index_url = 'https://www.iyiou.com'
    url2_list = []  # 文章内容url
    while url1:
        one_page_url, href = handle(url1)
        url2_list += one_page_url
        if href and len(url2_list) < 100:
            url1 = index_url + href
        else:
            url1 = ''
    url2_list = url2_list[:1] if config.DEBUG else url2_list  # 取十条测试数据
    for url2 in url2_list:
        get_data(url=url2, search_keyword=search_keyword, min_word_count=min_word_count)

    print('--------Finished searching articles from iyiou--------')


if __name__ == '__main__':
    kw = '人工智能'
    run(search_keyword=kw, min_word_count=3000)
