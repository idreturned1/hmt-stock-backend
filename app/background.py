import re
import requests

from app.utilities import set_interval
from multiprocessing import Pool
from bs4 import BeautifulSoup

from app.controller import Controller
bg_controller = Controller()

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
    watchList = bg_controller.get_stock_list()
    pool = Pool()
    latestStockData = pool.map(process_stock, watchList)
    pool.close()
    pool.join()
    for data in latestStockData:
        bg_controller.save_stock_update(data['_id'], data['updateData'])
        
def init_stock_check():
    set_interval(update_stock, 30 * 60)