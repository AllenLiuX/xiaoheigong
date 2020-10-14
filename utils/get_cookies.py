from selenium import webdriver
import os
from definitions import ROOT_DIR, CHROME_DRIVER_PATH
import pprint as pp


def get_cookies(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
    driver.get(url)
    cookies = driver.get_cookies()
    driver.close()
    return cookies
