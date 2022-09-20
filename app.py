# -- coding: utf-8 --
import urllib.request

from flask import Flask
app = Flask(__name__)


import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urlparse, parse_qs, parse_qsl
import xml.etree.ElementTree as ET
import xmltodict
import time

import requests
import json
from urllib.parse import urlparse
from urllib.parse import urlparse, parse_qs, parse_qsl
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@app.route('/test', methods=['GET'])
def test_get():
    title_receive = request.args.get('title_give')
    print(title_receive)
    return jsonify({'result':'success', 'msg': '이 요청은 GET!'})

@app.route('/books/{bookId}')
def api_arrange(value):
    for key, value in enumerate(value):
        book_lists = {}

        try:
            book_lists['G_NAME'] = value['G_NAME']
        except:
            book_lists['G_NAME'] = '';

        try:
            book_lists['G_PRICE'] = value['G_PRICE']
        except:
            book_lists['G_PRICE'] = '';

        try:
            book_lists['G_SIMPLE'] = value['G_SIMPLE']
        except:
            book_lists['G_SIMPLE'] = '';

        try:
            book_lists['IMG_URL'] = value['IMG_URL']
        except:
            book_lists['IMG_URL'] = '';

        try:
            book_lists['PONGJEL_YN'] = value['PONGJEL_YN']
        except:
            book_lists['PONGJEL_YN'] = '';

        try:
            book_lists['PUBLIC_YEAR'] = value['PUBLIC_YEAR']
        except:
            book_lists['PUBLIC_YEAR'] = '';


        new_book_list = list((book_lists.values()))

        title = '제목 : ' + new_book_list[0],
        price = '가격 : ' + new_book_list[1],
        if new_book_list[2] is not None:
            desc = '설명 : ' + new_book_list[2],
        img = '이미지 : ' + new_book_list[3],
        sell = '판매여부 : ' + new_book_list[4],
        year = '출판연도 : ' + new_book_list[5]

        print(title, price, desc, img, sell, year)


def api_get_xml(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
    }

    req = requests.get(url, headers=headers)
    req_html = req.content.decode('utf-8', 'replace')
    req_html = req.text
    collection_list = {}

    if req.status_code == 200:
        root = ET.fromstring(req_html)

        cc = xmltodict.parse(req_html)
        json_out = json.dumps(cc, indent=4, sort_keys=True)
        dd = json.loads(json_out)
        # print(dd['bookStoreNewInfo']['row'])

        return dd['bookStoreNewInfo']['row']


def execution_one_time(url):
    APIRESULT = api_get_xml(url)
    api_arrange(APIRESULT)


url = 'http://openapi.seoul.go.kr:8088/5172794b68717764353457746a6876/xml/bookStoreNewInfo/1/244'
execution_result = execution_one_time(url)
