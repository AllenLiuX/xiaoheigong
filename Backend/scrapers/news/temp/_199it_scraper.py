# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from common import save
from common import nameCleaner

now = datetime.now()

articleLimit = 20

def urlParser(search, path, num_years):
    #find poge limit
    articles_count = 1
    pagecount = 0
    url = "http://search.199it.com:8001/?word="+search+"&page=1"
    headers = {
        'Host': 'search.199it.com:8001',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Origin': 'http://search.199it.com',
        'Referer': 'http://search.199it.com/?q=%E4%B8%AD%E8%8A%AF%E5%9B%BD%E9%99%85&page=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
    }
    res = requests.get(url, headers = headers)
    pages = int((res.json()[0]))


    #page scroll
    while(articles_count < articleLimit and int(pagecount) <= int(pages)):
        url = "http://search.199it.com:8001/?word="+search+"&page="+ str(pagecount)
        res = requests.get(url)
        # sum.write("搜索内容：" + search + "\n")
        # sum.write("date: "+ datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n" )
        # sum.write("\n")

        if(len(res.json()) > 1):
            resp = res.json()
            pages = resp[0]
            count = 0
            articles = []
            for i in range(1, len(resp)):
                if(count == 0):
                    articles.append(resp[i])
                if(count == 2):
                    count = 0
                else:
                    count+=1
            for obj in articles:
                url = str(obj)
                id = findId(url)
                textScrape(url, path, id, num_years)
                articles_count+=1
            pagecount += 1
    print('--------Finished downloading %d articles from 199it--------' % articles_count)

def textScrape(url, path, id, num_years):
    url = url
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    print('Processing article %s' % id)
    author = '199it'
    title = soup.find('h1', {"class": "entry-title"}).getText()
    title = nameCleaner(title)
    date = soup.find('time', {"class": "entry-date"}).getText()
    soup.find('div', {"id": "wp_rp_first"}).decompose()
    for s in soup(['script', 'style']):
        s.decompose()
    article = soup.find('div', {"class": "entry-content articlebody"})
    save(article, path, title, author, date, id, num_years)



def findId(inp):
    left = 0
    right = 0
    for i in range(15,len(inp)):
        if(inp[i].isdigit()):
            left = i
            break
    for i in range(len(inp),0,-1):
        if(inp[i-1].isdigit()):
            right = i
            break
    return inp[left:right]


def run(search_keyword, num_years):
    # search = input("Please enter your search:")
    print('--------Begin searching articles from 199it--------')
    os.chdir('../../')

    if 'news' not in os.listdir('cache'):
        os.mkdir('cache/news')
    if '199it' not in os.listdir('cache/news'):
        os.mkdir('cache/news/199it')
    path = 'cache/news/199it'

    if search_keyword not in os.listdir(path):
        os.mkdir(os.path.join(path, search_keyword))
    path = os.path.join(path, search_keyword)

    if not os.path.exists(path):
        os.makedirs(path)
    urlParser(search_keyword, path, num_years)

if __name__ == '__main__':
    run(search_keyword='中芯国际', num_years=2)
