from oss import mongodb as mg
import pprint as pp
import os
import json
from definitions import ROOT_DIR
from utils.errors import updateError


def get_db_results(search_keyword, pdf_min_page, min_word_count, num_years):
    pdf_min_page = int(pdf_min_page) if int(pdf_min_page) > 0 else 0
    min_word_count = int(min_word_count) if int(min_word_count) > 0 else 0

    try:
        existing_pdfs = mg.search_datas(search_keyword=search_keyword, pdf_min_page=int(pdf_min_page),
                                        min_word_count=int(min_word_count),
                                        num_years=num_years, db='articles')
    except:
        updateError('Database Error: Error occurred when getting database results for %s.' % search_keyword)
        pass

    for pdf in existing_pdfs:
        pdf.pop('_id')
        pdf.pop('content')
        pdf.pop('keywordCount')
        pdf.pop('filtered')
        pdf.pop('wordCount')

    result = {'db_search_results': existing_pdfs}
    
    if not os.path.exists(os.path.join(ROOT_DIR, 'cache', search_keyword)):
        os.mkdir(os.path.join(ROOT_DIR, 'cache', search_keyword))

    with open(os.path.join(ROOT_DIR, 'cache', search_keyword, 'all_search_results.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result

def get_db_results_new(search_keyword, pdf_min_page, min_word_count, num_years):
    pdf_min_page = int(pdf_min_page) if int(pdf_min_page) > 0 else 0
    min_word_count = int(min_word_count) if int(min_word_count) > 0 else 0

    try:
        existing_pdfs = mg.show_datas(collection='articles', query={'search_keyword': search_keyword, 'filtered': 1})
    except:
        updateError('Database Error: Error occurred when getting database results for %s.' % search_keyword)

    for pdf in existing_pdfs:
        pdf.pop('_id')
        pdf.pop('content')
        pdf.pop('keywordCount')
        pdf.pop('filtered')
        pdf.pop('wordCount')

    filtered_pdfs = []
    for pdf in existing_pdfs:
        if 'page_num' in pdf and pdf['page_num'] > pdf_min_page:
            filter_pdfs.append(pdf)

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

if __name__ == '__main__':
    pp.pprint(get_db_results_new('恒大', '150', '3000', 5))
