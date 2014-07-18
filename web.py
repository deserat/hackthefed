from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import pymongo
import bson

db = pymongo.MongoClient("127.0.0.1", safe=True).congress

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='I am a mnokey',
))


@app.route('/', methods=['GET'])
def show_congressmen():
    legislators = db.legislator.find({"sponsor_count":{"$gt":5}}) #.sort({ "sponser_count":1}).limit(10)
    states = db.states.find()

    return render_template('index.html', legislators=legislators,states=states)


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


if __name__ == "__main__":
    app.run()