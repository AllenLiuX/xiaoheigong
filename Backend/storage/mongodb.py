import datetime as dt
import pprint as pp

import pymongo

from definitions import COMPANY_NAME_OCCUR

myclient = pymongo.MongoClient("mongodb://localhost:27017/")


def insert_data(data, collection, db='articles'):
    mydb = myclient[db]  # use articles as default database
    mycol = mydb[collection]
    x = mycol.insert_one(data)
    print(x.inserted_id)


def insert_datas(data_list, collection, db='articles'):
    mydb = myclient[db]  # use articles as default database
    mycol = mydb[collection]  # collection
    x = mycol.insert_many(data_list)
    print(x.inserted_ids)


def show_datas(collection, query={}, page=1, db='articles', sortby='_id', seq=True):
    mydb = myclient[db]
    mycol = mydb[collection]
    result = []

    if seq:
        objects = mycol.find(query).sort(sortby).skip((page - 1) * 10).limit(10)
    else:
        objects = mycol.find(query).sort(sortby, -1).skip((page - 1) * 10).limit(10)
    for x in objects:
        result.append(x)
    return result


def search_datas(search_keyword, pdf_min_page, min_word_count, num_years, page, tags, db='articles'):
    mydb = myclient[db]
    result = []
    date = dt.datetime.now() - dt.timedelta(num_years * 365)

    query = {
        'keywordCount.%s' % search_keyword: {'$gt': COMPANY_NAME_OCCUR},
        '$or': [{'page_num': {'$gt': pdf_min_page}}, {'wordCount': {'$gt': min_word_count}}],
        'date': {'$gte': date.isoformat()},
        'filtered': 1
    }

    if tags:
        query.update({'tags.list': {'$all': tags}})

    for collection in mydb.list_collection_names():
        result += show_datas(collection, query, page)

    return result


def delete_datas(query, collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    x = mycol.delete_many(query)
    print(x.deleted_count, ' objects has been deleted.')


def update_datas(query, values, collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    x = mycol.update_many(query, values)
    print(x.modified_count, ' objects has been modified.')


def delete_col(collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    mycol.drop()


if __name__ == '__main__':
    result = search_datas(search_keyword='中芯国际', pdf_min_page=20, min_word_count=3000, num_years=5)
    for r in result:
        print(r['date'])
