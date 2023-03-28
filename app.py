from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)


client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbkeunjibook

# HTML을 주는 부분


@app.route('/newbook')
def home():
    return render_template('index.html')


@app.route('/save')
def home2():
    return render_template('index2.html')


@app.route('/miss')
def home3():
    return render_template('index3.html')


@app.route('/search', methods=['POST'])
def saving():
    db.newbooks.delete_many({})
    db.newbooks.drop()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(
        'https://www.kyobobook.co.kr/categoryRenewal/categoryTab.laf?pageNumber=1&perPage=100&mallGb=KOR&linkClass=0126&ejkGb=&sortColumn=near_date&menuCode=003',
        headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    lis = soup.select('#prd_list_type1 li.id_detailli')

    # prd_list_type1 > li:nth-child(17) > div > div.info_area > div.detail > div.pub_info > span:nth-child(3)
    # prd_list_type1 > li:nth-child(35) > div > div.info_area > div.detail > div.pub_info > span:nth-child(3)

    for li in lis:
        isbn = li.select_one('div > div.info_area > div.detail > div.title > a')[
            'href'].split(',')[2]
        title = li.select_one(
            'div > div.info_area > div.detail > div.title > a > strong').text
        img = li.select_one(
            'div > div.info_area > div.cover_wrap > div > a > span > img')['src']
        desc = li.select_one(
            'div > div.info_area > div.detail > div.info > span').text.strip()
        date = li.select_one(
            'div > div.info_area > div.detail > div.pub_info > span:nth-child(3)').text.strip()
        if title is not None:
            doc = {
                'title': title,
                'img': img,
                'desc': desc,
                'isbn': isbn,
                'date': date
            }
            db.newbooks.insert_one(doc)
    return jsonify({'msg': '저장이 완료되었습니다.'})


@app.route('/search', methods=['GET'])
def listing():
    lists = list(db.newbooks.find({}, {'_id': False}))
    return jsonify({'lists': lists})


@app.route('/regist', methods=['POST'])
def mybooksaving():
    isbn_receive = request.form['isbn_give']
    url = 'https://seoji.nl.go.kr/landingPage/SearchApi.do?cert_key={인증키}&result_style=json&page_no=1&page_size=10'
    params = {'isbn': isbn_receive}
    mybook = requests.get(url, params).json()['docs'][0]

    series_title = mybook['SERIES_TITLE']
    publisher = mybook['PUBLISHER']
    title = mybook['TITLE']
    author = mybook['AUTHOR']
    vol1 = mybook['SERIES_NO']
    vol2 = mybook['VOL']

    doc = {'series_title': series_title,
           'publisher': publisher,
           'title': title,
           'author': author,
           'vol1': vol1,
           'vol2': vol2,
           'isbn': isbn_receive}

    db.mybooks.insert_one(doc)

    return jsonify({'msg': '저장이 완료되었습니다.'})


@app.route('/regist', methods=['GET'])
def mybooklisting():
    lists = list(db.mybooks.find({}, {'_id': False}))
    return jsonify({'lists': lists})


@app.route('/regist3', methods=['POST'])
def missbook():
    isbnnum_receive = request.form['isbnnum_give']
    bsnum_receive = request.form['bsnum_give']
    url = 'https://seoji.nl.go.kr/landingPage/SearchApi.do?cert_key={인증키}&result_style=json&page_no=1&page_size=10'
    params = {'isbn': isbnnum_receive}
    kbbook = requests.get(url, params).json()['docs'][0]

    series_title = kbbook['SERIES_TITLE']
    publisher = kbbook['PUBLISHER']
    title = kbbook['TITLE']
    author = kbbook['AUTHOR']
    vol1 = kbbook['SERIES_NO']
    vol2 = kbbook['VOL']

    doc = {'series_title': series_title,
           'publisher': publisher,
           'title': title,
           'author': author,
           'vol1': vol1,
           'vol2': vol2,
           'isbn': isbnnum_receive,
           'bsnumber': bsnum_receive}

    db.kyobobooks.insert_one(doc)
    return jsonify({"msg": "저장이 완료되었습니다."})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
