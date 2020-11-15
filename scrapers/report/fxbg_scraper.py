import datetime
import json
import os
from typing import Optional

import requests
from fake_useragent import UserAgent

import oss.mongodb as mg
from definitions import ROOT_DIR
from utils import bwlist
from utils.errors import DownloadError
from utils.errors import NoDocError
from utils.errors import updateError


token = '6PwWhSrcWZdMGiqNAPZHzZj2UHM2S5lVsqGbncDZN9grbufTWP1NF8BXjpbVTI60'

class FXBG:
    def __init__(self, user_token: str, user_id: str):
        """
        登录的时候需要提供一个用户token和一个用户id
        :param user_token: 用户密钥
        :param user_id: 用户ID
        """
        self.s = requests.Session()
        self.user_token = user_token
        self.user_id = str(user_id)
        self.blacklist = None
        self.whitelist = set()
        self.source = 'fxbg'
        self.summary = {'source': 'fxbg', 'has_pdf': 'pdf', 'search_keyword': '', 'search_time': '', 'data': []}

        # Request Headers
        self.headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'origin': 'https://www.fxbaogao.com',
            'pragma': 'no-cache',
            'referer': 'https://www.fxbaogao.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': str(UserAgent().random)
        }

    def check_database(self, search_keyword: str, pdf_min_num_page: str, num_years: int):
        db_existing = mg.search_datas(search_keyword=search_keyword, pdf_min_page=pdf_min_num_page, min_word_count='',
                                      num_years=num_years)
        for file in db_existing:
            self.whitelist.add(file['_id'])

    def get_pdf_id(self, search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int) -> dict:
        """
        根据搜索结果及搜索条件获取所有符合条件pdf的id
        :param search_keyword: 标题需要包含的关键词（公司名）
        :param filter_keyword: 标题不能包含的关键词
        :param pdf_min_num_page: 最少页数限制
        :param num_years: 筛选时间范围
        :return: id_list: 所有符合条件的pdf文件的id的列表
        """

        # This is the url for the redirected API
        current_year = datetime.date.today().year
        years = [year for year in range(current_year - num_years + 1, current_year + 1)]

        # Adding blacklist
        self.blacklist = bwlist.BWList(search_keyword, 'black')
        blacklist_exist = self.blacklist.bwlist_exist()

        search_url = 'https://api.mofoun.com/mofoun/search/report/search'
        payload = {
            'advancedQuery': 'true',
            'advancedRequest': {
                'title': search_keyword,
                'titleMustNot': filter_keyword
            },
            'keywords': search_keyword,
            'order': '2',
            'pageSize': '1000',
            'paragraphSize': '4',
            'pdfPage': pdf_min_num_page,
            'years': years
        }
        headers = self.headers.copy()
        headers.update({
            'user-token': self.user_token,
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Id': self.user_id,
            'VERSION': '1.0.0',
        })

        # Update summary before searching
        self.summary.update({'search_keyword': search_keyword})
        self.summary.update({'search_time': str(datetime.datetime.now())})

        response = self.s.post(url=search_url, data=json.dumps(payload), headers=headers)

        if response.status_code != 200:
            raise NoDocError('Bad response')

        response = response.json()

        id_list = []
        if not response['data']:
            raise NoDocError('Bad response')

        id_list = {doc['docId']: doc for doc in response['data']['dataList']}

        # Checking blacklist
        if blacklist_exist:
            id_list = self.blacklist.bwlist_filter(id_list, self.source)

        # Checking whitelist
        # self.check_database(search_keyword=search_keyword, pdf_min_num_page=pdf_min_num_page, num_years=num_years)
        for doc_id in id_list.copy():
            id_match_res = mg.show_datas('fxbg', query={'doc_id': doc_id})
            if doc_id in self.whitelist or id_match_res:
                print('article #' + str(doc_id) + ' is already in database. Skipped.')
                id_list.pop(doc_id)

        return id_list

    def get_pdf_url(self, doc_list: dict, doc_type: Optional[str] = '2') -> dict:
        """
        根据文档的id和类型选择获取pdf下载链接，该链接为在线查看pdf文档的链接
        :param doc_list: a list of 所有文档的id
        :param doc_type: 文档的类型，默认为2(pdf)
        :return: url_list: 所有所需要下载的pdf文件的下载链接， 形式为{pdf_id: pdf_url}
        """

        download_api_url = f'https://api.mofoun.com/mofoun/file/pdf/url'
        for doc_id in doc_list:
            params = {
                'docId': doc_id,
                'docType': doc_type
            }
            headers = self.headers.copy()
            headers.update({
                'user-token': self.user_token,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Id': self.user_id,
                'VERSION': '110100',
            })
            response = self.s.get(url=download_api_url, headers=headers, params=params).json()
            # pp.pprint(response)
            # time_interval = random.randint(5, 8)
            # time.sleep(time_interval)
            doc = doc_list[doc_id]
            title = str(doc['title']).replace('<em>', '').replace('</em>', '')
            date = doc['pdfPath'][7:17]

            updated_doc = {'source': self.source,
                           'doc_id': doc_id,
                           'date': str(datetime.datetime.strptime(date, '%Y/%m/%d').date()),
                           'download_url': 'https://oss-buy.hufangde.com' + response['data'],
                           'org_name': doc['orgName'].replace('<em>', '').replace('</em>', ''),
                           'page_num': doc['pageNum'],
                           'doc_type': 'EXTERNAL_REPORT',
                           'has_pdf': "pdf",
                           'oss_path': 'report/fxbg/' + str(doc_id) + '.pdf',
                           'title': title}

            doc_list.update({doc_id: updated_doc})

        print('--------Found %s pdfs in 发现报告--------' % len(doc_list))
        return doc_list

    def download_pdf(self, search_keyword: str, url_list: dict, get_pdf: bool):
        """
        通过提供的pdf下载url下载所有pdf至新建文件夹
        下载文件路径: 根目录/cache/[关键词]/has_pdf/发现报告/
        :param search_keyword: 标题需要包含的关键词（公司名）
        :param url_list: 所有所需要下载的pdf文件的下载链接
        """
        os.chdir(ROOT_DIR)
        keyword_dir = os.path.join('cache', search_keyword)

        if search_keyword not in os.listdir('cache'):
            os.mkdir(keyword_dir)

        if 'pdf' not in os.listdir(keyword_dir):
            os.mkdir(os.path.join(keyword_dir, 'pdf'))

        if '发现报告' not in os.listdir(os.path.join(keyword_dir, 'pdf')):
            os.mkdir(os.path.join(keyword_dir, 'pdf', '发现报告'))

        current_path = os.path.join(keyword_dir, 'pdf', '发现报告')

        pdf_count = 0

        for pdf_id in url_list:
            id_match_res = mg.show_datas('fxbg', query={'doc_id': pdf_id})
            if id_match_res:
                print('article #' + str(pdf_id) + ' is already in database. Skipped.')
                continue

            pdf_save_path = os.path.join(current_path, str(pdf_id) + '.pdf')

            if get_pdf:
                content = self.s.get(url=url_list[pdf_id]['download_url'], headers=self.headers)
                content.encoding = 'utf-8'

                content = content.content

                print('saving pdf with id: %s' % pdf_id)
                print('the source url is: ' + url_list[pdf_id]['download_url'])

                with open(pdf_save_path, 'wb') as f:
                    f.write(content)

                # upload to oss
                # oss_path = 'report/fxbg/' + str(pdf_id) + '.pdf'
                # print('Uploading file to ali_oss at ' + OSS_PATH + oss_path)
                # print(oss_path)
                # ossfile.upload_file(oss_path, pdf_save_path)

            doc_info = url_list[pdf_id]
            txt_save_path = os.path.join(current_path, str(pdf_id) + '.json')

            with open(txt_save_path, 'w', encoding='utf-8') as f:
                json.dump(doc_info, f, ensure_ascii=False, indent=4)

            # store doc_info to mongodb
            mg.insert_data(doc_info, 'articles')

            pdf_count += 1

            # Saving into summary
            doc_info_copy = doc_info.copy()
            doc_info_copy.pop('_id')
            self.summary['data'].append(doc_info_copy)

        # Saving summary
        summary_save_path = os.path.join(current_path, 'summary.json')
        with open(summary_save_path, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, ensure_ascii=False, indent=4)

        print('--------Finished downloading %d pdfs from 发现报告--------' % pdf_count)

    def run_fxbg(self, search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int, get_pdf: bool):
        print('--------Begin searching pdfs from 发现报告--------')
        try:
            pdf_id_list = self.get_pdf_id(search_keyword, filter_keyword, pdf_min_num_page, num_years)
            pdf_url_list = self.get_pdf_url(pdf_id_list)
        except NoDocError:
            updateError("No Doc Error: Empty response from FXBG.")

        try:
            self.download_pdf(search_keyword, pdf_url_list, get_pdf)
        except:
            updateError("Download Error: Error occurred when downloading pdfs from fxbg.")


def run(search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int, get_pdf: bool):
    # User ID does not change for a fixed account
    # User Token changes for each individual login
    USER_ID = '43934'
    USER_TOKEN = token
    try:
        fxbg_scraper = FXBG(USER_TOKEN, USER_ID)
        fxbg_scraper.run_fxbg(search_keyword=search_keyword, filter_keyword=filter_keyword,
                              pdf_min_num_page=pdf_min_num_page, num_years=num_years, get_pdf=get_pdf)
    except NoDocError:
        print('--------No documents found in 发现报告--------')
    except DownloadError:
        print('')


if __name__ == '__main__':
    run(search_keyword='中芯国际', filter_keyword='', pdf_min_num_page='10', num_years=5, get_pdf=True)
