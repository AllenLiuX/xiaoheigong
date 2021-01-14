import time
import sys
import pandas as pd
import numpy as np
sys.path.append('/Users/vincentl/PycharmProjects/Projects/xiaoheigong/')
import Backend.storage.mongodb as mg

company_path = 'company.csv'


def store_company():
    comp_df = pd.read_csv(company_path)
    for index in comp_df.index:
        row = comp_df.loc[index, :].tolist()
        id = row[0]
        name = row[1]
        data = {'id': id, 'name': name}
        try:
            mg.delete_datas({'name': name}, 'company_list', 'Company')
        except:
            pass
        mg.insert_data(data, 'company_list', 'Company')
    print(comp_df)

def company_to_id(name):
    query = {'name': name}
    datas = mg.show_datas('company_list', query, 'Company')
    if not datas:
        print('no company found')
        return 'no company found'
    id = datas[0]['id']
    return id


def id_to_companies(id):
    query = {'id': id}
    datas = mg.show_datas('company_list', query, 'Company')
    if not datas:
        print('no id found')
        return 'no id found'
    companies = []
    for data in datas:
        companies.append(data['name'])
    return companies

def company_to_companies(name):
    id = company_to_id(name)
    companies = id_to_companies(id)
    return companies

if __name__ == '__main__':
    start_time = time.time()
    store_company()
    id = company_to_id('特斯拉2')
    print(id)
    companies = id_to_companies('91330100716105852F')
    print(companies)
    print(company_to_companies('阿里'))
    print('======= Time taken: %f =======' %(time.time() - start_time))