# Import statements and necessary modules
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
<<<<<<< Updated upstream
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from tensorflow.keras.models import load_model

=======
from sqlalchemy import desc
>>>>>>> Stashed changes

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure app settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
jwt = JWTManager(app)

# Models
class RefCategorie(db.Model):
    __tablename__ = 'ref_categorie'
    id_cat = db.Column(db.BigInteger, primary_key=True)
    categorie = db.Column(db.String(255))
    max_ph = db.Column(db.Integer)
    min_ph = db.Column(db.Integer)
    max_temp = db.Column(db.Integer)
    min_temp = db.Column(db.Integer)

class Aquarium(db.Model):
    __tablename__ = 'aquarium'
    aquarium_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100))
    state = db.Column(db.String(100))
    max_ph = db.Column(db.Integer)
    min_ph = db.Column(db.Integer)
    max_temp = db.Column(db.Integer)
    min_temp = db.Column(db.Integer)
    nb_fish = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur.user_id'))

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'
    user_id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Fish(db.Model):
    __tablename__ = 'fish'
    id_fish = db.Column(db.BigInteger, primary_key=True)
    id_cat = db.Column(db.Integer, db.ForeignKey('ref_categorie.id_cat'))
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur.user_id'))

class AquaData(db.Model):
    __tablename__ = 'aquadata'
    id = db.Column(db.BigInteger, primary_key=True)
    ph = db.Column(db.Float)
    temperature = db.Column(db.Float)
    luminosity = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    moment = db.Column(db.DateTime)
    aquarium_id = db.Column(db.Integer, db.ForeignKey('aquarium.aquarium_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur.user_id'))

