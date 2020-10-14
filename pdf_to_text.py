import xpdf_python.wrapper as wrapper
from datetime import datetime

if __name__ == '__main__':
    # To be replaced with a universal pdf-text converter
    file = '爬虫需求.pdf'
    text = wrapper.to_text(file)[0]
    text = text.strip('\n').rstrip()
    print(text)
    # print(len(text))
    #date = '2015-05-05'
    #date = datetime.strptime(date, '%Y-%m-%d')
    #num_years = 5
    #new_date = datetime(date.year - num_years, 1, 1).isoformat()
    # print(new_date)



# print(text.count('中芯国际'))
