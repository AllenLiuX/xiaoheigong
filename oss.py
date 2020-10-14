# -*- coding: utf-8 -*-
from __future__ import print_function
import oss2
from itertools import islice
import os, sys

#Tuturial: https://www.alibabacloud.com/help/zh/doc-detail/32027.htm?spm=a2c63.p38356.b99.344.35e229afz0w5oV


# 当无法确定待上传的数据长度时，total_bytes的值为None。
def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')
        sys.stdout.flush()


def upload_file(obj, path):
    auth = oss2.Auth('LTAI4G6t2sZHcAknEZXEbcuZ', 'eyk2Qcv669bXmoqx1a4c21U5nvfnje')  #自己创建的用户
    bucket = oss2.Bucket(auth, 'http://oss-accelerate.aliyuncs.com', 'xiaoheipdf')
    # <yourObjectName>上传文件到OSS时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
    # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
    bucket.put_object_from_file(obj, path, progress_callback=percentage)



def get_file(obj, path):
    auth = oss2.Auth('LTAI4G6t2sZHcAknEZXEbcuZ', 'eyk2Qcv669bXmoqx1a4c21U5nvfnje')
    bucket = oss2.Bucket(auth, 'http://oss-accelerate.aliyuncs.com', 'xiaoheipdf')
    bucket.get_object_to_file(obj, path)


def list_file():
    auth = oss2.Auth('LTAI4G6t2sZHcAknEZXEbcuZ', 'eyk2Qcv669bXmoqx1a4c21U5nvfnje')
    bucket = oss2.Bucket(auth, 'http://oss-accelerate.aliyuncs.com', 'xiaoheipdf')
    for b in islice(oss2.ObjectIterator(bucket), 10):
        print(b.key)


if __name__=='__main__':
    path = os.getcwd()+'/PDFs/'
    files = os.listdir('PDFs')
    print(path, files)
    for f in files:
        upload_file('test_pdfs/'+f, path+f)