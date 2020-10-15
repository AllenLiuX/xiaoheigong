import json
import time

import xpdf_python.wrapper as xpdf
import os
import pdfkit

from utils import bwlist
from definitions import ROOT_DIR, COMPANY_NAME_OCCUR
import pprint as pp


class Filter:
    def __init__(self):
        """
        A filter that processes data collected from the scrapers
        either pdf -> text for pdf files
        or html -> pdf -> text for html files
        """
        self.tags = {'历史沿革': ({'历史沿革', '历史事件', '发展历程'}, 3),
                     '组织架构': ({'组织架构'}, 3),
                     '股权架构': ({'股权架构', '股权变动', '股权结构', '股东', '股权'}, 3),
                     '管理团队': ({'管理团队', '董事会', '管理人'}, 3),
                     '薪酬体系': ({'薪酬体系'}, 3),
                     '奖励机制': ({'奖励机制'}, 3),
                     '产品': ({'业务', '服务', '产品'}, 3),
                     '生产情况': ({'生产情况', '生产流程', '生产工艺', '产能'}, 3),
                     '销售情况': ({'销售', '市场需求', '渠道'}, 3),
                     '知识产权': ({'知识产权', '商标', '专利'}, 3),
                     '核心技术': ({'核心技术', '核心竞争力', '壁垒'}, 3),
                     '研发事项': ({'研发', '迭代'}, 3),
                     '客户': ({'客户', '用户', '合作', '伙伴'}, 3),
                     '市场需求': ({'市场需求'}, 3),
                     '竞争对象': ({'对手', '竞争格局', '竞争态势', '头部', '竞品'}, 3),
                     '供应商': ({'供应', '采购'}, 3),
                     '市场占有率': ({'市场占有率', '市场份额', '市场竞争力'}, 3),
                     '运营情况': ({'收入', '营收', '成本', '债务'}, 3),
                     '商业模式': ({'商业模式', '经营模式', '理念', '业务模型', '盈利模式', '增长点', '商业布局'}, 3),
                     '发展战略': ({'战略', '发展目标', '策略', '规划', '未来', '投资', '融资'}, 3)
                     }
        self.keyword_list = {'历史沿革': '历史沿革', '历史事件': '历史沿革', '发展历程': '历史沿革',
                             '组织架构': '组织架构',
                             '股权架构': '股权架构', '股权变动': '股权架构', '股权结构': '股权架构', '股东': '股权架构', '股权': '股权架构',
                             '管理团队': '管理团队', '董事会': '管理团队', '管理人': '管理团队',
                             '薪酬体系': '薪酬体系',
                             '奖励机制': '奖励机制',
                             '业务': '产品', '服务': '产品', '产品': '产品',
                             '生产情况': '生产情况', '生产流程': '生产情况', '生产工艺': '生产情况', '产能': '生产情况',
                             '销售': '销售情况', '市场需求': '销售情况', '渠道': '销售情况',
                             '知识产权': '知识产权', '商标': '知识产权', '专利': '知识产权',
                             '核心技术': '核心技术', '核心竞争力': '核心技术', '壁垒': '壁垒',
                             '研发': '研发事项', '迭代': '研发事项',
                             '客户': '客户', '用户': '客户', '合作': '客户', '伙伴': '客户',
                             '对手': '竞争对象', '竞争格局': '竞争对象', '竞争态势': '竞争对象', '头部': '竞争对象', '竞品': '竞争对象',
                             '供应': '供应商', '采购': '供应商',
                             '市场占有率': '市场占有率', '市场份额': '市场占有率', '市场竞争力': '市场占有率',
                             '收入': '运营情况', '营收': '运营情况', '成本': '运营情况', '债务': '运营情况',
                             '商业模式': '商业模式', '经营模式': '商业模式', '理念': '商业模式', '业务模型': '商业模式', '盈利模式': '商业模式',
                             '增长点': '商业模式', '商业布局': '商业模式',
                             '战略': '发展战略', '发展目标': '发展战略', '策略': '发展战略', '规划': '发展战略', '未来': '发展战略', '投资': '发展战略',
                             '融资': '发展战略'
                             }
        self.blacklist = None
        self.whitelist = None
        self.summary = {}

    def count_keywords(self, text: str) -> dict:
        """
        Count the number of occurrences of each keyword in self.keyword_list in text
        :param text: string version of pdf
        :return: a {keyword:count} dictionary
        """
        counter = {}

        for keyword in self.keyword_list:
            count = text.count(keyword)
            counter.update({keyword: count})

        return counter

    def count_tags(self, keyword_counter: dict) -> dict:
        """
        Helper method that counts the number of for a pdf
        :param keyword_counter: dict that stores the occurrence of each keyword in the text
        :return: a dict that stores the tags that a pdf owns
        """
        counter = {}

        for tag in self.tags:
            count = sum([keyword_counter[keyword] for keyword in self.tags[tag][0]])
            if count >= self.tags[tag][1]:
                counter.update({tag: count})

        return counter

    def pdf_to_text(self, pdf_path) -> str:
        """
        Converts pdf to text by calling xpdf library
        :param pdf_path: path to pdf
        :return: the pdf text as string
        """
        text = xpdf.to_text(pdf_path)
        return text

    def html_to_pdf(self, directory):
        """
        Data processing for data collected from websites that do now allow pdf download
        :param directory: the directory that contains the .html and .json files
        """
        curr_dir = os.getcwd()
        os.chdir(directory)

        for filename in os.listdir(os.curdir):
            if filename.endswith('.html'):
                doc_id = filename[0:len(filename) - 5]
                pdf_filename = doc_id + '.pdf'

                # Converting to PDF
                options = {
                    'quiet': '',
                    'page-size': 'Letter',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None
                }
                try:
                    pdfkit.from_file(filename, pdf_filename, options=options)
                except:
                    continue
                # Removing html files
                os.remove(filename)
        os.chdir(curr_dir)

    def pdf_process(self, directory, search_keyword):
        """
        Data processing for data collected from websites that allow pdf download
        :param directory: the directory that contains the .pdf and .json files
        """
        curr_dir = os.getcwd()
        os.chdir(directory)
        company_name_threshold = COMPANY_NAME_OCCUR
        self.blacklist = bwlist.BWList(search_keyword, 'black')
        self.whitelist = bwlist.BWList(search_keyword, 'white')

        for filename in os.listdir(os.curdir):
            if filename.endswith('.pdf'):
                doc_id = filename[0:len(filename) - 4]
                json_filename = doc_id + '.json'
                source = json.load(open(json_filename, 'r', encoding='utf-8'))['source']
                print('Processing file with id %s' % doc_id)

                try:
                    # Getting text from pdf
                    text = self.pdf_to_text(filename)[0]
                    word_count = len(text.strip('\n'))

                    # Add company name to keyword
                    self.keyword_list.update({search_keyword: '搜索关键词'})

                    # Adding attributes to txt
                    keywords_count = self.count_keywords(text)

                    # Company name count
                    if keywords_count[search_keyword] <= company_name_threshold:
                        print('File %s deleted due to not enough keyword occurrences' % doc_id)
                        raise ValueError

                    # Adding tags to txt
                    tags_count = self.count_tags(keywords_count)

                    with open(json_filename, 'r', encoding='utf-8') as file:
                        attributes = json.load(file)

                        # Already been processed
                        if 'content' in attributes.keys() and 'keywordCount' in attributes.keys():
                            continue

                        # Update json file
                        attributes.update({'content': text,
                                           'wordCount': word_count,
                                           'keywordCount': keywords_count,
                                           'tags': tags_count,
                                           'filtered': 1})
                        file.close()

                    with open(doc_id + '.json', 'w', encoding='utf-8') as file:
                        json.dump(attributes, file, ensure_ascii=False, indent=4)
                        file.close()

                    # Save downloaded id to whitelist
                    self.whitelist.add_to_bwlist(source, doc_id)
                except (ValueError, SyntaxError, FileNotFoundError):
                    print('--------%s put to blacklist--------' % doc_id)
                    # Save problematic id to blacklist
                    self.blacklist.add_to_bwlist(source, doc_id)

                    # Remove problematic files
                    if os.path.exists(json_filename):
                        os.remove(json_filename)
                    if os.path.exists(filename):
                        os.remove(filename)
                    if os.path.exists(doc_id + '.txt'):
                        os.remove(doc_id + '.txt')
                    continue

        # Saving blacklist and whitelist
        self.whitelist.save_bwlist()
        self.blacklist.save_bwlist()

        if os.path.exists('summary.json'):
            self.add_summary(search_keyword)
        os.chdir(curr_dir)

    def add_summary(self, search_keyword):
        """
        For EACH website, add all json files from local summary (just for that website) to universal summary
        :param search_keyword: search keyword
        """
        # Loading local summary
        source_summary = json.load(open('summary.json', 'r', encoding='utf-8'))

        # Removing unnecessary attribute
        if 'search_keyword' in source_summary.keys():
            source_summary.pop('search_keyword')

        source_name = source_summary['source']                              # '36kr'

        # Removing blacklisted ids from local summary
        for doc in source_summary['data'].copy():
            if source_name in self.blacklist.list.keys() and doc['doc_id'] in self.blacklist.list[source_name]:
                source_summary['data'].remove(doc)

        # if source_name in self.blacklist.list.keys():
        #     for source_id in self.blacklist.list[source_name]:
        #         if source_id in source_summary['data'].keys():
        #             source_summary['data'].pop(source_id)

        # Update to overall summary
        if search_keyword not in self.summary.keys():
            self.summary.update({search_keyword: {source_name: source_summary.copy()}})
        elif 'data' in source_summary.keys():
            updated = self.summary[search_keyword]
            updated.update({source_name: source_summary.copy()})
            self.summary.update({search_keyword: updated})

        # Saving local summary
        json.dump(source_summary, open('summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

    def save_summary(self, search_keyword):
        """
        Save the summary for EACH KEYWORD
        :param search_keyword: search keyword
        """
        save_path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'summary.json')
        if self.summary[search_keyword]:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.summary, f, ensure_ascii=False, indent=4)

    def run_filter(self, file_type: str):
        """
        For news: html --> pdf --> process pdf --> update json
        For reports: pdf --> process pdf --> update json
        :param file_type: can either be 'news' or 'report'
        """
        os.chdir(ROOT_DIR)

        for keyword_name in os.listdir('cache'):
            # keyword_name: 中芯国际/可口可乐……
            if not os.path.isdir(os.path.join('cache', keyword_name)):
                continue
            for source_name in os.listdir(os.path.join('cache', keyword_name, file_type)):
                # source_name: 发现报告/萝卜投研……
                curr_dir = os.path.join('cache', keyword_name, file_type, source_name)

                # path does not exist
                if not os.path.isdir(curr_dir):
                    continue

                print('======== Processing files from %s ========' % source_name)

                # Convert html files to pdf first for news sources
                if file_type == 'news':
                    self.html_to_pdf(curr_dir)

                # Process all pdf files
                self.pdf_process(curr_dir, keyword_name)
            self.save_summary(keyword_name)


def run_both_filters():
    """
    Runs both news filter and reports filter. News filter converts html to pdf, Report filter doesn't.
    """
    start_time = time.time()
    file_filter = Filter()
    file_filter.run_filter(file_type='news')
    file_filter.run_filter(file_type='report')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    run_both_filters()

