import json
import os
import time
import sys
sys.path.append('/Users/vincentl/PycharmProjects/Projects/xiaoheigong/')
from Backend.storage import mongodb as mg


keyword_list = {'历史沿革': '历史沿革', '历史事件': '历史沿革', '发展历程': '历史沿革',
                '组织架构': '组织架构',
                '股权架构': '股权架构', '股权变动': '股权架构', '股权结构': '股权架构', '股东': '股权架构', '股权': '股权架构',
                '管理团队': '管理团队', '董事会': '管理团队', '管理人': '管理团队',
                '薪酬体系': '薪酬体系',
                '奖励机制': '奖励机制',
                '业务': '产品', '服务': '产品', '产品': '产品',
                '生产情况': '生产情况', '生产流程': '生产情况', '生产工艺': '生产情况', '产能': '生产情况',
                '销售': '销售情况', '市场需求': '销售情况', '渠道': '销售情况',
                '知识产权': '知识产权', '商标': '知识产权', '专利': '知识产权',
                '核心技术': '核心技术', '核心竞争力': '核心技术', '壁垒': '壁垒',
                '研发': '研发事项', '迭代': '研发事项',
                '客户': '客户', '用户': '客户', '合作': '客户', '伙伴': '客户',
                '对手': '竞争对象', '竞争格局': '竞争对象', '竞争态势': '竞争对象', '头部': '竞争对象', '竞品': '竞争对象',
                '供应': '供应商', '采购': '供应商',
                '市场占有率': '市场占有率', '市场份额': '市场占有率', '市场竞争力': '市场占有率',
                '收入': '运营情况', '营收': '运营情况', '成本': '运营情况', '债务': '运营情况',
                '商业模式': '商业模式', '经营模式': '商业模式', '理念': '商业模式', '业务模型': '商业模式', '盈利模式': '商业模式',
                '增长点': '商业模式', '商业布局': '商业模式',
                '战略': '发展战略', '发展目标': '发展战略', '策略': '发展战略', '规划': '发展战略', '未来': '发展战略', '投资': '发展战略',
                '融资': '发展战略'
                }

label_map = {'历史沿革': ['历史沿革', '历史事件', '发展历程'],
             '组织架构': ['组织架构'],
             '股权架构': ['股权架构', '股权变动', '股权结构', '股东', '股权'],
             '管理团队': ['管理团队', '董事会', '管理人'],
             '薪酬体系': ['薪酬体系'], '奖励机制': ['奖励机制'],
             '产品': ['业务', '服务', '产品'],
             '生产情况': ['生产情况', '生产流程', '生产工艺', '产能'],
             '销售情况': ['销售', '市场需求', '渠道'],
             '知识产权': ['知识产权', '商标', '专利'],
             '核心技术': ['核心技术', '核心竞争力'],
             '壁垒': ['壁垒'],
             '研发事项': ['研发', '迭代'],
             '客户': ['客户', '用户', '合作', '伙伴'],
             '竞争对象': ['对手', '竞争格局', '竞争态势', '头部', '竞品'],
             '供应商': ['供应', '采购'],
             '市场占有率': ['市场占有率', '市场份额', '市场竞争力'],
             '运营情况': ['收入', '营收', '成本', '债务'],
             '商业模式': ['商业模式', '经营模式', '理念', '业务模型', '盈利模式', '增长点', '商业布局'],
             '发展战略': ['战略', '发展目标', '策略', '规划', '未来', '投资', '融资']
             }


def count_keywords(text: str) -> dict:
    """
    Count the number of occurrences of each keyword in self.keyword_list in text
    :param text: string version of pdf
    :return: a {keyword:count} dictionary
    """
    counter = {}
    for keyword, label in keyword_list.items():
        count = text.count(keyword)
        if label in counter:
            counter[label] += count
        else:
            counter.update({label: count})
    return counter


# temporarily needed. For generating label_map.
def reverse_keywords(keyword_list):
    reversed_keyword = {}
    for key, val in keyword_list.items():
        if val in reversed_keyword:
            reversed_keyword[val] = reversed_keyword[val]+[key]
        else:
            reversed_keyword[val] = [key]
    print(reversed_keyword)


def base_classifier(content, threshold):
    counter = count_keywords(content)

    print(counter)
    # print(keyword_list)

if __name__ == '__main__':
    start_time = time.time()
    # counter = count_keywords('历史事件历史事件历史事件历史事件')
    # print(counter)
    base_classifier('历史事件历史事件, 历史事件, 历史事件, 市场竞争力, 市场竞争力', 3)
    # reverse_keywords(keyword_list)
    print('======= Time taken: %f =======' %(time.time() - start_time))