# Routes
@app.route('/auth/register/', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if Utilisateur.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    new_user = Utilisateur(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 200

@app.route('/auth/login/', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Utilisateur.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.email)
        return jsonify(access_token=access_token, username=user.username, user_id=user.user_id), 200

    return jsonify({"msg": "Bad email or password"}), 401

@app.route('/test/', methods=['GET'])
def test():
    return "test"

@app.route('/fish/all', methods=['GET'])
@jwt_required()
def get_all_fish():
    user_id = get_jwt_identity()
    fishes = Fish.query.filter_by(user_id=user_id).all()
    fish_list = [{"id_fish": fish.id_fish, "name": fish.name} for fish in fishes]
    return jsonify(fish_list), 200

@app.route('/cat/all', methods=['GET'])
@jwt_required()
def get_all_cat():
    categories = RefCategorie.query.all()
    cat_list = [{"id_cat": cat.id_cat, "categorie": cat.categorie} for cat in categories]
    return jsonify(cat_list), 200

@app.route('/aqu/creation/', methods=['POST'])
@jwt_required()
def aquarium_fish_creation():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = Utilisateur.query.filter_by(email=current_user).first()
    
    aquarium_name = data.get('aquarium_name')
    fish_data = data.get('fish_data', [])
    
    if not aquarium_name or not fish_data:
        return jsonify({"msg": "Aquarium name and fish data are required"}), 400
    
    new_aquarium = Aquarium(name=aquarium_name, user_id=user.user_id)
    db.session.add(new_aquarium)
    db.session.commit()
    
    for fish in fish_data:
        id_cat = fish.get('id_cat')
        new_fish = Fish(id_cat=id_cat, user_id=user.user_id)
        db.session.add(new_fish)
    
    db.session.commit()
    
    return jsonify({"msg": "Aquarium and fish created successfully"}), 201


@app.route('/aqu/get', methods=['POST'])
@jwt_required()
def get_aquarium_user():
    data = request.get_json()
    user_id = data.get('user_id')

    aquarium = Aquarium.query.filter_by(user_id=user_id).first()

    if not aquarium:
        return jsonify(None)

    return jsonify({
        'name': aquarium.name,
        'user_id': aquarium.user_id,
        'state': aquarium.state,
        'max_ph': aquarium.max_ph,
        'min_ph': aquarium.min_ph,
        'max_temp': aquarium.max_temp,
        'min_temp': aquarium.min_temp,
        'nb_fish': aquarium.nb_fish
    }), 200



@app.route('/chart/aquadata', methods=['GET'])
@jwt_required()
def get_aquadata_for_charts():
    user_email = get_jwt_identity()
    user = Utilisateur.query.filter_by(email=user_email).first()

    seven_days_ago = datetime.utcnow() - timedelta(days=9)
    aquadata_records = AquaData.query.filter(AquaData.user_id == user.user_id, AquaData.moment >= seven_days_ago).all()

    if not aquadata_records:
        return jsonify({}), 200

    data_by_day = defaultdict(lambda: {"ph": [], "temp": []})

    for record in aquadata_records:
        day = record.moment.date()
        data_by_day[day]["ph"].append(record.ph)
        data_by_day[day]["temp"].append(record.temperature)

    sorted_days = sorted(data_by_day.keys())

    labels = [day.strftime("%m-%d") for day in sorted_days]
    data_ph = [data_by_day[day]["ph"][0] for day in sorted_days]  # Assuming one entry per day for simplicity
    data_temp = [data_by_day[day]["temp"][0] for day in sorted_days]  # Assuming one entry per day for simplicity

    response_data = {
        "data_ph": {
            "labels": labels,
            "datasets": [
                {
                    "data": data_ph,
                }
            ],
        },
        "data_temperature": {
            "labels": labels,
            "datasets": [
                {
                    "data": data_temp,
                }
            ],
        },
    }

    return jsonify(response_data), 200

#IA

def predict_water_change_day(model, scaler, recent_data, seq_length=10, threshold=0.5):
    features = ['pH', 'temperature', 'luminosity', 'turbidity']
    
    recent_data_scaled = scaler.transform(recent_data[features])
    
    if len(recent_data_scaled) < seq_length:
        raise ValueError(f"La longueur des données récentes est insuffisante. Attendu au moins {seq_length} jours.")
    
    recent_sequence = recent_data_scaled[-seq_length:]
    recent_sequence = np.array([recent_sequence])
    
    predictions = model.predict(recent_sequence)
    print(predictions)
    water_change_day = np.argmax(predictions <= threshold)
    print(water_change_day)
    
    if water_change_day == 0:
        return "Aujourd'hui"
    elif water_change_day == 1:
        return "Demain"
    else:
        return f'Dans {water_change_day} jours'
    

<<<<<<< Updated upstream
@app.route('/ia/predict/', methods=['GET'])
=======
@app.route('/card/aquadata', methods=['GET'])
@jwt_required()
def get_aquadata_for_card():
    user_email = get_jwt_identity()
    user = Utilisateur.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({})

    # Get the last two records for the user
    aquadata_records = AquaData.query.filter_by(user_id=user.user_id).order_by(desc(AquaData.moment)).limit(2).all()

    if len(aquadata_records) < 2:
        return jsonify({})

    # The most recent record
    latest_record = aquadata_records[0]
    # The second most recent record
    previous_record = aquadata_records[1]

    # Calculate percentage difference
    def calculate_difference(new_value, old_value):
        if old_value == 0:
            return 0.0
        return round(((new_value - old_value) / old_value) * 100, 1)

    ph_difference = calculate_difference(latest_record.ph, previous_record.ph)
    temp_difference = calculate_difference(latest_record.temperature, previous_record.temperature)

    response_data = {
        "ph": {
            "last_value": latest_record.ph,
            "update_date": latest_record.moment.strftime("%d/%m/%Y"),
            "difference_j1": ph_difference
        },
        "temperature": {
            "last_value": latest_record.temperature,
            "update_date": latest_record.moment.strftime("%d/%m/%Y"),
            "difference_j1": temp_difference
        }
    }

    return jsonify(response_data), 200




@app.route('/routes/protected/', methods=['GET'])
>>>>>>> Stashed changes
@jwt_required()
def activate_prediction():
    aquadata = AquaData.query.all()

    df = pd.DataFrame([(data.moment, data.temperature, data.ph) for data in aquadata],
                          columns=['pH', 'temperature', 'luminosity', 'turbidity'])
        
    model = load_model('aquarium_model.h5')
    scaler = joblib.load('scaler.pkl')
    
    try:
        prediction = predict_water_change_day(model, scaler, df)
        res = f"Jour estimé pour changer l'eau : {prediction}"
    except ValueError as e:
        print(e)
    
    return jsonify(res), 200


# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
