from bs4 import BeautifulSoup
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.9cihgwo.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html',user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

#--------------------메인페이지---------------
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/book/detail')
def book_detail():
    return render_template('book_detail.html')

# -------------------독후감-------------------

@app.route('/bookreport')
def review():
    return render_template('bookreport.html')
@app.route("/book", methods=["POST"])
def book_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    import requests
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

@app.route("/save/edit", methods=["POST"])
def edit_post():
    num_receive = request.form['num_give']
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    db.books.update_one({'num': int(num_receive)},
                              {'$set': {'url': url_receive, 'star': star_receive, 'comment': comment_receive}})
    return jsonify({'msg': '수정 완료!'})

@app.route("/delete", methods=["POST"])
def delete_post():
    num_receive = request.form['num_give'];
    db.books.delete_one({'num': int(num_receive)})
    print(num_receive)  # num값이 들어오는것을 확인
    return jsonify({'msg': '삭제 완료!'})


# ------------------로그인-------------------

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        # status -> 이걸 이용해서 jinja2 를 이용하면 로그아웃 버튼과 프로필 편집 기능을 없애버릴수있음

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/logout', methods=['POST'])
def logout():
    remove_token = request.cookies.get('mytoken')
    from dns.message import make_response
    response = make_response(redirect(url_for('/')))
    response.set_cookie('mytoken', remove_token, expires=0)
    return response




@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    print(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    print(username_receive)
    exists = bool(db.users.find_one({"username": username_receive}))
    print(exists)
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/"+file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive
        }
        db.posts.insert_one(doc)

        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("date", -1).limit(20))
        #find 해서 다 들고 오는데 조건이 없기 때문에 sort를 해서 걸러주고 / 20개만 들고오겠다는 듰
        for post in posts:
            post["_id"] = str(post["_id"])
            # 고유한 식별자가 필요하기 때문에 id 값으로 식별한다.
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            # 현재 해당 글의 좋아요 숫자가 몇 객인지 세서 적으라는 뜼
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload["id"]}))
            # 두줄의 정보가 추가 되었는데, count_heart 부분에
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 우리는 토큰을 알고 있기 때문에 누가 좋아요 했는지를 쉽게 알 수 있다.
        user_info = db.users.find_one({"username": payload["id"]})
        # 이 토큰에서 id 만 꺼내오면 누가 좋아요를 눌렀는지 바로 알수 있따.
        post_id_receive = request.form["post_id_give"]
        # receive  어떤 글을 receive 를 할때, get_post 함수에서 그 id 값중에서 서버에 전달 해줘야 하는 id 값을 정함

        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        # 그럴때 이게 취소하는 값인지 확인하고
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        # 세개의 정보르 받아서 많약 이게 좋아요다? 그럼 어찌 됐든 어떤 사람이 어떤 글에 좋아요는 하나 밖에 못하기 때문에 셀수 있다 값을
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        # 그럼 count 를 이용해서 값을 계산 할 수 있고
        return jsonify({"result": "success", 'msg': 'updated', "count": count})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)