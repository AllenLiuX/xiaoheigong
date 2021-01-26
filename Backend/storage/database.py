import json
import os
import sys

from definitions import ROOT_DIR, translate, CUSTOM_KW_OCCUR
from Backend.storage import mongodb as mg
from Backend.storage.mongodb import insert_data
from utils.errors import updateError


def get_db_results(search_keyword: str, custom_keyword: str, pdf_min_page: str, min_word_count: str, num_years: int, tags):
    """
    Given search keyword, page limit, time limit, word limit, find the documents in the database
    :return: a dictionary {'db_search_results': [document objects]}
    """
    pdf_min_page = int(pdf_min_page) if int(pdf_min_page) > 0 else 0
    min_word_count = int(min_word_count) if int(min_word_count) > 0 else 0
    result = {}

    if tags and custom_keyword:
        updateError('Cannot have tags and custom keyword at the same time')
        return result

    if tags is None:
        tags = []

    try:
        existing_pdfs = mg.search_datas(search_keyword, pdf_min_page, min_word_count, num_years, tags)
        # existing_pdfs = mg.show_datas(collection='articles', query={'search_keyword': search_keyword, 'filtered': 1})
    except:
        updateError('Database Error: Error occurred when getting database results for %s.' % search_keyword)
        return result

    if custom_keyword:
        existing_pdfs = [pdf for pdf in existing_pdfs if pdf['content'].count(custom_keyword) >= CUSTOM_KW_OCCUR]

    for pdf in existing_pdfs:
        # removing unnecessary attributes from the copy sent to frontend
        pdf.pop('_id')
        pdf.pop('content')
        pdf.pop('oss_path')
        pdf.pop('keywordCount')
        pdf['tags'] = pdf.pop('tags')['list']
        pdf.pop('filtered')

    filtered_pdfs = []
    for pdf in existing_pdfs:
        if 'page_num' in pdf.keys() and pdf['page_num'] >= pdf_min_page:
            filtered_pdfs.append(pdf)
        if 'page_num' not in pdf.keys() and pdf['wordCount'] > min_word_count:
            filtered_pdfs.append(pdf)

    result = {'db_search_results': filtered_pdfs}
    return result


def pre_filter():
    try:
        existing_pdfs = mg.show_datas(collection='articles', query={'filtered': 0})
    except:
        updateError('Database Error: Error occurred when getting database results for filtered=0.')
    for pdf in existing_pdfs:
        pdf['filtered'] = 1
        mg.delete_datas(query={'source': pdf['source'], 'doc_id': pdf['doc_id']}, collection='articles')
        mg.insert_data(pdf, collection='articles')


def upload_to_db(search_keyword):
    """
    Given a search keyword, uploads all the json files within the keyword directory to database
    :param search_keyword: the search keyword
    :return: none
    """
    summary = os.path.join(ROOT_DIR, 'cache', search_keyword, 'summary.json')
    summary = json.load(open(summary))[search_keyword]

    for source_summary in summary.keys():
        source = summary[source_summary]
        source_name = source['source']  # e.g. '36kr'

        source_type = source['has_pdf']  # 'html' or 'pdf'
        data_dir = os.path.join(ROOT_DIR, 'cache', search_keyword, source_type, translate[source_name])

        for doc in source['data']:
            if not os.path.exists(data_dir):
                continue

            pdf_id = doc['doc_id']
            json_path = os.path.join(data_dir, str(pdf_id) + '.json')

            try:
                json_file = json.load(open(json_path))
            except FileNotFoundError:
                updateError('File not found error: Error occurred when uploading %s data to database' % source_name)
                continue

            try:
                insert_data(json_file, 'articles')
            except:
                updateError('Upload error: Error occurred when uploading %s data to database' % source_name)
                continue


if __name__ == '__main__':
    if len(sys.argv) > 1:
        keywords = sys.argv[1]
    else:
        keywords = '中芯国际'
    upload_to_db(keywords)
