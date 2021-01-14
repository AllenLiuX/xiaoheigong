import sys
# import scrapers.news.cyzone as cyzone
import Backend.scrapers.news.huxiu as huxiu
# import scrapers.news.iyiou as iyiou
# import scrapers.news.leiphone as leiphone
# import scrapers.news.pencilnews as pencilnews
# import scrapers.news.lieyunwang as lieyunwang
# import scrapers.report.woshipm_scrapper as wspm
# import scrapers.news._51pdf as _51pdf
# import scrapers.news._767stock as _767stock
import time

import Backend.scrapers.news._36kr_scraper as _36kr
import Backend.scrapers.report.fxbg_scraper as fxbg
import Backend.scrapers.report.robo_scraper as robo


def run_all(search_keyword, filter_keyword, min_words, pdf_min_num_page, num_years):
    """
    Run all scrapers with time
    :param search_keyword:
    :param filter_keyword:
    :param min_words:
    :param pdf_min_num_page:
    :param num_years:
    :return:
    """
    start_time = time.time()
    search_keyword = sys.argv[1] if len(sys.argv) > 1 else search_keyword
    get_pdf = len(sys.argv) <= 1

    # fxbg.run(search_keyword=search_keyword, filter_keyword=filter_keyword, pdf_min_num_page=pdf_min_num_page,
    #          num_years=num_years, get_pdf=get_pdf)
    robo.run(search_keyword=search_keyword, filter_keyword=filter_keyword, pdf_min_num_page=pdf_min_num_page,
             num_years=num_years, get_pdf=get_pdf)
    _36kr.run(search_keyword=search_keyword, min_word_count=min_words, num_years=num_years, get_pdf=get_pdf)
    # wspm.run(search_keyword, min_words, num_years, 15, '', get_pdf=get_pdf)

    # cyzone.run(search_keyword=search_keyword)
    huxiu.run(search_keyword=search_keyword, min_word_count=min_words, get_pdf=get_pdf)
    # iyiou.run(search_keyword=search_keyword)
    # leiphone.run(search_keyword=search_keyword)
    # pencilnews.run(search_keyword=search_keyword)
    # lieyunwang.run(search_keyword=search_keyword)

    # _51pdf.main(search_word=search_keyword, max_art=30, max_text=300, s_date='2018-01-01')
    # _767stock.main(search_word=search_keyword, max_art=30, max_text=300, s_date='2018-01-01')

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    run_all(search_keyword='恒大', filter_keyword='', min_words='2000', pdf_min_num_page='10', num_years=10)
