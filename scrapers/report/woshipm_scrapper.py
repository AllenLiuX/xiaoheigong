import urllib.request
from urllib.parse import quote
import string
import pdfkit
from PyPDF2 import PdfFileReader
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re
import os
import sys
import getopt
import time
from definitions import ROOT_DIR, OSS_PATH
import oss.mongodb as mg
import oss.oss as ossfile


def get_pagenum(path):
    reader = PdfFileReader(path)
    if reader.isEncrypted:
        reader.decrypt('')
    page_num = reader.getNumPages()
    return page_num


def get_url_dynamic(url):
    chrome_driver = '/usr/local/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path = chrome_driver, chrome_options=chrome_options)
#    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    html_text = driver.page_source
    # driver.quit()
#    print(html_text)
    return html_text


def get_urls(searchword, begin_time, art_num):
    url = "http://api.woshipm.com/search/list.html?tab=0&key=" + searchword + "&sortType=1"
    url = quote(url, safe=string.printable)  # to transcribe Chinese searchword in url
    res = []
    page = 1
    while len(res) < art_num:
        cur_url = url + "&page=" + str(page)
        page += 1
        print("Searching by: " + cur_url)
        # # 3 Selenium method
        try:
            # print(get_url_dynamic(cur_url))
            response = get_url_dynamic(cur_url)
        except:
            print('Error')
        # print(response)
        # with open('page2.html', 'w') as f:
        #     f.write(response)
        soup = BeautifulSoup(response, features="html.parser")
        articles = soup.find_all(class_='clearfix row article-cont')

        id_cach = [art['id'] for art in articles]
        if len(id_cach) < 20:  # 最后一页
            res += id_cach
            break
        res += id_cach[:art_num % 20]
    print(res)
    return res


def form_json(id, soup, content, searchword, begin_time, current_path, oss_path, get_pdf):
    info = {}
    # 获取时间
    date = soup.find_all('time')[0].text
    print('date:', date)
    s_time = time.mktime(time.strptime(begin_time, '%Y-%m-%d'))
    e_time = time.mktime(time.strptime(date, '%Y-%m-%d'))
    if s_time > e_time:
        print('Date exceed begin time found. Skip the following articles.')
        return False
    info['date'] = date
    # 获取id, type, source, author
    info['doc_id'] = int(id)
    info['doc_type'] = 'report'
    info['source'] = '人人都是产品经理'
    info['url'] = 'http://www.woshipm.com/pd/' + id + '.html'
    info['pdf_url'] = OSS_PATH + oss_path
    info['content'] = content
    author = soup.find(class_='author u-flex').find('a').text
    print('author:', author)
    info['author'] = author
    # 获取页数
    # print(path)
    pdf_save_path = os.path.join(current_path, id + '.pdf')
    if get_pdf:
        page_num = get_pagenum(pdf_save_path)
    else:
        page_num = -1
    print("Number of pages:", page_num)
    info['page_num'] = page_num
    # 获取title
    title = soup.find_all(class_='article--title')[0].text
    print('title:', title)
    info['title'] = title
    # print(info)
    json_save_path = os.path.join(current_path, id + '.json')
    with open(json_save_path, 'w') as f:
        f.write(json.dumps(info, ensure_ascii=False, indent=4, separators=(',', ':')))
    # store into mongodb
    mg.insert_data(info, 'woshipm')
    return True


def calc_keywords(content, keywords):
    keys = keywords.split(',')
    stats = {}
    for i in keys:
        count = len(re.findall(i, content))
        stats[i] = count
    print(stats)


def process_article(id, words_min, searchword, keywords, begin_time, get_pdf: bool):
    url = "http://www.woshipm.com/pd/" + id + ".html"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}

    try:
        request = urllib.request.Request(url, headers=header)
        response = urllib.request.urlopen(request).read()
        result = response.decode('utf-8', 'ignore').replace(u'\xa9', u'')
    except:
        print('error: page not found.')
        return
    soup = BeautifulSoup(result, features="html.parser")
    # 获取纯文本信息raw_txt
    # content = str(soup.find_all(class_="article--content grap"))
    # re_words = re.compile(u"[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]+")
    # txt = re.findall(re_words, content)
    # raw_txt = "".join(txt)
    txt = soup.find(class_="article--content grap").find_all('p')
    raw_txt = ""
    for t in txt:
        raw_txt += t.text

    if len(raw_txt) >= words_min:  # 判断文本长度
        calc_keywords(raw_txt, keywords)
        # 转换pdf
        print("Word count: ", len(raw_txt))
        print("Downloading article #" + id + ' ' + url)
        # print("content:", raw_txt)
        os.chdir(ROOT_DIR)
        keyword_dir = os.path.join(ROOT_DIR, 'cache', searchword)
        current_path = os.path.join(keyword_dir, 'report', 'woshipm')
        pdf_save_path = os.path.join(current_path, str(id) + '.pdf')
        oss_path = 'report/woshipm/' + id + '.pdf'

        if get_pdf:
            config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
            pdfkit.from_url(url, pdf_save_path, configuration=config)

            # 上传pdf to oss
            print('Uploading file to ali_oss at ' + OSS_PATH + oss_path)
            ossfile.upload_file(oss_path, pdf_save_path)

        # 获取json信息
        conti = form_json(id, soup, raw_txt, searchword, begin_time, current_path, oss_path, get_pdf)
        if conti == False:
            return False
    # print(result)
    return True


