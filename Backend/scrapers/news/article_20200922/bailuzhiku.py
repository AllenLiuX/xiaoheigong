import os
import requests
from lxml import etree
import config
import public_fun


def handle(search_word, page, s_date):
    '''
    获取搜索结果中的文章url
    :param search_word: 搜素关键词
    :param page: 页数
    :return:
    '''
    url = 'http://www.bailuzhiku.com/policy/listResult'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '249',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'UM_distinctid=174b08f0e9f751-046de8b491666e-f7b1332-1fa400-174b08f0ea0753; Hm_lvt_ec196724ce16461e3c277405b7fd5b34=1600690000,1600954535; ASP.NET_SessionId=4rbp124yzypezle4rhpto2ha; CNZZDATA1271635556=2128017459-1600685978-%7C1600961875; login=0AB50DBC033234B887CC04C65CEFDB55DCF4C4D20E676E2871DB5D62CB6E694AE5E7C5FBE096B4CFB0F94A6078317AF2A666E0BBFE4462E589B5A01AAD274038017190521182DE351C4015B5A3BFF55D0D06B214586270CC875C8AFFB237FEF1F14537703D6AECE7D7B1E688FA26A3159ED956F104017DD3648BF4C1A081735331FFFD9D0B7E6A1C504440004CF4B1C1295F39C0; Hm_lpvt_ec196724ce16461e3c277405b7fd5b34=1600962708',
        'Host': 'www.bailuzhiku.com',
        'Origin': 'http://www.bailuzhiku.com',
        'Referer': 'http://www.bailuzhiku.com/policy/list?keyword=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',

    }
    form_data = {
        'pageSize': '20',
        'Keyword': search_word,
        'Type': '0',
        'IsJoinGov': '0',
        'IsQueryDate': '0',
        'EngSortType': '0',
        'EngSearchType': '0',
        'PageIndex': page,
        'PageSize': 20,
        'RowsCount': '0'
    }
    index_url2 = 'http://www.bailuzhiku.com{}'
    res = requests.post(url=url, headers=headers, data=form_data)
    res.encoding = res.apparent_encoding
    html = etree.HTML(res.text)
    data = html.xpath('//*[@class="newsList"]/h3/a/@href')
    date = html.xpath('//*[@class="clearfix"]/li[1]/span/text()')
    result = []
    if data:
        pages = page + 1 if data else 0
        for d in range(len(data)):
            if public_fun.calc_date(s_date=s_date, e_date=date[d]):
                result.append(index_url2.format(data[d]))
        return result, pages
    else:
        print('url1 404错误:', res.status_code, url)
        return [], 0


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
    json_result = {'source': 'blzk', 'doc_id': '', 'date': '', 'download_url': '',
                   'org_name': '', 'page_num': '1', 'doc_type': 'REPORT', 'title': ''}
    path = os.path.join(config.SAVE_PATH, search_word, 'news', 'bailuzhiku')
    res = requests.get(url=url, headers=config.HEADERS)
    html = etree.HTML(res.text)
    content_text = public_fun.filter_space_json(html.xpath('//*[@class="textarea-box policy-textarea"]//text()'))
    if len(content_text) > max_text:
        try:
            doc_id = url.split('/')[-1].replace('.html', '')  # 文章ID
            title = html.xpath('//*[@class="policy-wrap-title"]/h1')[0]  # 文章标题
            description = html.xpath('//*[@class="textarea-box policy-textarea"]')[0]  # 文章内容
            html_list = [title, description]
            html_result = public_fun.filter_space_html(html_list)
            json_result['doc_id'] = doc_id
            json_result['date'] = public_fun.filter_space_json(
                html.xpath('//*[@class="attribute-table"]/tbody/tr[2]/td[1]/div/text()')[0])
            json_result['download_url'] = 'http://www.bailuzhiku.com/' + \
                                          html.xpath('//*[@class="header-tool-link download"]/@href')[0]
            try:
                json_result['org_name'] = public_fun.filter_space_json(
                    html.xpath('//*[@class="attribute-table"]/tbody/tr[1]/td[1]/div/text()')[0])
            except:
                json_result['org_name'] = ''
            json_result['title'] = public_fun.filter_space_json(html.xpath('//h1[@class="title"]/text()')[0])
            public_fun.write_down_json(path=path, filename=doc_id + '.json', text=json_result)
            public_fun.write_down_html(path=path, filename=doc_id + '.html', text=html_result)
        except Exception as e:
            print(e.__traceback__.tb_lineno, url, e)
    else:
        print('文章字数不足', max_text)


def main(search_word, s_date, max_art, max_text):
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
    p1 = '人工智能'
    p2 = '2'
    p3 = 10
    p4 = 500
    r2 = main(search_word=p1, s_date=p2, max_art=p3, max_text=p4)
