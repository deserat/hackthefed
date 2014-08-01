import os
import pymongo
import bson
import json
import csv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/us/crs_terms".format(APP_DIR)

from conf.vance import DB, DB_HOST, DB_USER, DB_PASS

db = pymongo.MongoClient(DB_HOST).congress

db.legislator.drop()
db.create_collection("legislator")

def process_legislators(terms):
    terms.next()
    


with open(DATA_DIR, 'rb') as csvfile:
    terms = csv.reader(csvfile) 
    terms.next()
    for t in terms:
        db.subject.insert( { "name" : t } )
