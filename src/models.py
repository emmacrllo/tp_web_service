from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:root@10.4.247.242:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
fake = Faker()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(200))
    job = db.Column(db.String(100))

    def __init__(self, firstname, lastname, age, email, job):
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        self.email = email
        self.job = job

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appname = db.Column(db.String(100))
    username = db.Column(db.String(100))
    lastconnection = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, appname, username, lastconnection, user_id):
        self.appname = appname
        self.username = username
        self.lastconnection = lastconnection
        self.user_id = user_id

@app.route('/application', methods=['GET'])
def get_applications():
    applications = Application.query.all()
    application_data = []
    for app in applications:
        application_data.append({
            'id': app.id,
            'appname': app.appname,
            'username': app.username,
            'lastconnection': app.lastconnection.isoformat(),
            'user_id': app.user_id
        })
    return jsonify(application_data)

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'age': user.age,
            'email': user.email,
            'job': user.job
        })
    return jsonify(user_data)

def populate():
    with app.app_context():
        # Création de 100 utilisateurs factices
        for _ in range(100):
            firstname = fake.first_name()
            lastname = fake.last_name()
            age = random.randint(18, 50)
            email = fake.email()
            job = fake.job()
            user = User(firstname=firstname, lastname=lastname, age=age, email=email, job=job)
            db.session.add(user)

        # Création de 100 applications factices avec des utilisateurs associés
        apps = ["Facebook", "Instagram", "Snapchat", "TikTok", "X"]
        for _ in range(100):
            appname = random.choice(apps)
            username = fake.user_name()
            lastconnection = datetime.now()
            user = User.query.order_by(User.id).first()
            if user:
                application = Application(appname=appname, username=username, lastconnection=lastconnection, user_id=user.id)
                db.session.add(application)

        # Enregistrement des changements dans la base de données
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        # Création de toutes les tables définies dans les modèles
        #db.create_all()

        # Peupler les tables avec des données factices
        #populate()

        app.run(host="0.0.0.0", port=8081, debug=True)