def main():
    """
    Two modes: directed run without options / called with 5 optional options: searchword, words_min, begin_time, art_num, and keywords.
    """
    searchword, words_min, begin_time, art_num, keywords = '', '', '', '', ''
    if len(sys.argv) == 1:
        searchword = input("Searchword: ")
        words_min = input("Min words count: ")
        begin_time = input("End time(yyyy-mm-dd): ")
        art_num = input("Max number of articles: ")
        keywords = input("keywords: ")
    else:
        opts, args = getopt.getopt(sys.argv[1:], '-s:-w:-e:-a:-k:',
                                   ['searchword=', 'words_min=', 'begin_time=', 'art_num=', 'keywords='])
        for opt_name, opt_value in opts:
            if opt_name in ('-s', 'searchword'):
                searchword = opt_value
            if opt_name in ('-w', 'words_min'):
                words_min = opt_value
            if opt_name in ('-e', 'begin_time'):
                begin_time = opt_value
            if opt_name in ('-a', 'art_num'):
                art_num = opt_value
            if opt_name in ('-k', 'keywords'):
                keywords = opt_value
    # set default values
    if searchword == '':
        searchword = '中芯国际'
    if words_min == '':
        words_min = str(3000)
    if begin_time == '':
        cur = datetime.now()
        before = cur - timedelta(days=1095)
        begin_time = before.strftime("%Y-%m-%d")
        print(begin_time)
    if art_num == '':
        art_num = 30
    if keywords == '':
        keywords = '战略,进步,成功,失败,生长,增长'
    if searchword not in os.listdir():
        os.mkdir(searchword)
    ids = get_urls(searchword, begin_time, int(art_num))
    print("Found articles count: " + str(len(ids)))
    for id in ids:
        print("Processing article #" + str(id))
        status = process_article(id, int(words_min), searchword, keywords, begin_time)
        if not status:
            break


def run(searchword='中芯国际', words_min='3000', num_years='', art_num=30, keywords='', get_pdf=False):
    # set default values
    if num_years == '':
        cur = datetime.now()
        before = cur - timedelta(days=1095)
        begin_time = before.strftime("%Y-%m-%d")
        print(begin_time)
    else:
        cur = datetime.now()
        before = cur - timedelta(days=365 * num_years)
        begin_time = before.strftime("%Y-%m-%d")
        print(begin_time)
    if keywords == '':
        keywords = '战略,进步,成功,失败,生长,增长'
    # if searchword not in os.listdir():
    #     os.mkdir(searchword)
    ids = get_urls(searchword, begin_time, int(art_num))
    print("Found articles count: " + str(len(ids)))
    # os.chdir(ROOT_DIR)
    keyword_dir = os.path.join(ROOT_DIR, 'cache', searchword)
    if searchword not in os.listdir('cache'):
        os.mkdir(keyword_dir)
    if 'report' not in os.listdir(keyword_dir):
        os.mkdir(os.path.join(keyword_dir, 'report'))
    if 'woshipm' not in os.listdir(os.path.join(keyword_dir, 'report')):
        os.mkdir(os.path.join(keyword_dir, 'report', 'woshipm'))
    for id in ids:
        print("Processing article #" + str(id))
        # check whether or not already in database
        id_match_res = mg.show_datas('woshipm', query={'doc_id': int(id)})
        # print(id_match_res)
        if id_match_res:
            print('article #' + id + ' is already in database. Skipped.')
            continue
        status = process_article(id, int(words_min), searchword, keywords, begin_time, get_pdf)
        if status == False:
            break
    mg.show_datas('woshipm')


if __name__ == "__main__":
    main()
