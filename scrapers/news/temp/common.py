import os
import shutil
import json
from datetime import datetime
from OCR import imgToText
now = datetime.now()

def nameCleaner(string):
    chars = [' ', '|','丨','\\','/','“','"','」','「',':']
    for elem in chars :
        if elem in string :
            string = string.replace(elem, '')
    return  string

def save(article,path,title, author, date, id, num_years):
    json_save_path = os.path.join(path, str(id) + '.json')
    html_save_path = os.path.join(path, str(id) + '.html')

    if(not os.path.exists(json_save_path)):
         if(prefilter(date, num_years)):
            text = article.get_text()
            if(len(text) >= 1000):
                print('--------%s passed prefilters--------' %id)
                #download html
                with open(html_save_path, "w", encoding='utf-8') as file:
                    file.write(str(article))
                file.close()


                #check OCR

                images = article.find_all('img')
                ocrText = ""
                if(len(images) > 5):
                    print('--------Performing OCR on %s--------' %id)
                    imageSRC = []
                    for img in images:
                        imageSRC.append(img.get('src'))
                    ocrText = imgToText(imageSRC)
                    print(ocrText)

                doc_info = {
                    'doc_id': id,
                    'title': title,
                    'date': date,
                    'org_name': author,
                    'doc_type': 'NEWS',
                    'text_count': len(text),
                    'image_count': len(images),
                    'text': text,
                    'ocrText': ocrText
                }

                with open(json_save_path, 'w', encoding='utf-8') as f:
                    json.dump(doc_info, f, ensure_ascii=False, indent=4)

def prefilter(date, num_years):
    ret = True
    dateToday = datetime.now().strftime("%Y")
    if date[0:3].isnumeric():
        years = int(dateToday) - int(date[0:4])
        if years > num_years:
            ret = False
    return ret
