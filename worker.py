import entry_point.scrape as scrape
with open("company.txt", "rb") as f:
    contents = f.read().decode("UTF-8")
    scrape(search_keyword='恒大', filter_keyword='',
           min_words='0', pdf_min_num_page='0', num_years=10)
