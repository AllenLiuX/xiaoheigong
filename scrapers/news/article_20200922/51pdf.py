import os
import requests
from lxml import etree
import config
import public_fun


def handle(url, s_date, search_word):
    print(url)
    res = requests.get(url=url, headers=config.HEADERS, verify=False)
    if res.status_code != 404:
        res.encoding = res.apparent_encoding
        html = etree.HTML(res.text)
    else:
        print('url1 404错误:', res.status_code, url)
        return [], ''
    urls = html.xpath('//a[@class="rlist"]/@href')
    titles = html.xpath('//a[@class="rlist"]/text()')
    index_next_page = 'http://www.51pdf.cn{}'
    label = html.xpath('//*[@id="ctl00_web_center_AspPager"]/table/tbody/tr/td[1]/a[4]/@href')
    next_href = index_next_page.format(label[0]) if len(label) > 0 else None
    path = os.path.join(config.SAVE_PATH, search_word, 'news', '51pdf')  # 路径

    for n in range(len(urls)):
        json_result = {'source': 'jczxw', 'doc_id': '', 'date': '', 'download_url': '',
                       'org_name': '', 'page_num': '1', 'doc_type': 'NEW', 'title': ''}
        json_result['doc_id'] = urls[n].split('/')[-1].replace('.html', '')
        # json_result['date'] = date_list[date_list(n)]
        json_result['download_url'] = index_next_page.format(urls[n])
        json_result['title'] = titles[n]
        public_fun.write_down_json(path=path, filename=json_result['doc_id'] + '.json', text=json_result)
    return next_href


def main(search_word, s_date, max_art, max_text):
    # s_date = public_fun.reduce_date(s_date)
    si_list = ['98', '99', '16', '15', '14', '13', '12', '11', '10', '9', '6', '7', '8']
    url2_list = []  # 文章内容url
    for si in si_list[:int(s_date)]:
        url1 = 'http://www.51pdf.cn/search.aspx?si={}&ft=0&keyword={}'.format(si, search_word)  # 文章url列表
        while url1:
            next_page = handle(url=url1, s_date=s_date, search_word=search_word)
            if next_page and len(url2_list) < max_art:
                url1 = next_page
            else:
                url1 = ''


if __name__ == '__main__':
    p1 = '人工智能'
    p2 = '2'
    p3 = 10
    p4 = 500
    r2 = main(search_word=p1, s_date=p2, max_art=p3, max_text=p4)
