from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.khegl5v.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

from datetime import datetime


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/post_list')
def post_list():
    return render_template('post_list.html')


@app.route('/post_write')
def post_write():
    return render_template('post_write.html')


@app.route('/post_view')
def post_view():
    return render_template('post_view.html')


@app.route('/list', methods=['GET'])
def show_list():
    lists = list(db.list.find({}, {'_id': False}))
    return jsonify({'all_lists': lists})


@app.route('/list', methods=['POST'])
def save_list():
    title_receive = request.form['title_give']
    text_receive = request.form['text_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/img/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'title': title_receive,
        'text': text_receive,
        'file': f'{filename}.{extension}',
        'time': today.strftime('%Y.%m.%d')
    }

    db.list.insert_one(doc)

    return jsonify({'msg': '게시글 작성 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
