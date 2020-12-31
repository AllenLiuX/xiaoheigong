from selenium import webdriver
import requests
from lxml import etree
import time
import re
import os
import config
import public_fun


class SouGou:

    def __init__(self, search_word, s_date, max_art, max_text=3000):
        self.search_word = search_word
        self.s_date = public_fun.reduce_date(s_date)
        self.max_art = max_art
        self.max_text = max_text
        self.index_url = 'https://weixin.sogou.com/'
        self.driver = self.creat_driver()
        self.path = os.path.join(config.SAVE_PATH, search_word, 'news', 'sougou')
        self.result = []
        self.main()
        self.driver.close()

    def creat_driver(self):
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.add_argument('--headless')
        driver = webdriver.Chrome()
        driver.get(self.index_url)
        driver.find_element_by_xpath('//*[@id="query"]').send_keys(self.search_word)
        driver.find_element_by_xpath('//*[@id="searchForm"]/div/input[3]').click()
        return driver

    def get_url_list(self):
        labels = self.driver.find_elements_by_xpath('//h3/a[@target="_blank"]')
        dates = self.driver.find_elements_by_xpath('//span[@class="s2"]')
        one_page_url = []
        for n in range(len(labels)):
            if public_fun.calc_date(s_date=self.s_date, e_date=dates[n].text):
                one_page_url.append(labels[n].get_attribute('href'))
        try:
            self.next_page = self.driver.find_element_by_xpath('//*[@id="sogou_next"]').get_attribute('href')
        except:
            self.next_page = None
        self.result += one_page_url
        if one_page_url and len(self.result) < self.max_art:
            if config.DEBUG:
                self.result = self.result[:2]
            else:
                self.get_url_list()

    def get_content(self, url):
        self.driver.get(url)
        time.sleep(1)
        doc_id = re.findall('url=([^&]*)', string=url)[0].replace('..', '')  # 取后十个英文
        text = ''.join(self.driver.find_element_by_xpath('//*[@id="img-content"]').get_attribute('textContent').split())
        if len(text) > self.max_text:
            # ===========================html==========================
            html = [self.driver.execute_script("return document.documentElement.outerHTML")]
            # ===========================json==========================
            json_result = {'source': 'sougou', 'doc_id': '', 'date': '', 'download_url': url, 'org_name': '',
                           'page_num': '1', 'doc_type': 'NEW', 'title': ''}
            json_result['doc_id'] = doc_id
            try:
                json_result['date'] = ''.join(
                    self.driver.find_element_by_xpath('//em[@id="publish_time"]').text.split())
                json_result['org_name'] = ''.join(self.driver.find_element_by_xpath('//a[@id="js_name"]').text.split())
                json_result['title'] = ''.join(
                    self.driver.find_element_by_xpath('//*[@id="activity-name"]').text.split())
            except:
                pass
            public_fun.write_down_html(path=self.path, filename=doc_id[-10:] + '.html', text=html)
            public_fun.write_down_json(path=self.path, filename=doc_id[-10:] + '.json', text=json_result)
        else:
            print(url)
            print('文章字数不足', self.max_text)

    def main(self):
        self.get_url_list()
        self.result = self.result[:3] if config.DEBUG else self.result
        [self.get_content(url=url) for url in self.result]


if __name__ == '__main__':
    p1 = '人工智能'   # 搜索关键词
    p2 = 3  # 最早时间
    p3 = 10  # 文章数
    p4 = 1000  # 文字数量
    sou_gou = SouGou(search_word=p1, s_date=p2, max_art=p3, max_text=p4)
