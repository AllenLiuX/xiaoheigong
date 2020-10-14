import os
import requests
from lxml import etree
import config
import public_fun
from fake_useragent import UserAgent
from definitions import ROOT_DIR


# %%

def handle(url):
    header = {'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=header, verify=False)
    if res.status_code != 404:
        html = etree.HTML(res.text)
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''
    urls = html.xpath('//*[@class="headTit"]/@href')
    times = html.xpath('//*[@class="time"]/text()')  # 获取时间
    times = [t.split(' ')[0].replace('年', '').replace('月', '').replace('日', '') for t in times]  # 修改时间格式
    try:
        next_href = html.xpath('//*[@class="next"]/@href')[0]  # 下一页
    except:
        next_href = ''
    if len(urls) != len(times):
        print('链接长度:', len(urls), '时间长度:', len(times))
        return False
    else:
        result = [urls[n] for n in range(len(urls)) if public_fun.calc_date(times[n])]  # 通过时间过滤url2
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
    :param url:url2 文章内容链接
    :return:
    """
    json_result = {'source': 'lyw', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'NEWS', 'title': ''}
    path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'news', 'leiphone')  # 路径
    header = {'user-agent': str(UserAgent().random)}
    res = requests.get(url=url, headers=header)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="lph-article-comView"]//text()'))  # 正文内容
    if len(content_text) > min_word_count:
        try:
            doc_id = url.split('/')[-1].replace('.html', '')  # 文章ID
            title = html.xpath('//*[@class="article-title"]')[0]  # 标题
            description = html.xpath('//*[@class="lph-article-comView"]')[0]  # 文章内容
            html_list = [title, description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            date = public_fun.filter_space_json(html.xpath('//*[@class="time"]/text()')[0])[:10]
            json_result['date'] = date[0:4] + date[5:7] + date[8:]
            json_result['download_url'] = url
            json_result['org_name'] = html.xpath('//*[@class="aut"]/a/text()')[0]
            json_result['title'] = public_fun.filter_space_json(html.xpath('//*[@class="headTit"]/text()')[0])
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足%s' % min_word_count, url)


def run(search_keyword, min_word_count=3000):
    print('--------Begin searching articles from leiphone--------')
    url1 = 'https://www.leiphone.com/search?s={}'.format(search_keyword)  # 文章url列表
    url2_list = []  # 文章内容url
    while url1:
        one_page_url, href = handle(url1)
        url2_list += one_page_url
        if href and len(url2_list) < 100:
            url1 = href
        else:
            url1 = ''
    url2_list = url2_list[:1] if config.DEBUG else url2_list  # 取十条测试数据
    for url2 in url2_list:
        get_data(url=url2, search_keyword=search_keyword, min_word_count=min_word_count)

    print('--------Finished searching articles from leiphone--------')


if __name__ == '__main__':
    s_w = '人工智能'
    run(search_keyword=s_w, min_word_count=3000)
