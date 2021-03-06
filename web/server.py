
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import pymongo
import bson
import json

from conf.vance import DB, DB_HOST, DB_USER, DB_PASS


db = pymongo.MongoClient(DB_HOST, safe=True).congress

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='I am a mnokey',
))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/states', methods=['GET'])
def states():
    states = db.states.find().sort([("sponsor_count",pymongo.DESCENDING)])

    return render_template('states.html', states=states)


@app.route('/committees', methods=['GET'])
def committees():
    committees = db.committee.find().sort([("type",pymongo.ASCENDING)])

    return render_template('committees.html', committees=committees)

@app.route('/subjects/', methods=['GET'])
def subjects():
    subjects = db.subject.find({},{"name":1,"count":1,"top_count":1})

    return render_template('subjects.html', subjects=subjects)

@app.route('/subjects/<subject_id>/', methods=['GET'])
def subject(subject_id):
    subject = db.subject.find_one({"_id":bson.ObjectId(subject_id)})

    return render_template('subject_detail.html', subject=subject)

@app.route('/legislators/', methods=['GET'])
def legislators():
    legislators = db.legislator.find().sort([("sponsor_count",pymongo.DESCENDING)]) #.sort({ "sponser_count":1}).limit(10)

    return render_template('legislators.html', legislators=legislators)


@app.route('/congresses/', methods=['GET'])
def congresses():
    congresses = list(db.congress.find().sort([("name",pymongo.DESCENDING)]))
    d = []
    for c in congresses:
        c['id'] = str(c['_id'])
        del c['_id']
        d.append(c)

    return render_template('congresses.html', congresses=congresses,data=json.dumps(d) )


@app.route('/congresses.json', methods=['GET'])
def congresses_json():
    congresses = db.congress.find().sort([("name",pymongo.DESCENDING)])
    response = []

    # TODO: Write serializer once we figure out what common things need normalization
    # bson serialization of id is unacceptable.
    for c in congresses:
        c['id'] = str(c['_id'])
        del c['_id']
        response.append(c)
    
    return json.dumps(response)


if __name__ == "__main__":
    app.run()