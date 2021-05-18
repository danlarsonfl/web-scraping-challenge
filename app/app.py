# Import libraries
from flask import Flask, render_template, redirect, jsonify, request, Response
from flask_pymongo import PyMongo
from bson.json_util import dumps
import scrape_mars

# Create Flask app
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'nasa_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/nasa_db'

# PyMongo for Mongo connection
mongo = PyMongo(app)


@app.route('/')
def getTemplate():
    data = mongo.db.data.find_one()
    return render_template('index.html', data=data)



@app.route('/scraper')
def scraper():
    data = mongo.db.data
    scrape_data = scrape_mars.scraper()
    data.update({}, scrape_data, upsert=True)
    return redirect('/', code=302)

if __name__ == "__main__":
    app.run(debug=True)
