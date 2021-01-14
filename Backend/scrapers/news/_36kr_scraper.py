# -*- coding: utf-8 -*-
import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import Backend.storage.mongodb as mg
from definitions import ROOT_DIR
from utils import bwlist
from utils.errors import NoDocError, updateError

now = datetime.now()


def clean_html(text):
    clean_re = re.compile('<.*?>')
    clean_text = re.sub(clean_re, '', text)
    return clean_text


class _36KR:
    def __init__(self):
        self.s = requests.Session()
        self.blacklist = None
        self.whitelist = set()
        self.source = '36kr'
        self.summary = {}

    def get_pdf_urls(self, search_keyword, min_word_count, path, num_years, get_pdf: bool):
        url = "https://36kr.com/search/articles/" + search_keyword + "?sort=score"

        res = requests.get(url)  # init page
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        articles = soup.find('ul',
                             {"class": "kr-search-result-list-main clearfloat"})  # find class that contains search results

        articles_count = 0

        self.summary.update({'source': '36kr'})
        self.summary.update({'has_pdf': 'html'})
        self.summary.update({'search_keyword': search_keyword})
        self.summary.update({'search_time': str(datetime.now().date())})
        self.summary.update({'data': []})

        if articles:
            for a in articles.find_all('a', {"class": "article-item-title weight-bold"},
                                       href=True):  # find all a links with href within class
                valid = self.download_articles(search_keyword, "https://36kr.com" + a['href'], path, num_years,
                                               get_pdf)
                if valid:
                    articles_count += 1

        # Save summary
        summary_save_path = os.path.join(path, 'summary.json')

        with open(summary_save_path, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, ensure_ascii=False, indent=4)

        if not articles:
            raise NoDocError('No documents found')

        print('--------Finished downloading %d articles from 36kr--------' % articles_count)

    def prefilter(self, date, num_years, search_keyword, doc_id):
        ret = True

        # Date processing
        dateToday = datetime.now().strftime("%Y")
        if date[0:3].isnumeric():
            years = int(dateToday) - int(date[0:4])
            if years > num_years:
                ret = False
        else:
            return False

        # Blacklist processing
        bl = bwlist.BWList(search_keyword, 'black')
        blacklist_exist = bl.bwlist_exist()

        if blacklist_exist and bl.in_bwlist(doc_id, '36kr'):
            ret = False

        # whitelist by database
        id_match_res = mg.show_datas('articles', query={'doc_id': str(doc_id),
                                                        'search_keyword': search_keyword})  # new whitelist --vincent
        if id_match_res:
            print('article #' + str(doc_id) + ' is already in database. Skipped.')
            ret = False

        date = datetime.strptime(date, '%Y-%m-%d')
        date = datetime(date.year, date.month, date.day)

        return ret

    def download_articles(self, search_keyword, url, path, num_years, get_pdf: bool):
        try:
            url = url
            res = requests.get(url)
            html_page = res.content
            soup = BeautifulSoup(html_page, 'html.parser')

            pattern = re.compile(r"(?<=\"articleDetailData\":{\"code\":0,\"data\":{\"itemId\":)[0-9]*")
            doc_id = re.search(pattern, str(soup)).group(0)

            pattern = re.compile(r"(?<=\"author\":\")(.*)(?=\",\"authorId)")
            author = re.search(pattern, str(soup)).group(0)

            title = soup.find('h1').getText()
            title = title.replace('|', '')
            date = soup.find('span', {"class": "title-icon-item item-time"}).getText()[3:]

            article = soup.find('div', {"class": "article-content"})
            article = clean_html(str(article))

            valid = self.prefilter(date, num_years, search_keyword, doc_id)

            if valid:
                print('Processing article %s' % doc_id)
                json_save_path = os.path.join(path, str(doc_id) + '.json')
                html_save_path = os.path.join(path, str(doc_id) + '.html')

                if get_pdf:
                    with open(html_save_path, "w", encoding='utf-8') as file:
                        file.write(article)

                # Saving doc attributes
                doc_info = {
                    'source': '36kr',
                    'doc_id': doc_id,
                    'title': title,
                    'date': date,
                    'org_name': author,
                    'oss_path': 'news/36kr/' + str(doc_id) + '.pdf',
                    'doc_type': 'NEWS',
                    'download_url': url,
                    'has_pdf': 'html',
                    'content': article,
                    'filtered': 0,  # -- new filter vincent
                    'search_keyword': search_keyword,
                }

                doc_info_copy = doc_info.copy()
                with open(json_save_path, 'w', encoding='utf-8') as f:
                    json.dump(doc_info, f, ensure_ascii=False, indent=4)

                self.summary['data'].append(doc_info_copy)

                # store doc_info to mongodb     --vincent
                # mg.insert_data(doc_info, 'articles')
                return valid
        except Exception as e:
            # updateError('Error occurred when scraping text from 36kr. \n' + str(e.__traceback__.tb_lineno) + ": " + str(e))
            updateError('Error occurred when scraping text from 36kr.')

        pass

    def run(self, search_keyword, min_word_count, num_years, get_pdf: bool):
        print('--------Begin searching articles from 36kr--------')

        try:
            os.chdir(ROOT_DIR)
            keyword_dir = os.path.join('cache', search_keyword)

            if search_keyword not in os.listdir('cache'):
                os.mkdir(keyword_dir)

            if 'html' not in os.listdir(keyword_dir):
                os.mkdir(os.path.join(keyword_dir, 'html'))

            if '36kr' not in os.listdir(os.path.join(keyword_dir, 'html')):
                os.mkdir(os.path.join(keyword_dir, 'html', '36kr'))

            current_path = os.path.join(keyword_dir, 'html', '36kr')

            self.get_pdf_urls(search_keyword, min_word_count, current_path, num_years, get_pdf)

        except NoDocError:
            print('--------No documents found in 36kr--------')
            pass


def run(search_keyword, min_word_count, num_years, get_pdf):
    _36kr = _36KR()
    _36kr.run(search_keyword=search_keyword, min_word_count=min_word_count, num_years=num_years, get_pdf=get_pdf)


if __name__ == '__main__':
    run(search_keyword='特斯拉', min_word_count='0', num_years=1, get_pdf=False)
