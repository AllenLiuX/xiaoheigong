from flask import Flask
from flask_restful import Resource, Api
from flask import request
from flask_cors import CORS
from entry_point import search_db, get_all_tags
import json

app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/', methods=['POST'])
def get_query_string():
    query = request.get_json()["params"]
    tags = query['tags'] if 'tags' in query.keys() else []
    return {
        "data": search_db(search_keyword=query["search_keyword"], custom_keyword=query["custom_keyword"], min_words='500',
                          pdf_min_num_page=query["pdf_min_num_page"], num_years=query["num_years"],
                          page=query["page"], tags=tags, sort=query['sort'])
    }


@app.route('/tags', methods=['GET'])
def get_tags():
    return get_all_tags()


if __name__ == "__main__":
    app.run(host='0.0.0.0')

# run to start environment .\env\Scripts\Activate.ps1
# then run py server.py
