# -*- coding: utf-8 -*-
import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pprint as pp

from definitions import ROOT_DIR
from utils import bwlist
from utils.errors import NoDocError

import oss.mongodb as mg
import oss.oss as ossfile

now = datetime.now()


class _36KR():
    def __init__(self):
        self.s = requests.Session()
        self.blacklist = None
        self.whitelist = set()
        self.source = '36kr'
        self.summary = {}

    def check_database(self, search_keyword: str, min_word_count: str, num_years: int):
        db_existing = mg.search_datas(search_keyword=search_keyword, pdf_min_page='', min_word_count=min_word_count,
                                      num_years=num_years)
        for file in db_existing:
            self.whitelist.add(file['_id'])

    def urlParser(self, search_keyword, min_word_count, path, num_years, get_pdf: bool):
        url = "https://36kr.com/search/articles/" + search_keyword + "?sort=score"

        res = requests.get(url)  # init page
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        articles = soup.find('ul',
                             {
                                 "class": "kr-search-result-list-main clearfloat"})  # find class that contains search results

        if not articles:
            raise NoDocError('No documents found')

        articles_count = 0

        self.summary.update({'source': '36kr'})
        self.summary.update({'source_type': 'news'})
        self.summary.update({'search_keyword': search_keyword})
        self.summary.update({'search_time': str(datetime.now().date())})
        self.summary.update({'data': []})

        # Generate db whitelist
        self.check_database(search_keyword=search_keyword, min_word_count=min_word_count, num_years=num_years)

        for a in articles.find_all('a', {"class": "article-item-title weight-bold"},
                                   href=True):  # find all a links with href within class
            valid = self.textScrape(search_keyword, "https://36kr.com" + a['href'], path, num_years,
                                    get_pdf)
            if valid:
                articles_count += 1

        # Save summary
        summary_save_path = os.path.join(path, 'summary.json')
        with open(summary_save_path, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, ensure_ascii=False, indent=4)

        print('--------Finished downloading %d articles from 36kr--------' % articles_count)

    def prefilter(self, date, num_years, search_keyword, doc_id):
        ret = True

        # Date processing
        dateToday = datetime.now().strftime("%Y")
        if date[0:3].isnumeric():
            years = int(dateToday) - int(date[0:4])
            if years > num_years:
                ret = False

        # Blacklist processing
        bl = bwlist.BWList(search_keyword, 'black')
        blacklist_exist = bl.bwlist_exist()

        if blacklist_exist and bl.in_bwlist(doc_id, '36kr'):
            ret = False

        # whitelist by database
        id_match_res = mg.show_datas('36kr', query={'doc_id': str(doc_id)})
        if id_match_res:
            print('article #' + str(doc_id) + ' is already in database. Skipped.')
            ret = False

        date = datetime.strptime(date, '%Y-%m-%d')
        date = datetime(date.year, date.month, date.day)

        return ret

    def textScrape(self, search_keyword, url, path, num_years, get_pdf: bool):
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

        valid = self.prefilter(date, num_years, search_keyword, doc_id)

        if valid:
            print('Processing article %s' % doc_id)
            json_save_path = os.path.join(path, str(doc_id) + '.json')
            html_save_path = os.path.join(path, str(doc_id) + '.html')
            pdf_save_path = os.path.join(path, str(doc_id) + '.pdf')

            if get_pdf:
                with open(html_save_path, "w", encoding='utf-8') as file:
                    file.write(str(article))

            # Saving doc attributes
            doc_info = {
                'source': '36kr',
                'doc_id': doc_id,
                'title': title,
                'date': date,
                'org_name': author,
                'oss_path': 'news/36kr/' + str(doc_id) + '.pdf',
                'doc_type': 'NEWS'
            }

            doc_info_copy = doc_info.copy()
            self.summary['data'].append(doc_info_copy)

            with open(json_save_path, 'w', encoding='utf-8') as f:
                json.dump(doc_info, f, ensure_ascii=False, indent=4)

            # store doc_info to mongodb
            mg.insert_data(doc_info, '36kr')

        return valid

    def run(self, search_keyword, min_word_count, num_years, get_pdf: bool):
        print('--------Begin searching articles from 36kr--------')

        try:
            os.chdir(ROOT_DIR)
            keyword_dir = os.path.join('cache', search_keyword)

            if search_keyword not in os.listdir('cache'):
                os.mkdir(keyword_dir)

            if 'news' not in os.listdir(keyword_dir):
                os.mkdir(os.path.join(keyword_dir, 'news'))

            if '36kr' not in os.listdir(os.path.join(keyword_dir, 'news')):
                os.mkdir(os.path.join(keyword_dir, 'news', '36kr'))

            current_path = os.path.join(keyword_dir, 'news', '36kr')

            if os.path.exists(current_path + "summary.txt"):
                sum = open(os.path.join(current_path, "summary" + ".json"), "a", encoding='utf-8')
            else:
                sum = open(os.path.join(current_path, "summary" + ".json"), "w", encoding='utf-8')

            self.urlParser(search_keyword, min_word_count, current_path, num_years, get_pdf)

        except NoDocError:
            print('--------No documents found in 36kr--------')
            pass


def run(search_keyword, min_word_count, num_years, get_pdf):
    _36kr = _36KR()
    _36kr.run(search_keyword=search_keyword, min_word_count=min_word_count, num_years=num_years, get_pdf=get_pdf)


if __name__ == '__main__':
    run(search_keyword='可口可乐', min_word_count='3000', num_years=1, get_pdf=True)
