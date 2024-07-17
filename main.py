from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
import json

app = Flask(__name__)


API_KEY = "TopSecretAPIKey"


# CREATE DB
class Base(DeclarativeBase):
    pass

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def convert_instance_to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "amenities": {
                "seats": self.seats,
                "has_toilet": self.has_toilet,
                "has_wifi": self.has_wifi,
                "has_sockets": self.has_sockets,
                "can_take_calls": self.can_take_calls,
                "coffee_price": self.coffee_price,
            }
        }

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read a random Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    cafes = Cafe.query.all()
    if cafes:
        random_cafe = random.choice(cafes)
        return jsonify(random_cafe.convert_instance_to_dict())
    else:
        return jsonify({"error": "No cafes found"}), 404

# HTTP GET - GET ALLLLL Records:
@app.route("/all", methods=["GET"])
def get_all_cafes():
    all_cafes = Cafe.query.all()
    if all_cafes:
        cafes_list = [cafe.convert_instance_to_dict() for cafe in all_cafes]
        return jsonify(cafes=cafes_list)
    else:
        return jsonify({"error": "No cafes found"}), 404

# HTTP GET - Search Cafe by Location:
@app.route("/searchlocation", methods=["GET"])
def search_location():
    location_query = request.args.get('location')
    if location_query:
        cafes = Cafe.query.filter(Cafe.location.ilike(f"%{location_query}%")).all()
        if cafes:
            cafes_list = [cafe.convert_instance_to_dict() for cafe in cafes]
            return jsonify(cafes=cafes_list)
        else:
            return jsonify({"error": "No cafes found"}), 404
    else:
        return jsonify({"error": "Location parameter is missing"}), 400

# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    try:
        # Debug: Print the entire form data received
        print("Form data received:")
        print(request.form)

        # Extract and clean form data
        name = request.form.get("name\n").strip() if request.form.get("name\n") else None
        map_url = request.form.get("map_url\n").strip() if request.form.get("map_url\n") else None
        img_url = request.form.get("img_url").strip() if request.form.get("img_url") else None
        location = request.form.get("location").strip() if request.form.get("location") else None
        seats = request.form.get("seats").strip() if request.form.get("seats") else None
        has_toilet = request.form.get("has_toilet").strip() if request.form.get("has_toilet") else None
        has_wifi = request.form.get("has_wifi").strip() if request.form.get("has_wifi") else None
        has_sockets = request.form.get("has_sockets").strip() if request.form.get("has_sockets") else None
        can_take_calls = request.form.get("can_take_calls").strip() if request.form.get("can_take_calls") else None
        coffee_price = request.form.get("coffee_price").strip() if request.form.get("coffee_price") else None

        # Debug: Print extracted values
        print("Extracted values:")
        print(f"name: {name}, map_url: {map_url}, img_url: {img_url}, location: {location}")
        print(f"seats: {seats}, has_toilet: {has_toilet}, has_wifi: {has_wifi}, has_sockets: {has_sockets}")
        print(f"can_take_calls: {can_take_calls}, coffee_price: {coffee_price}")

        # Convert boolean values correctly
        has_toilet = json.loads(has_toilet.lower()) if has_toilet else False
        has_wifi = json.loads(has_wifi.lower()) if has_wifi else False
        has_sockets = json.loads(has_sockets.lower()) if has_sockets else False
        can_take_calls = json.loads(can_take_calls.lower()) if can_take_calls else False

        # Debug: Print converted boolean values
        print("Converted boolean values:")
        print(f"has_toilet: {has_toilet}, has_wifi: {has_wifi}, has_sockets: {has_sockets}, can_take_calls: {can_take_calls}")

        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            seats=seats,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            has_sockets=has_sockets,
            can_take_calls=can_take_calls,
            coffee_price=coffee_price
        )

        db.session.add(new_cafe)
        db.session.commit()

        print("New cafe added successfully")
        return jsonify(response={"success": "Cafe added successfully!!"}), 201
    except Exception as e:
        # Debug: Print the error message
        print("Error occurred:")
        print(str(e))
        # Return an error response if something goes wrong
        return jsonify(error={"error": str(e)}), 400




# PATCH:
@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    try:
        new_price = request.args.get("new_price")
        if new_price:
            cafe = Cafe.query.get(cafe_id)
            if cafe:
                old_price = cafe.coffee_price
                cafe.coffee_price = new_price
                db.session.commit()
                return jsonify(response={"success": f"Price successfully updated from {old_price} to {new_price} for cafe id {cafe_id}"}), 200
            else:
                return jsonify(error={"error": "Cafe not found"}), 404
        else:
            return jsonify(error={"error": "New price not provided"}), 400
    except Exception as e:
        return jsonify(error={"error": str(e)}), 400


# DELETE with API Key:
@app.route("/delete_cafe/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == API_KEY:
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": f"Cafe with id {cafe_id} Successfully deleted!!"}), 200
        else:
            return jsonify(error={"error": "Cafe not found"}), 404
    else:
        return jsonify(error={"error": "Unauthorized access"}), 403




if __name__ == '__main__':
    app.run(debug=True)
