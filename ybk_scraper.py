import json
import pprint as pp

import requests
from fake_useragent import UserAgent


class YBK:
    def __init__(self):
        """
        登录的时候需要提供一个用户token和一个用户id
        """
        self.s = requests.Session()
        self.X_date = 'Sun, 09 Aug 2020 17:27:32 GMT'
        self.signature = '"9zQpr9h8ZhgzRE0ginyMwyFmyJI="'
        self.user_agent = str(UserAgent().random)

        # Request Headers
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-encoding': 'gzip, deflate, br',
            'Accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Authorization': 'hmac id="AKIDdlutrcn7F4j62Fskwqbiqrki3q3j40r1vjjw", algorithm="hmac-sha1", headers="x-date", signature=%s' % self.signature,
            'Connection': 'keep-alive',
            'Origin': 'https://www.yanbaoke.com',
            'Referer': 'https://www.yanbaoke.com',
            'Sec-fetch-dest': 'empty',
            'Sec-fetch-mode': 'cors',
            'Sec-fetch-site': 'cross-site',
            'User-Agent': self.user_agent,
            'X-Date': self.X_date
        }

    def get_pdf_id(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-encoding': 'gzip, deflate, br',
            'Accept-language': 'en-US,en;q=0.9',
            'Authorization': 'hmac id="AKIDdlutrcn7F4j62Fskwqbiqrki3q3j40r1vjjw", algorithm="hmac-sha1", headers="x-date", signature=%s' % self.signature,
            'Origin': 'https://www.yanbaoke.com',
            'Referer': 'https://www.yanbaoke.com/info/n4SazXfGWeMJ7bDym5ZmVP',
            'Sec-fetch-dest': 'empty',
            'Sec-fetch-mode': 'cors',
            'Sec-fetch-site': 'cross-site',
            'User-Agent': self.user_agent,
            'X-Date': self.X_date
        }

        params = {
            'tags': '中芯国际',
            'title': '0',
            'skip': '0',
            'size': '20',
            'sort': 'desc'
        }

        search_url = 'https://api.quzili.cn/search'

        response = self.s.get(url=search_url, headers=self.headers, params=params).json()
        pp.pprint(response)
        files = response['hits']['hits']

        file = files[0]
        time = file['_source']['time']
        title = file['_source']['title']
        uuid = file['_source']['uuid']

        pdf_url = 'https://api.quzili.cn/user'


        payload = {
            'buy': '1',
            'deviceid': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36MacIntel",
            'fileid': "n4SazXfGWeMJ7bDym5ZmVP",
            'title': "电商行业：中国新一代工业品电商的趋势展望，产业协同，价值深耕_32页_1mb.pdf",
            'token': "1b71fd64d8e0302420910b855a8abd55f4cb2558",
            'uid': "AkTZkKnTzjYDNgttbx4R3a"
        }

        pdf_response = self.s.post(url=pdf_url, data=json.dumps(payload), headers=headers)
        # pdf_response.raise_for_status()
        # pdf_response.encoding = pdf_response.apparent_encoding
        print(pdf_response)

        download_url = 'https://files.quzili.cn/files/%E7%94%B5%E5%95%86%E8%A1%8C%E4%B8%9A%EF%BC%9A%E4%B8%AD%E5%9B%BD%E6%96%B0%E4%B8%80%E4%BB%A3%E5%B7%A5%E4%B8%9A%E5%93%81%E7%94%B5%E5%95%86%E7%9A%84%E8%B6%8B%E5%8A%BF%E5%B1%95%E6%9C%9B%EF%BC%8C%E4%BA%A7%E4%B8%9A%E5%8D%8F%E5%90%8C%EF%BC%8C%E4%BB%B7%E5%80%BC%E6%B7%B1%E8%80%95_32%E9%A1%B5_1mb.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=B3XAEB56S9IDOX2UPEVC%2F20200809%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200809T171402Z&X-Amz-Expires=60&X-Amz-SignedHeaders=host&X-Amz-Signature=ac5bfc8e241af41fbd21b20c2972bf79808609a1b6d91f65b07eb9b409f51437'

        params = {
            'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
            'X-Amz-Credential': 'B3XAEB56S9IDOX2UPEVC%2F20200809%2Fus-east-1%2Fs3%2Faws4_request',
            'X-Amz-Date': '20200809T172920Z',
            'X-Amz-Expires': '60',
            'X-Amz-SignedHeaders': 'host',
            'X-Amz-Signature': 'e997999a391e3bb8e92e9ba3a347b4a1d8f6a566b11ccff6894476d836c2be8b'
        }

        download_response = self.s.get(url=download_url, headers=headers, params=params)

        print(download_response)

        # try:
        #     pdf_response = requests.get(url=pdf_url, headers=headers, params=params, timeout=30)
        #     pdf_response.raise_for_status()
        #     pdf_response.encoding = pdf_response.apparent_encoding
        #     print(pdf_response)
        # except:
        #     print("something happened")


if __name__ == '__main__':
    ybk_scraper = YBK()
    ybk_scraper.get_pdf_id()
