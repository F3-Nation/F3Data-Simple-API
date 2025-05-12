import os
from flask import Flask, jsonify
from models import db, Org, Event
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
db.init_app(app)
print("Database initialized")

@app.route('/', methods=['GET'])
def index():
    return jsonify(message="Welcome to the VERY simple F3 Data API!")

@app.route('/regions/count', methods=['GET'])
def count_regions():
    count = Org.query.filter_by(org_type='region').count()
    return jsonify(count=count)

@app.route('/weeklyworkouts/count', methods=['GET'])
def count_weekly_workouts():
    count = Event.query.count()
    return jsonify(count=count)

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 8080)))
