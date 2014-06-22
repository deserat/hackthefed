#
# Don't assume nothing smart from this file I'm just messing around with 
# the data files and getting to know them. Anything of value will go 
# elsewhere.
# 


import nltk
from nltk import bigrams
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import operator
import os
import calendar
import pymongo
import bson
import json

#
# Settings
#

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/113/bills/sres/".format(APP_DIR)


db = pymongo.Connection("127.0.0.1", safe=True).congress


# 
# Drop collections while we play
# 

db.congressman.drop()
db.create_collection("congressman")

db.states.drop()
db.create_collection("states")


# Loop over bills. Count and tally statistics on congressmen 
# for each peace of legislation.

for root, dirs, files in os.walk(DATA_DIR):
    if "data.json" in files:
        file_path = "{0}/data.json".format(root)
        rez = json.loads( open(file_path, 'r').read() )
        
        sponsor = rez.get('sponsor', None)



        # Check if the bill has a sponsor if so give 'em credit
        if sponsor:
            
            congressman = db.congressman.find_one({"thomas_id": sponsor['thomas_id']})

            db.states.update(
                { "name" : sponsor['state'] },
                { "$inc" : { "sponsor_count" : 1} },
                True,
                False
            )

            if not congressman:
                #  If the congressman doesn't exist we need to create them 
                # Add this resolution to the sponsered resolutions sub doc
                # incrment the sponsered count
                print "inserting"

                sponsor["sponsored_resolutions"] = [ 
                    {
                        "bill_id" : rez.get("bill_id", "NOID"),
                        "title": "NOTITLE"
                    }
                ]

                sponsor["sponsor_count"] = 1

                id =  db.congressman.insert(sponsor)

                print "Created congressman"
            else:
                print "updateing congressman"
                db.congressman.update(
                    {"thomas_id": sponsor['thomas_id'] },
                    {
                        "$inc" : { "sponsor_count" : 1},
                        "$push" : { "sponsored_resolutions": 
                            {
                                "bill_id" : rez.get("bill_id", "NOID"),
                                "title": rez.get("official_title", "TITLE") # make a fucntion that gets on of the titles
                            }
                        }
                    }
                )
                tmp = db.congressman.find_one({"thomas_id": sponsor['thomas_id']})
                print tmp["sponsor_count"]

        # Loop through all the cosponsors of a bill and give them each credit for the bills
        # they cosponsor

        for cosponsor in rez.get('cosponsors', ()):

            db.states.update(
                { "name" : cosponsor['state'] },
                { "$inc" : { "cosponsor_count" : 1 } },
                True,
                False
            )

            congressman = db.congressman.find_one({"thomas_id": sponsor['thomas_id']})
            if not congressman:
                #  If the congressman doesn't exist we need to create them 
                # Add this resolution to the sponsered resolutions sub doc
                # incrment the sponsered count
                print "inserting"

                cosponsor["cosponsored_resolutions"] = [ 
                    {
                        "bill_id" : rez.get("bill_id", "NOID"),
                        "title": "NOTITLE"
                    }
                ]

                cosponsor["cosponsored_count"] = 1

                id =  db.congressman.insert(cosponsor)

                print "Created congressman"
            else:
                print "updateing congressman"
                db.congressman.update(
                    {"thomas_id": cosponsor['thomas_id'] },
                    {
                        "$inc" : { "cosponsor_count" : 1},
                        "$push" : { "cosponsored_resolutions": 
                            {
                                "bill_id" : rez.get("bill_id", "NOID"),
                                "title": rez.get("official_title", "TITLE") # make a fucntion that gets on of the titles
                            }
                        }
                    }
                )
                tmp = db.congressman.find_one({"thomas_id": cosponsor['thomas_id']})
                print tmp["sponsor_count"]


# bigram_counts = {}

# stop_words = stopwords.words('english')


# stop_words = stop_words + [
#     "senate", "congress", "session", "113th", "u.s.","government",
#     "bill", "in", "the", "Res","office", "rule", "law","ats" ]

# stop_bigrams = ['people united', 'exceed 000', 'resolution considered',
#     'rules senate', 'standing rules', 'act u', 'whereas united', 'u c',
#     'senate 1st', 'res agreed', 'united states', 'senate united',
#     'congressional bills', 'printing res', 'u printing', 'bills u',
#     'submitted following', 'following resolution', 'therefore resolved',
#     '1st res', 'states whereas', 'resolved senate', '000 000', 'referred committee',
#     'resolution referred', 'senate ats']


# # very niaeve fix me
# for n in range(0,2015):
#     stop_words.append("{0}".format(n))


# # very niaeve fix me
# for n in range(1,12):
#     stop_words.append(calendar.month_name[n])

# bigram_strings = []





        # {
        #     "district": null, 
        #     "name": "Reid, Harry", 
        #     "state": "NV", 
        #     "thomas_id": "00952", 
        #     "title": "Sen", 
        #     "sponser_count" : 0,
        #     "sponsered_resolutions" : [
        #         {
        #             "id": "name"
        #             "title": "name"
        #         },
        #     ],
        #     "sponsered_bills" : [
        #         {
        #             "id": "name"
        #             "title": "name"
        #         },
        #     ],
        #     "sponsered_subjects" : {
        #         "Civil actions and liability" : 35,
        #         "Evidence and witnesses": 2,
        #     }

        # }, 





    # if "document.txt" in files:
    #     file_path = "{0}/document.txt".format(root)
    #     print file_path
    #     f = open(file_path, 'r')
    #     text = f.read()

    #     db.bigrams.update({})

    #     tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
    #     tokenized = tokenizer.tokenize(text)

    #     for b in bigrams([word.strip().lower() for word in tokenized if word.strip().lower() not in stop_words]):
    #         if '%s %s' % b not in stop_bigrams:
    #             bigram_strings.append(b)


# print "######## Counting Bigrams ###################"
# for bi in bigram_strings:
#     bi_key = '%s %s' % bi
#     if bi_key not in bigram_counts.keys():
#         bigram_counts[bi_key] = 1
#     else:
#         bigram_counts[bi_key] = bigram_counts[bi_key] + 1


# print "######## Sorting Bigrams ###################"
# sorted_bigrams = sorted(bigram_counts.iteritems(), key=operator.itemgetter(1),reverse=True)


# for i in range(0, 100):
#     print sorted_bigrams[i]
#     #print " {0} : {1} ".format(sorted_bigrams[i])