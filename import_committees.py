import os
import pymongo
import bson
import json
import yaml

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/congress-legislators/".format(APP_DIR)

from conf.vance import DB, DB_HOST, DB_USER, DB_PASS

db = pymongo.MongoClient(DB_HOST).congress

db.committee.drop()
db.create_collection("committee")

def process_committees(committees):

    for c in committees:
        exists = db.committee.find_one({"thomas_id":c["thomas_id"]})
        if exists is not None: 
            # if it exists it has congresses and names so we need to append
            print "Exists"

            congresses = [ "{0}".format(congress) for congress in c['congresses'] ]
            names = [
                { "{0}".format(key) : c['names'][key] } for key in c['names']
            ] 

            db.committee.update(
                {"thomas_id":c["thomas_id"]},
                {
                    "$addToSet": { 
                        "congresses": { "$each": congresses } ,
                        "names": { "$each": names } 
                    }

                }
            )
        else:
            if 'congresses' in c:
                c['congresses'] = [ "{0}".format(congress) for congress in c['congresses'] ]
                c['names'] = [
                    { "{0}".format(key) : c['names'][key] } for key in c['names']
                ]    
                if "subcommittees" in c:
                    for sc in c["subcommittees"]:
                        sc['congresses'] = [ "{0}".format(congress) for congress in sc['congresses'] ]
                        sc['names'] = [
                            { "{0}".format(key) : sc['names'][key] } for key in sc['names']
                        ]    

            else:
                c['congresses'] = ["113"]
                c['names'] = [{"113": c["name"]}]
            

            db.committee.insert(c)


with open("{0}/committees-current.yaml".format(DATA_DIR), 'r') as stream:
    committees = yaml.load(stream) 
    process_committees(committees)  


with open("{0}/committees-historical.yaml".format(DATA_DIR), 'r') as stream:
    committees = yaml.load(stream) 
    process_committees(committees)   


db.subject.create_index("thomas_id")
