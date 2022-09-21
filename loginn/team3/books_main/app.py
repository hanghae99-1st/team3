import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@Cluster0.zysnu4d.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/detail', methods=["GET"])
def book_post():
    url = 'http://openapi.seoul.go.kr:8088/5172794b68717764353457746a6876/xml/bookStoreNewInfo/1/244'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.text, "xml")

    rows = soup.find_all("row")

    for row in rows:
        if row != None:
            bookId = row.find('UID_').string
            title = row.find('G_NAME').string
            selling = row.find('PONGJEL_YN').string
            price = row.find('G_PRICE').string
            desc = row.find('G_SIMPLE').string
            year = row.find('PUBLIC_YEAR').string
            img = row.find('IMG_URL').string
        else:
            bookId == 'none',
            title == 'none',
            selling == 'none',
            price == 'none',
            desc == 'none',
            year == 'none',
            img == 'none'

        doc = {
            "bookId": bookId,
            "title": title,
            "selling": selling,
            "price": price,
            "desc": desc,
            "year": year,
            "img": img
        }

        db.books.insert_one(doc)

    book_lists = list(db.books.find({}, {'_id': False}))
    dict_result = []
    for i in book_lists:
        dict_list = []
        dict_list.append(i)
        dicttolist = dict_list[0]
        result = list(dicttolist.values())

        for j in dicttolist:
            dict_plus = {
                'id': result[0],
                'img': result[6],
                '제목': result[1],
                '판매여부': result[2],
                '가격': result[3],
                '설명': result[4],
                '출판연도': result[5]
            }
            dict_result.append(dict_plus)

    json_data = json.dumps(dict_result)


    return render_template('main.html', json_data = json_data)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


