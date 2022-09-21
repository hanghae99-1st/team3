from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.2bmu9hy.mongodb.net/cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/book", methods=["POST"])
def book_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    image = og_image['content']
    title = og_title['content']
    description = og_description['content']
    books_list = list(db.books.find({}, {'_id': False}))
    count = len(books_list) + 1

    print(count)
    doc = {
        'num': count,
        'image':image,
        'title':title,
        'desc':description,
        'star':star_receive,
        'comment':comment_receive
    }

    db.books.insert_one(doc)

    return jsonify({'msg':'POST 연결 완료!'})

@app.route("/book", methods=["GET"])
def book_get():
    book_list = list(db.books.find({}, {'_id': False}))

    return jsonify({'books':book_list})



@app.route("/open/edit", methods=["GET"])
def edit_get():
    num_receive = request.args.get('num_give')
    books_list = list(db.books.find({'num': int(num_receive)}, {'_id': False}))

    return jsonify({'books': books_list})


# pythonthema - 수정 POST요청, title, 별점, 코멘트 데이터 수정용 POST API 구성
@app.route("/save/edit", methods=["POST"])
def edit_post():
    num_receive = request.form['num_give']
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    db.books.update_one({'num': int(num_receive)},
                              {'$set': {'url': url_receive, 'star': star_receive, 'comment': comment_receive}})
    return jsonify({'msg': '수정 완료!'})


# pythonthema - 삭제 요청 API 구성
@app.route("/delete", methods=["POST"])
def delete_post():

    num_receive = request.form['num_give'];

    db.books.delete_one({'num': int(num_receive)})
    print(num_receive)  # num값이 들어오는것을 확인
    return jsonify({'msg': '삭제 완료!'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
