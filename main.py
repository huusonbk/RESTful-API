from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import numpy as np

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record

@app.route("/random", methods=['GET', 'POST'])
def get_random():
    if request.method == 'GET':
        all_cafes = db.session.query(Cafe).all()
        get_cafe = random.choice(all_cafes)
        print(get_cafe)
        return jsonify(get_cafe.to_dict()
                       )


@app.route("/all", methods=['GET', 'POST'])
def get_all():
    if request.method == 'GET':
        all_cafes = db.session.query(Cafe).all()

        all_cafe_dict = {"cafes": [get_cafe.to_dict() for get_cafe in all_cafes]}

        return jsonify(all_cafe_dict)


@app.route("/search", methods=['GET', 'POST'])
def get_search():
    if request.method == 'GET':
        loc = request.args.get('loc')
        try:
            result = db.session.query(Cafe).filter_by(location=loc).first()
            print(result)
            return jsonify(result.to_dict())
        except:
            return jsonify({
                "error": {
                    "Not found": "Sorry we dont have a cafe at that location"
                }
            })


## HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add():
    try:
        if request.method == 'POST':
            # CREATE RECORD
            new_cafe = Cafe(
                name=request.form['name'],
                map_url=request.form['map_url'],
                img_url=request.form['img_url'],
                location=request.form['location'],
                seats=request.form['seats'],
                has_toilet=bool(request.form['has_toilet']),
                has_wifi=bool(request.form['has_wifi']),
                has_sockets=bool(request.form['has_sockets']),
                can_take_calls=bool(request.form['can_take_calls']),
                coffee_price=request.form['coffee_price'], )
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify({
                "response": {
                    "success": "Successfully to added new cafe"
                }
            })
    except:
        return jsonify({
            "error": {
                "Not response": "Sorry we cannot add this item"
            }
        })


## HTTP PUT/PATCH - Update Record


@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def edit(cafe_id):
    try:
        admin = Cafe.query.get(cafe_id)
        admin.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify({
            "response": {
                "success": "Successfully to added new cafe"
            }
        })
    except:
        return jsonify({
            "error": {
                "Not found": "Sorry we dont have a cafe at that location"
            }
        })


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    if request.args.get('API_key') == "sdz":
        try:
            admin = Cafe.query.get(cafe_id)
            db.session.delete(admin)
            db.session.commit()
            return jsonify({
                "response": {
                    "success": "Successfully to added new cafe"
                }
            })
        except:
            return jsonify({
                "error": {
                    "Not found": "Sorry we dont have a cafe at that location"
                }
            })
    else:
        return jsonify({
            "error": {
                "403": "Forbidden"
            }
        })


if __name__ == '__main__':
    app.run(debug=True)
