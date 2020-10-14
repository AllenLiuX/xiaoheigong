from selenium import webdriver
import os
from definitions import ROOT_DIR, CHROME_DRIVER_PATH
import pprint as pp


def get_cookies(url):
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get(url)
    cookies = driver.get_cookies()
    driver.close()
    return cookies
