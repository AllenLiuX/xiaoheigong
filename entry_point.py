import Backend
import Backend.processing.filter_and_process as filter
from Backend.storage import database
from Backend.scrapers import run_scrapers
import sys
import shutil
import os
import pprint as pp
from definitions import CATEGORY_TO_TAG


def search_db(search_keyword: str, min_words: str, pdf_min_num_page: str, num_years: int, tags=None):
    return database.get_db_results(search_keyword, pdf_min_num_page, min_words, num_years, tags)


def get_all_tags():
    return CATEGORY_TO_TAG


def scrape(search_keyword, filter_keyword, min_words, pdf_min_num_page, num_years):
    """
    This function does the following:
    1. run_all():
        Run all the scrapers being activated in in run_scrapers, and store all the json files in /cache
    2. run_filter():
        Process text and generate tags
    3. upload_to_db():
        Add to database
    4. Clear cache
    """
    if not os.path.isdir('cache'):
        os.mkdir('cache')
    run_scrapers.run_all(search_keyword=search_keyword, filter_keyword=filter_keyword, min_words=min_words,
                         pdf_min_num_page=pdf_min_num_page, num_years=num_years)
    filter.run_filter(search_keyword=search_keyword)
    Backend.storage.database.upload_to_db(search_keyword=search_keyword)
    shutil.rmtree('cache')


if __name__ == '__main__':
    # pp.pprint(
    #     search_db(search_keyword='中芯国际', min_words='3000', pdf_min_num_page='150', num_years=1))
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = '中芯国际'
    scrape(search_keyword=keyword, filter_keyword='', min_words='500', pdf_min_num_page='20', num_years=1)
    # pp.pprint(search_db(search_keyword=keyword, min_words='500', pdf_min_num_page='20', num_years=1))
    # pp.pprint(get_all_tags())
