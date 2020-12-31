import os
import requests
from lxml import etree
import config
import public_fun


def handle(url, s_date):
    res = requests.get(url=url, headers=config.HEADERS, verify=False)
    if res.status_code != 404:
        res.encoding = res.apparent_encoding
        html = etree.HTML(res.text)
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''
    urls = html.xpath('//*[@class="m-list2 m-list2-sear"]//@href')
    times = html.xpath('//*[@class="time"]/text()')  # 获取时间
    try:
        index_next_page = 'https://s.iresearch.cn{}'
        title = html.xpath('//*[@class="m-page m-page-lt f-mt-auto"]/a/text()')
        href = html.xpath('//*[@class="m-page m-page-lt f-mt-auto"]/a/@href')
        for n in range(len(title)):
            if '下一页' in title[n]:
                next_href = index_next_page.format(href[n])
    except:
        next_href = ''
    if len(urls) != len(times):
        print('链接长度:', len(urls), '时间长度:', len(times))
        return False
    else:
        result = [urls[n] for n in range(len(urls)) if
                  public_fun.calc_date(s_date=s_date, e_date=times[n])]  # 通过时间过滤url2
    return result, next_href


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
    json_result = {'source': 'irw', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'REPORT', 'title': ''}
    path = os.path.join(config.SAVE_PATH, search_word, 'news', 'iresearch')  # 路径
    res = requests.get(url=url, headers=config.HEADERS)
    res.encoding = res.apparent_encoding
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="m-article"]//text()'))  # 正文内容

    if len(content_text) > max_text:
        try:
            # ==============================html=========================
            doc_id = url.split('/')[-1].replace('.shtml', '')  # 文章ID
            title = html.xpath('//*[@class="m-cont-hd"]')[0]  # 标题
            description = html.xpath('//*[@class="m-article"]')[0]  # 文章内容 html
            html_list = [title, description]
            html_result = public_fun.filter_space_html(html_list)
            # ==============================json=========================
            json_result['doc_id'] = doc_id
            json_result['date'] = public_fun.filter_space_json(html.xpath('//*[@class="origin"]/em/text()')[0]
                                                               .replace('年', '-').replace('月', '-').replace('日', '')[:10])
            json_result['download_url'] = url
            json_result['org_name'] = public_fun.filter_space_json(html.xpath('//*[@class="origin"]/span/text()'))
            json_result['title'] = public_fun.filter_space_json(html.xpath('//*[@class="title"]//text()'))
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足', max_text, url)


def main(search_word, s_date, max_art, max_text):
    s_date = public_fun.reduce_date(s_date)
    url1 = 'https://s.iresearch.cn/news/{}/'.format(search_word)  # 文章url列表
    url2_list = []  # 文章内容url
    while url1:
        one_page_url, href = handle(url=url1, s_date=s_date)
        url2_list += one_page_url
        if href and len(url2_list) < max_art:
            url1 = href
        else:
            url1 = ''
    url2_list = url2_list[:5] if config.DEBUG else url2_list  # 取十条测试数据
    for url2 in url2_list:
        get_data(url=url2, search_word=search_word, max_text=max_text)


if __name__ == '__main__':
    p0 = '人工智能'
    p1 = 10
    p2 = 500
    p3 = '5'
    r = main(search_word=p0, s_date=p3, max_art=p1, max_text=p2)
