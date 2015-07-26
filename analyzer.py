# -*- coding: utf-8 -*-

# Note: Please make sure that the chiang-mai_thailand.osm.json
# is in the data directory before running this.

import json

AIRPORT_LAT = 18.767749
AIRPORT_LNG = 98.9640088

def count_document():
    return db.chiangmai.find().count()

def count_node():
    return db.chiangmai.find({ "type": "node" }).count()

def count_way():
    return db.chiangmai.find({ "type": "way" }).count()

def count_unique_users():
    result = db.chiangmai.aggregate([
        { "$group": { "_id": "users", "unique_users": { "$addToSet": "$created.user" } } },
        { "$unwind": "$unique_users" },
        { "$group": { "_id": "$_id", "count": { "$sum": 1 } } }
    ])
    for res in result: return res['count']

def count_shop():
    return db.chiangmai.find({ "shop": { "$exists": True } }).count()

def count_hospital():
    return db.chiangmai.find({ "amenity": "hospital" }).count()

def highest_contributor():
    result = db.chiangmai.aggregate([
        { "$group": { "_id": "users", "unique_users": { "$push": "$created.user" } } },
        { "$unwind": "$unique_users" },
        { "$group": { "_id": "$unique_users", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } },
        { "$limit": 1 }
    ])
    for res in result: return res["_id"]

def hotels_near_airport(km):
    db.chiangmai.ensure_index([("loc", "2dsphere")])
    result = db.chiangmai.find(
        {
            "tourism": "hotel",
            "loc":
            {
                "$near": {
                    "$geometry": { "type": "Point" , "coordinates": [AIRPORT_LNG, AIRPORT_LAT] },
                    "$maxDistance": km*1000
                }
            }
        },
        { "_id": 0, "name": 1, "loc.coordinates": 1}
    )

    return [res["name"] for res in result]

def process():
    print("Number of documents: {0}".format(count_document()))
    print("Number of nodes: {0}".format(count_node()))
    print("Number of ways: {0}".format(count_way()))
    print("Number of unique users: {0}".format(count_unique_users()))
    print("Number of shops: {0}".format(count_shop()))
    print("Number of hospitals: {0}".format(count_hospital()))
    print("Top 1 contributing user: {0}".format(highest_contributor()))
    print("Hotels near Chiang Mai internation airport within 2km: {0}".format(hotels_near_airport(2)))

def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.chiangmai

    return db

def load_data(file_path):
    with open(file_path, 'r') as f:
        for line in f.readlines():
            db.chiangmai.insert(json.loads(line))

if __name__ == "__main__":
    db = get_db()
    if db.chiangmai.find().count() == 0:
        load_data("data/chiang-mai_thailand.osm.json")

    process()