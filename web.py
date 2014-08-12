from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import pymongo
import bson

from conf.vance import DB, DB_HOST, DB_USER, DB_PASS

db = pymongo.MongoClient(DB).congress

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

    states = db.states.find()

    return render_template('states.html', states=states)


@app.route('/committees', methods=['GET'])
def committees():

    committees = db.committee.find()

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
    legislators = db.legislator.find() #.sort({ "sponser_count":1}).limit(10)

    return render_template('legislators.html', legislators=legislators)


@app.route('/congresses/', methods=['GET'])
def congresses():
    congresses = db.congress.find().sort({ "name":1})

    return render_template('congresses.html', congresses=congresses)


if __name__ == "__main__":
    app.run()