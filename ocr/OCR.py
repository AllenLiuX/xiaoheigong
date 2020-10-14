import cv2
import pytesseract

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


img = cv2.imread('test.jpg')

gray = get_grayscale(img)


# Adding custom options
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(img, config=custom_config, lang ="chi_sim")

# text = pytesseract.image_to_string(img, lang ="chi_sim")

text = text.replace(' ', '')
print(text)
