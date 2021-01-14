import datetime
import os

from definitions import ROOT_DIR


class NoDocError(Exception):
    def __init__(self, message):
        self.message = message


class UploadError(Exception):
    def __init__(self, message):
        self.message = message


class DownloadError(Exception):
    def __init__(self, message):
        self.message = message


class ResponseError(Exception):
    def __init__(self, message):
        self.message = message


def updateError(message):
    print(message)
    error_file = open(os.path.join(ROOT_DIR, 'error_report.txt'), 'a')
    error_file.write('%s: ' % str(datetime.datetime.now()))
    error_file.write(message + '\n')
    error_file.close()
