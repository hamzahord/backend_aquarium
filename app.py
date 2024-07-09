# Import statements and necessary modules
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

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
    name = db.Column(db.String(255))
    id_cat = db.Column(db.Integer, db.ForeignKey('ref_categorie.id_cat'))
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur.user_id'))

class AquaData(db.Model):
    __tablename__ = 'aquadata'
    id = db.Column(db.BigInteger, primary_key=True)
    ph = db.Column(db.Float)
    temperature = db.Column(db.Float)
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
        return jsonify(access_token=access_token, username=user.username), 200

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

@app.route('/aqu/creation', methods=['POST'])
def aquarium_creation():
    data = request.get_json()
    # Implement aquarium creation logic here
    return jsonify({"msg": "Aquarium created successfully"}), 200



@app.route('/routes/protected/', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)