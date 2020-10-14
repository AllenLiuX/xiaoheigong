import pymongo
import datetime as dt
import pprint as pp

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


def show_datas(collection, query={}, db='articles', sortby='_id', seq=True):
    mydb = myclient[db]
    mycol = mydb[collection]
    result = []
    if seq:
        objects = mycol.find(query).sort(sortby)
    else:
        objects = mycol.find(query).sort(sortby, -1)
    for x in objects:
        result.append(x)
    return result


def search_datas(search_keyword, pdf_min_page, min_word_count, num_years, db='articles'):
    mydb = myclient[db]
    result = []
    date = dt.datetime.now() - dt.timedelta(num_years * 365)

    query = {
        'keywordCount.%s' % search_keyword: {'$gt': 30},
        '$or': [{'page_num': {'$gt': pdf_min_page}}, {'wordCount': {'$gt': min_word_count}}],
        # 'date': {'$gt': date},
        'filtered': 1
    }
    for collection in mydb.list_collection_names():
        result += show_datas(collection, query)

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
    # insert_datas([{'a': 'hello2'}, {'a': 'hello3'}, {'a': 'hello4'}], 'fxbg')
    # data = show_datas('fxbg', sortby='a', seq=False)
    # print(data)
    # delete_datas({'a': {'$regex': '^mod'}}, 'fxbg')
    # update_datas({'a': {'$regex': '^hello'}}, {'$set': {'a': 'modified'}}, 'fxbg')
    # data = show_datas('fxbg')
    # print(data)
    # # 获取数据库list
    # dblist = myclient.list_database_names()
    # print(dblist)
    # id_match_res = show_datas('woshipm', query={'id': 3134984})
    # print(id_match_res)
    # print(show_datas('robo', query={'page_num': {'$gt': 104}}))
    result = search_datas(search_keyword='中芯国际', pdf_min_page=20, min_word_count=3000, num_years=5)
    for r in result:
        print(r['_id'])
