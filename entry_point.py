import scrapers.run as run_all
import processing.filter as filter
import processing.upload as upload
import processing.run_database as run_database


def run(search_keyword, filter_keyword, min_words, pdf_min_num_page, num_years):
    run_database.get_db_results(search_keyword=search_keyword, min_word_count=min_words,
                                pdf_min_page=pdf_min_num_page, num_years=num_years)
    run_all.run_all(search_keyword=search_keyword, filter_keyword=filter_keyword, min_words=min_words,
                    pdf_min_num_page=pdf_min_num_page, num_years=num_years)
    filter.run_both_filters()
    upload.update_filtered(search_keyword=search_keyword)
    return upload.transfer(search_keyword=search_keyword)


if __name__ == '__main__':
    run(search_keyword='中芯国际', filter_keyword='', min_words='3000', pdf_min_num_page='150', num_years=1)
