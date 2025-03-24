#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    return jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers])

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)
    if camper:
        return jsonify(camper.to_dict())
    else:
        return jsonify({"error": "Camper not found"}), 404
    

@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            camper.name = data['name']
        if 'age' in data:
            camper.age = data['age']
            
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 202  # Tests expect 200
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400  # Match expected format
    
@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    
    try:
        camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
    
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 201
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400
    

@app.route('/activities', methods=['GET'])  # Changed from '/activity' to '/activities'
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities])

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    try:
        db.session.delete(activity)
        db.session.commit()
        return "", 204  # Successful deletion returns 204 No Content
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    
    try:
        # Get camper and activity
        camper = Camper.query.get(data.get('camper_id'))
        activity = Activity.query.get(data.get('activity_id'))
        
        if not camper or not activity:
            return jsonify({"errors": ["validation errors"]}), 400
        
        # Create signup
        signup = Signup(
            time=data.get('time'),
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id')
        )
    
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)