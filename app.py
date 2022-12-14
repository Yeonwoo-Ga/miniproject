from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)
import certifi
from pymongo import MongoClient

ca = certifi.where();
client = MongoClient('mongodb+srv://test:sparta@cluster0.khegl5v.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta
import datetime
from datetime import datetime, timedelta

from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
SECRET_KEY = 'SPARTA'

import jwt



import hashlib


@app.route('/')
def home():

    return render_template('index.html')

    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     user_info = db.user.find_one({"id": payload['id']})
    #     return render_template('index.html', borders=users, nickname=user_info["nick"], id=user_info["id"])
    # except jwt.ExpiredSignatureError:
    #     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # except jwt.exceptions.DecodeError:
    #     return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# @app.route('/membership')
# def membership():
#     return render_template('membership.html')
#
#
# @app.route('/api/membership', methods=['POST'])
# def api_membership():
#     id_receive = request.form['id_give']
#     pw_receive = request.form['pw_give']
#     nickname_receive = request.form['nickname_give']
#
#     pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
#
#     db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
#
#     return jsonify({'result': 'success'})


@app.route('/login')
def login():
    return render_template('login.html')


# @app.route('/api/login', methods=['POST'])
# def api_login():
#     id_receive = request.form['id_give']
#     pw_receive = request.form['pw_give']
#
#     # 암호화
#     pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
#
#     # 유저찾기
#     result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
#
#     # JWT 토큰발급
#     if result is not None:
#
#         payload = {
#             'id': id_receive,
#             'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
#         }
#         token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf8')
#
#         # token주기
#         return jsonify({'result': 'success', 'token': token})
#     # 없을 시
#     else:
#         return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
#
#
# @app.route('/api/nick', methods=['GET'])
# def api_valid():
#     token_receive = request.cookies.get('mytoken')
#
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256']).decode('utf8')
#         print(payload)
#
#         userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
#         return jsonify({'result': 'success', 'nickname': userinfo['nick']})
#     except jwt.ExpiredSignatureError:
#         return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
#     except jwt.exceptions.DecodeError:
#         return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/api/sign_in', methods=['POST'])
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디

    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})
@app.route('/post_list')
def post_list():
    return render_template('post_list.html')


@app.route('/post_write')
def post_write():
    return render_template('post_write.html')


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256']).decode('utf8')
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart"}))
            return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "my_username": payload["id"]})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/post_view')
def post_view():
    return render_template('post_view.html')


@app.route('/membership')
def membershop():
    return render_template('membership.html')


@app.route('/list', methods=['GET'])
def show_list():
    lists = list(db.list.find({}, {'_id': False}).sort('_id', -1))
    return jsonify({'all_lists': lists})


@app.route('/list/save', methods=['POST'])
def save_list():
    title_receive = request.form['title_give']
    text_receive = request.form['text_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/img/{filename}.{extension}'
    num_list = list(db.list.find({}, {'_id': False}))
    file.save(save_to)
    count = len(num_list) + 1
    doc = {
        'num': count,
        'title': title_receive,
        'text': text_receive,
        'file': f'{filename}.{extension}',
        'time': today.strftime('%Y.%m.%d')
    }

    db.list.insert_one(doc)

    return jsonify({'msg': '게시글 작성 완료!'})


@app.route("/list/delete", methods=["POST"])
def list_delete():
    num_receive = request.form['num_give']
    db.list.delete_one({'num': int(num_receive)})
    return jsonify({'msg': '삭제 완료'})


@app.route('/postview/<title>')
def show_clicked_post(title):
    data = db.list.find_one({'title': title}, {'_id': False})
    num = data['num']
    title = data['title']
    text = data['text']
    file = data['file']
    time = data['time']

    return render_template("post_view.html",
                           num=num,
                           title=title,
                           text=text,
                           file=file,
                           time=time,
                           )


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
