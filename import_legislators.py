import os
import pymongo
import bson
import json
import csv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/congress-legislators/".format(APP_DIR)

from conf.vance import DB, DB_HOST, DB_USER, DB_PASS

db = pymongo.MongoClient(DB_HOST).congress

db.legislator.drop()
db.create_collection("legislator")

def process_legislators(legislators):
    headers = legislators.next()
    print headers

    while True:
        leg_dict = {}
        try :
            leg = legislators.next()
        except StopIteration:
            break

        for i in range(0, len(headers)):
            leg_dict[headers[i]] = leg[i]

        db.legislator.insert(leg_dict)


with open("{0}/legislators-historic.csv".format(DATA_DIR), 'rb') as csvfile:
    legislators = csv.reader(csvfile) 
    process_legislators(legislators)  


with open("{0}/legislators-current.csv".format(DATA_DIR), 'rb') as csvfile:
    legislators = csv.reader(csvfile) 
    process_legislators(legislators)    

db.legislator.create_index({"thomas_id":1})