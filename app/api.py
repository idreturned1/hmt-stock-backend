import re
import requests
from flask import Blueprint, request, Response
from flask_cors import cross_origin
from bson.json_util import dumps
from bs4 import BeautifulSoup

from app.controller import Controller
api_controller = Controller()

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
@cross_origin()
def base():
    return Response(response=dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')


@bp.route('/get', methods=['GET'])
@cross_origin()
def get_stock_update():
    userId = request.args.get("userId")
    if userId is None:
        return Response(response=dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    response = api_controller.get_stock_status_for_user(userId)
    return Response(response=dumps(response),
                    status=200,
                    mimetype='application/json')


@bp.route('/count', methods=['GET'])
@cross_origin()
def get_availability_count():
    userId = request.args.get("userId")
    if userId is None:
        return Response(response=dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    response = api_controller.get_availability_count_for_user(userId)
    return Response(response=response,
                    status=200,
                    mimetype='application/json')


@bp.route('/add', methods=['POST'])
@cross_origin()
def add_watch_url():
    data = request.json
    if data is None or data == {}:
        return Response(response=dumps({"Error": "Please provide data"}),
                        status=400,
                        mimetype='application/json')

    watchId = data['url'].split('/')[-1][0:-4]
    _id = api_controller.find_watch(watchId)

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

        _id = api_controller.add_watch(
            {'url': data['url'], 'name': name, 'categoryId': categoryId, 'price': price, 'watchId': watchId, 'inStock': inStock, 'image': imageUrl})

    response = api_controller.add_watch_for_user(data['userId'], _id)
    return Response(response=response,
                    status=200,
                    mimetype='application/json')