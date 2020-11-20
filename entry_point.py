import processing.filter as filter
import processing.run_database as run_database
import processing.upload as upload
import scrapers.run_scrapers as run_scrapers


def run_all(search_keyword, filter_keyword, min_words, pdf_min_num_page, num_years):
    run_database.get_db_results(search_keyword=search_keyword, pdf_min_page=pdf_min_num_page, min_word_count=min_words,
                                num_years=num_years)
    run_scrapers.run_all(search_keyword=search_keyword, filter_keyword=filter_keyword, min_words=min_words,
                         pdf_min_num_page=pdf_min_num_page, num_years=num_years)
    filter.run_both_filters(search_keyword=search_keyword)
    upload.update_filtered(search_keyword=search_keyword)
    return upload.transfer(search_keyword=search_keyword)


def search_db(search_keyword, min_words, pdf_min_num_page, num_years):
    return run_database.get_db_results(search_keyword, pdf_min_num_page, min_words, num_years)


def scrape(search_keyword, filter_keyword, min_words, pdf_min_num_page, num_years):
    run_scrapers.run_all(search_keyword=search_keyword, filter_keyword=filter_keyword, min_words=min_words,
                         pdf_min_num_page=pdf_min_num_page, num_years=num_years)
    filter.run_both_filters(search_keyword=search_keyword)
    upload.update_filtered(search_keyword=search_keyword)
    upload.transfer(search_keyword)
    return 1


if __name__ == '__main__':
    # pp.pprint(
    #     search_db(search_keyword='中芯国际', min_words='3000', pdf_min_num_page='150', num_years=1))
    scrape(search_keyword='特斯拉', filter_keyword='', min_words='0', pdf_min_num_page='0', num_years=10)
