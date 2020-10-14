from selenium import webdriver
import os
from definitions import ROOT_DIR
import pprint as pp


def get_cookies(url):
    CHROME_DRIVER_PATH = os.path.join(ROOT_DIR, 'venv', 'chromedriver')
    chrome_driver = '/usr/local/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1420,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path = chrome_driver, chrome_options=chrome_options)
    #driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    driver.get(url)
    cookies = driver.get_cookies()
    driver.close()
    return cookies
