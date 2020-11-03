import json
import os
import pprint as pp

from definitions import ROOT_DIR
from definitions import translate
from oss.mongodb import update_datas


def update_filtered(search_keyword):
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
        source_type = source['source_type']  # 'news'
        data_dir = os.path.join(ROOT_DIR, 'cache', search_keyword, source_type, translate[source_name])

        for doc in source['data']:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            pdf_id = doc['doc_id']
            json_path = os.path.join(data_dir, str(pdf_id) + '.json')
            json_file = json.load(open(json_path))

            update_datas({'doc_id': str(pdf_id)}, {'$set': json_file}, source_name)


def transfer(search_keyword):
    """
    Collects all the data from current search and from database, and return a list of results to the frontend
    :param search_keyword: current search keyword
    :return: a tuple of a list of results, and the length of the list
    """
    all_results = []
    summary = os.path.join(ROOT_DIR, 'cache', search_keyword, 'summary.json')
    summary = json.load(open(summary, 'r', encoding='utf-8'))[search_keyword]

    for source in summary.keys():
        all_results += summary[source]['data']

    db_search_results = os.path.join(ROOT_DIR, 'cache', search_keyword, 'db_search_results.json')
    db_search_results = json.load(open(db_search_results, 'r', encoding='utf-8'))['db_search_results']

    all_results += db_search_results

    with open(os.path.join(ROOT_DIR, 'cache', search_keyword, 'all_search_results.json'), 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    return all_results, len(all_results)


if __name__ == '__main__':
    # update_filtered('中芯国际')
    pp.pprint(transfer("中芯国际"))
