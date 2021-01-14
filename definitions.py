import os

# The root project directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OSS_PATH = 'http://xiaoheipdf.oss-accelerate.aliyuncs.com/'
CHROME_DRIVER_PATH = os.path.join(ROOT_DIR, 'venv', 'chromedriver')


# The number of occurrences of the company name in a pdf as a keyword
COMPANY_NAME_OCCUR = 3

# Dictionary storing all the relationship between acronyms and Chinese
translate = {'fxbg': '发现报告',
             'robo': '萝卜投研',
             '36kr': '36kr',
             'woshipm': '我是产品经理'}

tokens = {
    'fxbg': 'jaOLojHQVzv45khzOXkacIoiUUIYxwUIz9R8ywGC5qutZUMwgHW82H6YMIxHS1pi',
    'robo': '6F92C0E64F0F20766C1006C21F3DDECF'
}

if __name__ == '__main__':
    print(ROOT_DIR)
