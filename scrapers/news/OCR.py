import cv2
import pytesseract
import requests
from PIL import Image

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def imgToText(list):
    ret = ""

    for url in list:
        # Adding custom options
        custom_config = r'--oem 3 --psm 12'
        img = Image.open(requests.get(url, stream = True).raw)
        text = pytesseract.image_to_string(img, config=custom_config, lang ="chi_sim")
        text = text.replace(' ', '')
        text = text.replace('\n', '')
        text = text.replace('\t', '')
         # text = pytesseract.image_to_string(img, lang ="chi_sim")
        ret += text
    return ret
