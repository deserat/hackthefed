import os
import calendar
import pymongo
import bson
import json
import csv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/congress-legislators/".format(APP_DIR)

db = pymongo.MongoClient("127.0.0.1", safe=True).congress

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









#  { 
#     "last_name": 
#     "first_name": 
#     "birthday": 
#     "gender": 
#     "type": 
#     "state": 
#     "party": 
#     "url": 
#     "address": 
#     "phone": 
#     "contact_form": 
#     "rss_url": 
#     "twitter": 
#     "facebook": 
#     "facebook_id": 
#     "youtube": 
#     "youtube_id": 
#     "bioguide_id": 
#     "thomas_id": 
#     "opensecrets_id": 
#     "lis_id": 
#     "cspan_id": 
#     "govtrack_id": 
#     "votesmart_id": 
#     "ballotpedia_id": 
#     "washington_post_id": 
#     "icpsr_id": 
#     "wikipedia_id":
# }