import os
from pymongo import MongoClient
from bson.objectid import ObjectId


class Controller:
    def __init__(self):
        db_url = os.environ.get('DB_URL', 'mongodb://localhost:27017')
        self.client = MongoClient(db_url)
        db = self.client['HMT-stock']
        self.stockDataTable = db['stock_data']
        self.userDataTable = db['user_data']

    def get_stock_status_for_user(self, userId):
        if (userId == '-1'):
            return []
        user = self.userDataTable.find_one({'_id': ObjectId(userId)})
        if (user != None):
            watchList = []
            for watchId in user['watchIdList']:
                watch = self.stockDataTable.find_one(
                    {'_id': ObjectId(watchId)})
                if (watch != None):
                    watchList.append(watch)
            return watchList
        else:
            return []

    def add_watch_for_user(self, userId, watchId):
        if (userId == '-1'):
            insertObject = self.userDataTable.insert_one(
                {'watchIdList': [watchId]})
            return str(insertObject.inserted_id)
        else:
            user = self.userDataTable.find_one({'_id': ObjectId(userId)})
            if (user == None):
                user = {'_id': ObjectId(userId), 'watchIdList': []}
                self.userDataTable.insert_one(
                    user)
            if (watchId not in user['watchIdList']):
                user['watchIdList'].append(watchId)
                self.userDataTable.update_one(
                    {'_id': ObjectId(userId)}, {'$set': {'watchIdList': user['watchIdList']}})
            return userId

    def find_watch(self, watchId):
        watch = self.stockDataTable.find_one({'watchId': watchId})
        if (watch != None):
            return str(watch['_id'])
        else:
            return None

    def add_watch(self, data):
        insertObject = self.stockDataTable.insert_one(data)
        return str(insertObject.inserted_id)

    def get_stock_list(self):
        return self.stockDataTable.find()

    def save_stock_update(self, watchId, data):
        self.stockDataTable.update_one(
            {'_id': ObjectId(watchId)}, {'$set': data})

    def get_availability_count_for_user(self, userId):
        if (userId == '-1'):
            return '0'
        user = self.userDataTable.find_one({'_id': ObjectId(userId)})
        if (user != None):
            availabilityCount = 0
            for watchId in user['watchIdList']:
                watch = self.stockDataTable.find_one(
                    {'_id': ObjectId(watchId)})
                if (watch != None and watch['inStock'] == True):
                    availabilityCount += 1
            return str(availabilityCount)
        else:
            return '0'
