from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# ------------------ CONFIG ------------------
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3307/taskmanager"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Later use environment variable

# ------------------ EXTENSIONS ------------------
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ------------------ MODELS ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default="pending")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ------------------ ROUTES ------------------

# Root route for browser testing
@app.route("/")
def index():
    return "✅ Task Manager API is running!"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input provided"}), 400
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input provided"}), 400
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"message": "Task title is required"}), 400
    new_task = Task(title=data['title'], description=data.get('description', ''), user_id=current_user)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201

@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user).all()
    return jsonify([{"id": t.id, "title": t.title, "status": t.status} for t in tasks])

@app.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    current_user = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=current_user).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify({"message": "Task updated"})

@app.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    current_user = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=current_user).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

# ------------------ MAIN ------------------
if __name__ == "__main__":
    # ✅ Create tables inside app context
    with app.app_context():
        db.create_all()
    
    # Run the development server
    app.run(debug=True)
