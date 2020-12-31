import urllib.request
from urllib.parse import quote
import string
import pdfkit

from bs4 import BeautifulSoup
import json
import re
# from datetime import datetime

def get_urls(keyword, range, sequence, begin_time, end_time, art_num):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'
    }
    url = "https://search.sina.com.cn/?q="+keyword+"&c=news&range="+range+"&sort="+sequence
    if begin_time != "":
        url += "&time="+begin_time[:4]+"&stime="+begin_time+"%2000:00:00"
    if end_time != "":
        url += "&etime="+end_time+"%2023:59:59"
    url += "&num=10"
    url = quote(url, safe=string.printable) #to transcribe Chinese keyword in url

    res = []
    sources = []
    # a = range(3)
    i=1
    while len(res) < art_num:
        cur_url = url+"&page="+str(i)
        i+=1
        print("Searching by: " + cur_url)
        try:
            request = urllib.request.Request(cur_url, headers=header)
            response = urllib.request.urlopen(request, timeout=10.0).read()
        except:
            print('error')
        # print(response)
        result = response.decode('utf-8', 'ignore').replace(u'\xa9', u'')
        # print(result)
        pattern = re.compile('href="(https://.*.sina.com.cn/.*?)"')
        allurl = re.compile(pattern).findall(result)
        res += allurl
        res = list(set(res))
        # pattern2 = re.compile('fgray_time">([^<]+)<')
        # allsrc = re.compile(pattern2).findall(result)
        # sources += allsrc
    if len(res) > art_num:
        res = res[:art_num]
        # sources = sources[:art_num]

    # config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    # pdfkit.from_url(url, 'PDFs/out.pdf', configuration=config)

    return res, sources

def get_json(url, source, soup, name):
    info = {'doc_url': url}
    data = source.split(' ')
    info['source'] = data[0]
    info['date'] = data[1]+data[2]
    with open('PDFs/article'+name+'.json', 'w') as f:
        f.write(json.dumps(info, ensure_ascii=False, indent=4, separators=(',', ':')))



def process_article(url, words_min, name, source):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
    request = urllib.request.Request(url, headers=header)
    response = urllib.request.urlopen(request).read()
    result = response.decode('utf-8', 'ignore').replace(u'\xa9', u'')
    # with open('1.html', 'w') as f:
    #     f.write(result)
    soup = BeautifulSoup(result, features="html.parser")
    art = str(soup.find_all(id="artibody"))

    re_words = re.compile(u"[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]+")
    txt = re.findall(re_words, art)
    txt_all = "".join(txt)
    if len(txt_all) >= words_min:
        print("Downloading article #" + name + url)
        print(txt_all)
        print("Word count: ", len(txt_all))
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        pdfkit.from_url(url, "PDFs/article"+name+'.pdf', configuration=config)
        # get_json(url, source, soup, name)
    # print(result)


def main():
    keyword = input("Keyword: ")
    words_min = input("Minimum words count: ")
    art_num = input("Number of articles: ")
    range = input("Keyword position(all/title): ")
    sequence = input("Sort by(time/rel/count): ")
    begin_time = input("Begin time(yyyy-mm-dd): ")
    end_time = input("End time(yyy-mm-dd): ")
    urls, sources = get_urls(keyword, range, sequence, begin_time, end_time, int(art_num))
    urls = list(set(urls))
    print(urls)
    print(sources)
    print(len(urls), len(sources))
    print("Found articles count: "+str(len(urls)))
    i = 0
    for u in urls:
        print("Processing article #"+str(i))
        process_article(u, int(words_min), str(i), '')
        #process_article(u, int(words_min), str(i), sources[i])
        i += 1
        #next: 用bs获取<h2>并依次获取下面的title，url，source。

if __name__=="__main__":
    main()