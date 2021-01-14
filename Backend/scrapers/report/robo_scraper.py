import datetime
import json
import os

import requests
from fake_useragent import UserAgent

import Backend.storage.mongodb as mg
from definitions import ROOT_DIR
from definitions import tokens
from utils import bwlist
from utils.errors import NoDocError
from utils.errors import updateError
from utils.get_cookies import get_cookies

token = tokens['robo']


class ROBO:
    def __init__(self):
        sso = ''
        # Prevents the case where cookies does not contain cloud sso token; loops until we have sso
        while sso == '':
            cookies = get_cookies('https://robo.datayes.com')
            for cookie in cookies:
                if cookie['name'] == 'cloud-sso-token':
                    sso = cookie['value']
        try:
            self.s = requests.Session()
            sso = token
            self.cookie = 'cloud-sso-token=%s; ' % sso

            self.headers = {
                'accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, image/apng, */*; '
                          'q=0.8, application/signed-exchange; v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'cookie': self.cookie,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': str(UserAgent().random)
            }
        except Exception as e:
            updateError('Error occurred when sending request to Robo. \n' + str(e.__traceback__.tb_lineno) + ": " + str(e))
            pass
        self.source = 'robo'
        self.blacklist = None
        self.whitelist = set()
        self.summary = {'source': 'robo', 'has_pdf': 'pdf', 'search_keyword': '', 'search_time': '', 'data': []}

    def get_pdf_id(self, search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int) -> dict:
        # Adding blacklist
        self.blacklist = bwlist.BWList(search_keyword, 'black')
        blacklist_exist = self.blacklist.bwlist_exist()

        search_url = 'https://gw.datayes.com/rrp_adventure/web/search'
        headers = self.headers.copy()
        curr_year = datetime.datetime.today().year
        start_year = curr_year - num_years
        params = {
            'type': 'EXTERNAL_REPORT',
            'pageSize': 50,
            'pageNow': '1',
            'sortOrder': 'desc',
            'query': search_keyword,
            'pubTimeStart': str(start_year) + '0101',
            'pubTimeEnd': str(curr_year) + '1231',
            'minPageCount': pdf_min_num_page
        }

        # Updating summary before search
        self.summary.update({'search_keyword': search_keyword})
        self.summary.update({'search_time': str(datetime.datetime.now().date())})

        response = self.s.get(url=search_url, headers=headers, params=params).json()

        # Bad request
        if response['code'] != 1:
            raise NoDocError('No documents found')

        json_list = response['data']['list']

        id_list = {doc['data']['id']: doc for doc in json_list}

        # Filter Blacklist
        if blacklist_exist:
            id_list = self.blacklist.bwlist_filter(id_list, self.source)

        # Filter Whitelist
        for doc_id in id_list.copy():
            id_match_res = mg.show_datas('articles', query={'doc_id': str(doc_id), 'search_keyword': search_keyword})
            if id_match_res:
                print('article #' + str(doc_id) + ' is already in database. Skipped.')
                id_list.pop(doc_id)

        print('--------Found %d pdfs in 萝卜投研--------' % len(id_list))
        return id_list

    def update_json(self, id_list: dict, search_keyword: str):
        """
        Formats the doc_object into a standard format
        :param id_list: a dict of {doc_id: doc_object}
        :param search_keyword: the search keyword
        :return: an dict of {doc_id: doc_object} with more details in the object
        """
        download_api_url = f'https://gw.datayes.com/rrp_adventure/web/externalReport/'
        updated_json = {}

        for id in id_list:
            download_url = self.s.get(url=download_api_url + str(id), headers=self.headers).json()

            try:
                download_url = download_url['data']['downloadUrl']
            except Exception as e:
                updateError('Error occurred when getting response from Robo. \n' + str(e.__traceback__.tb_lineno) + ": " + str(e))
                continue

            date = id_list[id]['data']['publishTime']
            date = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10])).date()

            updated_dict = {'source': self.source,
                            'doc_id': str(id),
                            'date': str(date),
                            'org_name': id_list[id]['data']['orgName'],
                            'page_num': id_list[id]['data']['pageCount'],
                            'doc_type': id_list[id]['type'],
                            'download_url': download_url,
                            'has_pdf': 'pdf',
                            'oss_path': 'report/robo/' + str(id) + '.pdf',
                            'title': id_list[id]['data']['title'],
                            'filtered': 0,  # -- new filter vincent
                            'search_keyword': search_keyword,
                            }

            updated_json.update({id: updated_dict})
        return updated_json

    def download_pdf(self, search_keyword: str, doc_id_list: dict, get_pdf: bool):
        url_list = self.update_json(doc_id_list, search_keyword)
        pdf_count = 0

        os.chdir(ROOT_DIR)
        keyword_dir = os.path.join('cache', search_keyword)

        if search_keyword not in os.listdir('cache'):
            os.mkdir(keyword_dir)

        if 'pdf' not in os.listdir(keyword_dir):
            os.mkdir(os.path.join(keyword_dir, 'pdf'))

        if '萝卜投研' not in os.listdir(os.path.join(keyword_dir, 'pdf')):
            os.mkdir(os.path.join(keyword_dir, 'pdf', '萝卜投研'))

        current_path = os.path.join(keyword_dir, 'pdf', '萝卜投研')

        for pdf_id in url_list:
            pdf_save_path = os.path.join(current_path, str(pdf_id) + '.pdf')
            txt_save_path = os.path.join(current_path, str(pdf_id) + '.json')

            # get pdf only when get_pdf is true
            try:
                if get_pdf:
                    print('saving pdf with id: %s' % pdf_id)
                    content = self.s.get(url=url_list[pdf_id]['download_url'], headers=self.headers)
                    content.encoding = 'utf-8'
                    content = content.content

                    with open(pdf_save_path, 'wb') as f:
                        f.write(content)

                    # upload to oss
                    # oss_path = 'report/robo/' + str(pdf_id) + '.pdf'
                    # print('Uploading file to ali_oss at ' + OSS_PATH + oss_path)
                    # ossfile.upload_file(oss_path, pdf_save_path)

                doc_info = url_list[pdf_id]

                with open(txt_save_path, 'w', encoding='utf-8') as f:
                    json.dump(doc_info, f, ensure_ascii=False, indent=4)

                # store doc_info to mongodb --vincent
                # mg.insert_data(doc_info, 'articles')

                pdf_count += 1

                doc_info_copy = doc_info.copy()
                # doc_info_copy.pop('_id')
                self.summary['data'].append(doc_info_copy)
            except Exception as e:
                print(e)
                updateError('Error occurred when saving pdf %s from ROBO' % pdf_id)
                if os.path.exists(pdf_save_path):
                    os.remove(pdf_save_path)

                if os.path.exists(txt_save_path):
                    os.remove(txt_save_path)

                continue

        # Saving summary
        if self.summary:
            summary_save_path = os.path.join(current_path, 'summary.json')
            with open(summary_save_path, 'w', encoding='utf-8') as f:
                json.dump(self.summary, f, ensure_ascii=False, indent=4)

        print('--------Finished downloading %d pdfs from 萝卜投研--------' % pdf_count)

    def run(self, search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int, get_pdf: bool):
        print('--------Begin searching pdfs from 萝卜投研--------')
        try:
            pdf_id_list = self.get_pdf_id(search_keyword, filter_keyword, pdf_min_num_page, num_years)
        except NoDocError:
            updateError("No Doc Error: Empty response from ROBO. \n" + str(NoDocError.__traceback__.tb_lineno) + ": " + str(NoDocError))
            return

        try:
            self.download_pdf(search_keyword, pdf_id_list, get_pdf)
        except Exception as e:
            updateError("Download Error: Error occurred when downloading pdfs from ROBO. \n" + str(e.__traceback__.tb_lineno) + ": " + str(e))


def run(search_keyword: str, filter_keyword: str, pdf_min_num_page: str, num_years: int, get_pdf: bool):
    robo_scraper = ROBO()
    robo_scraper.run(search_keyword=search_keyword, filter_keyword=filter_keyword,
                     pdf_min_num_page=pdf_min_num_page,
                     num_years=num_years, get_pdf=get_pdf)


if __name__ == '__main__':
    run(search_keyword='中芯国际', filter_keyword='', pdf_min_num_page='20', num_years=1, get_pdf=False)
