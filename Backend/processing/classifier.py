import sys
import time

from definitions import KW_TO_TAG, TAG_TO_KW

sys.path.append('/Users/vincentl/PycharmProjects/Projects/xiaoheigong/')

keyword_list = KW_TO_TAG  # updated new kw-tag relation in definitions -- Matthew

label_map = TAG_TO_KW  # updated new tag-kw relation in definitions -- Matthew


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
            reversed_keyword[val] = reversed_keyword[val] + [key]
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
    print('======= Time taken: %f =======' % (time.time() - start_time))
