import datetime
import json
import os
from lxml import etree

import config


def calc_date(s_date, e_date):
    '''
    过滤函数时间,计算输入时间与config.S_TIME时间相差天数
    :param s_date:
    :param e_date:
    :return:
    '''
    try:
        s_date = datetime.datetime.strptime(s_date, "%Y-%m-%d")
        e_date = datetime.datetime.strptime(e_date, "%Y-%m-%d")
        day = e_date - s_date
    except:
        return True
    return True if day.days > 0 else False


def reduce_date(reduction):
    if type(reduction) != int:
        reduction = reduction if len(reduction) == 1 else reduction[0]
    s_date = config.S_TIME.split('-')
    s_date[0] = str(int(s_date[0]) - int(reduction))
    new_s_date = '-'.join(s_date)
    return new_s_date


def filter_space_json(text_list):
    '''
    清楚标签内容的\n \t \r 空格等无用字符
    :param text_list:
    :return: str
    '''
    text = ''.join(a for a in text_list if a.split() != [])
    return text


def filter_space_html(text_list):
    '''
    将element转换成标签并出去\n \t \r等无用字符
    :param text_list: 网页标签element
    :return: 解析处理后的网页标签 eg: [div<..........>, .....]
    '''
    result = []
    for h in text_list:
        h2 = etree.tostring(h, method='html')
        h3 = ' '.join(h2.decode('utf-8').split())
        result.append(h3)
    return result


def write_down_html(path, filename, text):
    '''
    数据保存
    :param filename: 文件名 xxx.html
    :param path:路径
    :param text: 保存内容 [label1, label2,...]
    :return:
    '''
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), 'a', encoding='utf-8') as f:
        for t in text:
            f.write(t + '\n')


def write_down_json(path, filename, text):
    '''
    数据保存
    :param filename: 文件名
    :param path:路径
    :param text: 保存内容
    :return:
    '''
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), 'w', encoding='utf-8') as f:
        f.write(str(text))


def get_next_html(url, headers, xpath_list, next_page_xpath):
    '''
    针对分页文章
    :param url:url2 文章内容rul
    :param headers: headers
    :param xpath_list: 需要获取的标签
    :param next_page_xpath: 下一页标签链接
    :return:
    '''
    import requests
    result = []
    res = requests.get(url=url, headers=headers)
    html = etree.HTML(res.text)
    for xpath in xpath_list:
        result.append(html.xpath(xpath))
    try:
        next_page = html.xpath(next_page_xpath)[0]
    except:
        next_page = ''
    return result, next_page


if __name__ == '__main__':
    a = 4
    print(reduce_date(reduction=a))
