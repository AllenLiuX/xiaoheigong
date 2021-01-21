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
    return {
        "data": search_db(search_keyword=query["search_keyword"], min_words='500',
                          pdf_min_num_page=str(query["pdf_min_num_page"]), num_years=int(query["num_years"]),
                          tags=query["tags"])
    }


@app.route('/tags', methods=['GET'])
def get_tags():
    return get_all_tags()


if __name__ == "__main__":
    app.run(host='0.0.0.0')

# run to start environment .\env\Scripts\Activate.ps1
# then run py server.py
