from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import pymongo

db = pymongo.Connection("127.0.0.1", safe=True).congress

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='I am a mnokey',
))


@app.route('/', methods=['GET'])
def show_congressmen():
    legislator = db.legislator.find()
    states = db.states.find()

    return render_template('index.html', legislator=legislator,states=states)


if __name__ == "__main__":
    app.run()