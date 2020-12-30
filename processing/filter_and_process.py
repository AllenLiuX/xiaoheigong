import json
import os
import time

import xpdf_python.wrapper as xpdf
from definitions import ROOT_DIR, COMPANY_NAME_OCCUR
from utils import bwlist
from utils.errors import updateError


def pdf_to_text(pdf_path) -> str:
    """
    Converts pdf to text by calling xpdf library
    :param pdf_path: path to pdf
    :return: the pdf text as string
    """
    text = xpdf.to_text(pdf_path)
    return text


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

    def pdf_process(self, directory, search_keyword):
        """
        Data processing for data collected from websites that allow pdf download
        Convert pdf to text and store them in corresponding json files
        :param search_keyword: the search keyword
        :param directory: the directory that contains the .pdf and .json files
        """
        curr_dir = os.getcwd()
        os.chdir(directory)
        self.blacklist = bwlist.BWList(search_keyword, 'black')

        for filename in os.listdir(os.curdir):
            if filename.endswith('.pdf'):
                doc_id = filename[0:len(filename) - 4]
                json_filename = doc_id + '.json'

                try:
                    # Open json file
                    print('Processing file with id %s' % doc_id)
                except FileNotFoundError:
                    updateError('FILE NOT FOUND: %s. Skipped.' % json_filename)
                    if os.path.exists(json_filename):
                        os.remove(json_filename)
                    if os.path.exists(filename):
                        os.remove(filename)
                    if os.path.exists(doc_id + '.txt'):
                        os.remove(doc_id + '.txt')
                    continue

                try:
                    # Getting text from pdf
                    text = pdf_to_text(filename)[0]
                except FileNotFoundError:
                    updateError('FILE NOT FOUND: %s. Skipped.' % filename)
                    if os.path.exists(json_filename):
                        os.remove(json_filename)
                    if os.path.exists(filename):
                        os.remove(filename)
                    if os.path.exists(doc_id + '.txt'):
                        os.remove(doc_id + '.txt')
                    continue

                with open(json_filename, 'r', encoding='utf-8') as file:
                    # Update content to json
                    attributes = json.load(file)
                    file.close()

                with open(json_filename, 'w', encoding='utf-8') as file:
                    # Update content to json
                    attributes.update({'content': text})
                    json.dump(attributes, file, ensure_ascii=False, indent=4)
                    file.close()

        os.chdir(curr_dir)

    def filter_and_generate_tags(self, directory, search_keyword, has_pdf):
        print("======== Filtering and generating tags ========")
        curr_dir = os.getcwd()
        os.chdir(directory)
        company_name_threshold = COMPANY_NAME_OCCUR
        file_type = '.' + has_pdf  # '.html' or '.pdf'
        for filename in os.listdir(os.curdir):
            if filename.endswith(file_type):
                doc_id = filename[0:len(filename) - len(file_type)]
                json_filename = doc_id + '.json'

                print('generating tags for pdf with id %s' % doc_id)

                with open(json_filename, 'r', encoding='utf-8') as file:
                    # Update content to json
                    attributes = json.load(file)
                    text = attributes['content']
                    source = json.load(open(json_filename, 'r', encoding='utf-8'))['source']

                try:
                    word_count = len(text.strip('\n'))

                    # Add company name to keyword
                    self.keyword_list.update({search_keyword: '搜索关键词'})

                    # Adding attributes to txt
                    keywords_count = self.count_keywords(text)

                    # Company name count
                    if keywords_count[search_keyword] <= company_name_threshold:
                        raise ValueError

                    # Adding tags to txt
                    tags_count = self.count_tags(keywords_count)

                    with open(json_filename, 'r', encoding='utf-8') as file:
                        attributes = json.load(file)

                        # Already been processed
                        if 'keywordCount' in attributes.keys():
                            continue

                        # Update json file
                        attributes.update({'wordCount': word_count,
                                           'keywordCount': keywords_count,
                                           'tags': tags_count,
                                           'filtered': 1})
                        file.close()

                    with open(doc_id + '.json', 'w', encoding='utf-8') as file:
                        json.dump(attributes, file, ensure_ascii=False, indent=4)
                        file.close()

                except (ValueError, SyntaxError):
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

        # Saving blacklist
        self.blacklist.save_bwlist()

        if os.path.exists('summary.json'):
            self.add_summary(search_keyword)

        os.chdir(curr_dir)

    def add_summary(self, search_keyword):
        """
        For EACH website, add all json files from local summary (just for that website) to universal summary
        Called in filter_and_generate_tags()
        :param search_keyword: search keyword
        """
        try:
            # Loading local summary
            source_summary = json.load(open('summary.json', 'r', encoding='utf-8'))

            # Removing unnecessary attribute
            if 'search_keyword' in source_summary.keys():
                source_summary.pop('search_keyword')

            source_name = source_summary['source']  # '36kr'

            # Removing blacklisted ids from local summary
            for doc in source_summary['data'].copy():
                if source_name in self.blacklist.list.keys() and doc['doc_id'] in self.blacklist.list[source_name]:
                    source_summary['data'].remove(doc)

            # Update to overall summary
            if search_keyword not in self.summary.keys():
                self.summary.update({search_keyword: {source_name: source_summary.copy()}})
            elif 'data' in source_summary.keys():
                updated = self.summary[search_keyword]
                updated.update({source_name: source_summary.copy()})
                self.summary.update({search_keyword: updated})

            # Saving local summary
            json.dump(source_summary, open('summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
        except:
            updateError("Error occurred when writing summary for keyword: " + search_keyword)

    def save_summary(self, search_keyword):
        """
        Save the summary for EACH KEYWORD
        Called after filtering is done for all websites in self.run_filter()
        :param search_keyword: search keyword
        """
        try:
            save_path = os.path.join(ROOT_DIR, 'cache', search_keyword, 'summary.json')
#            print(self.summary)
            if self.summary[search_keyword]:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(self.summary, f, ensure_ascii=False, indent=4)
        except:
            updateError("Error occurred when saving summary for keyword: " + search_keyword)

    def run_filter(self, search_keyword: str, file_type: str):
        """
        For news: html --> text --> update json
        For reports: pdf --> process pdf --> update json
        :param search_keyword: search keyword
        :param file_type: can either be 'html' or 'has_pdf'
        """
        os.chdir(ROOT_DIR)

        if not os.path.isdir(os.path.join('cache', search_keyword)):        # cache/中芯国际 not exist
            os.makedirs(os.path.join('cache', search_keyword))

        if not os.path.isdir(os.path.join('cache', search_keyword, file_type)):     # cache/中芯国际/news 不存在
            os.makedirs(os.path.join('cache', search_keyword, file_type))

        for source_name in os.listdir(os.path.join('cache', search_keyword, file_type)):        # source_name: 发现报告/萝卜投研……
            print(source_name)
            curr_dir = os.path.join('cache', search_keyword, file_type, source_name)

            if not os.path.isdir(curr_dir):         # path does not exist
                os.makedirs(curr_dir)

            print('======== Processing files from %s ========' % source_name)

            # Process all pdf files
            self.pdf_process(curr_dir, search_keyword)
            self.filter_and_generate_tags(curr_dir, search_keyword, file_type)
        self.save_summary(search_keyword)


def run_filter(search_keyword):
    """
    Runs both news filter and reports filter. News filter converts html to pdf, Report filter doesn't.
    """
    start_time = time.time()
    file_filter = Filter()
    file_filter.run_filter(search_keyword=search_keyword, file_type='pdf')
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    run_filter(search_keyword='恒大')