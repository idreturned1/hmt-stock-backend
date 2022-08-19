import re
import requests
import threading
from flask import Flask, request, json, Response
from flask_cors import cross_origin
from controller import Controller
from multiprocessing import Pool
from bs4 import BeautifulSoup
from bson.json_util import dumps



def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def process_stock(watchInstance):
    if (watchInstance['url'] is not None):
        page = requests.get(watchInstance['url'])
        soup = BeautifulSoup(page.content, "html.parser")

        inStock = True if soup.find(
            id="ContentPlaceHolder1_btn_request")['value'] == 'Add to Cart' else False

        priceText = soup.find(id="ContentPlaceHolder1_tr_mrp").text
        priceSearch = re.search('(\d+)', priceText)
        if priceSearch:
            price = int(priceSearch.group(1))

        return {'_id': watchInstance['_id'], 'updateData': {
            'inStock': inStock, 'price': price}}


def update_stock():
    watchList = controller.get_stock_list()
    pool = Pool()
    latestStockData = pool.map(process_stock, watchList)
    pool.close()
    pool.join()
    for data in latestStockData:
        controller.save_stock_update(data['_id'], data['updateData'])


app = Flask(__name__)


@app.route('/')
@cross_origin()
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')


@app.route('/api/get', methods=['GET'])
@cross_origin()
def get_stock_update():
    userId = request.args.get("userId")
    if userId is None:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    response = controller.get_stock_status_for_user(userId)
    return Response(response=dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/api/count', methods=['GET'])
@cross_origin()
def get_availability_count():
    userId = request.args.get("userId")
    if userId is None:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    response = controller.get_availability_count_for_user(userId)
    return Response(response=response,
                    status=200,
                    mimetype='application/json')


@app.route('/api/add', methods=['POST'])
@cross_origin()
def add_watch_url():
    data = request.json
    if data is None or data == {}:
        return Response(response=dumps({"Error": "Please provide data"}),
                        status=400,
                        mimetype='application/json')

    watchId = data['url'].split('/')[-1][0:-4]
    _id = controller.find_watch(watchId)

    if (_id == None):
        page = requests.get(data['url'])
        soup = BeautifulSoup(page.content, "html.parser")
        categoryId = int(data['url'].split('/')[3])
        inStock = False if soup.find(
            id="ContentPlaceHolder1_btn_request") != None else True

        priceText = soup.find(id="ContentPlaceHolder1_tr_mrp").text
        priceSearch = re.search('(\d+)', priceText)
        if priceSearch:
            price = int(priceSearch.group(1))

        name = soup.find('h4').text.strip()

        imageUrl = soup.find(id="sim544741")['src']

        _id = controller.add_watch(
            {'url': data['url'], 'name': name, 'categoryId': categoryId, 'price': price, 'watchId': watchId, 'inStock': inStock, 'image': imageUrl})

    response = controller.add_watch_for_user(data['userId'], _id)
    return Response(response=response,
                    status=200,
                    mimetype='application/json')



controller = Controller()
set_interval(update_stock, 30 * 60)
