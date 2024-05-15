from sqlalchemy import create_engine, text
from flask import Flask, jsonify, request, abort
from faker import Faker
import random
from datetime import datetime

# Modifier la chaîne de connexion à la base de données PostgreSQL avec le nouvel utilisateur et son mot de passe
# Modifier la chaîne de connexion à la base de données PostgreSQL avec le nouvel utilisateur et son mot de passe
db_string = "postgresql://root:root@10.4.247.242:5432/postgres"

# Créer une instance de moteur SQLAlchemy
engine = create_engine(db_string)

app = Flask(__name__)

# Configuration de l'URI de la base de données PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = db_string

# Désactivation du suivi des modifications de la base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

fake = Faker()

# Créer la table user 
create_user_table_sql = """
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY ,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    age  INT,
    email VARCHAR(200),
    job VARCHAR(100)
)
"""
# Créer la table application
create_application_table_sql = """
CREATE TABLE IF NOT EXISTS applications(
    id SERIAL PRIMARY KEY ,
    appname VARCHAR(100),
    username VARCHAR(100),
    lastconnection TIMESTAMP WITH TIME ZONE,
    user_id INTEGER REFERENCES users(id)
)
"""

# Définir une fonction pour exécuter une requête SQL sans retour pour tout ce qui est de la création des tables ou de l'insertion des données 
def run_sql(query:str):
    with engine.connect() as connection:
        trans = connection.begin()  
        connection.execute(text(query))
        trans.commit()  

def run_sql_with_result(query:str):
    with engine.connect() as connection:
        trans = connection.begin()  
        result = connection.execute(text(query))
        trans.commit()  
        return result

def populate_tables():
    apps = ["Facebook", "Instagram", "Snapchat","TikTok","X"]
    for _ in range(100):
        firstname = fake.first_name()
        lastname = fake.last_name()
        age = random.randrange(18,50)
        email = fake.email()
        job = fake.job().replace("'","")
        insert_user_query = f"""   
        INSERT INTO users(firstname,lastname,age,email,job)
        VALUES ('{firstname}','{lastname}',{age},'{email}','{job}')
        RETURNING id
        """   
        user_id=run_sql_with_result(insert_user_query).scalar()
 
        apps_name = [random.choice(apps) for _ in range(1,random.randrange(1,5))]
        num_apps = random.randint(1,5)
        for i in range(num_apps):
            username = fake.user_name()
            lastconnection = datetime.now()
            appname = random.choice(apps)
            insert_applications_query = f"""   
            INSERT INTO applications(appname,username,lastconnection,user_id)
            VALUES ('{appname}','{username}','{lastconnection}','{user_id}')
            """   
            run_sql(insert_applications_query)

@app.route("/user", methods=["GET"])
def get_users():
    users = run_sql_with_result("SELECT * FROM users")
    data = []
    for row in users:
        user = {
            "id":row[0],
            "firstname":row[1],
            "lastname":row[2],
            "age":row[3],
            "email":row[4],
            "job":row[5]
        }
        data.append(user)
    return jsonify(data)


@app.route("/application", methods=["GET"])
def get_applications():
    applications = run_sql_with_result("SELECT * FROM applications")
    data = []
    for row in applications:
        application = {
            "id": row[0],
            "appname": row[1],
            "username": row[2],
            "lastconnection": row[3].strftime("%Y-%m-%d %H:%M:%S"),  # Conversion au format string
            "user_id": row[4]
        }
        data.append(application)
    return jsonify(data)

# Route pour créer un nouvel utilisateur
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    age = data.get('age')
    email = data.get('email')
    job = data.get('job')

    if not all([firstname, lastname, age, email, job]):
        abort(400, 'Missing required fields')

    # Insertion dans la base de données
    insert_user_query = f"""   
        INSERT INTO users(firstname,lastname,age,email,job)
        VALUES ('{firstname}','{lastname}',{age},'{email}','{job}')
        RETURNING id
    """
    user_id = run_sql_with_result(insert_user_query).scalar()

    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201

# Route pour mettre à jour un utilisateur existant
@app.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    age = data.get('age')
    email = data.get('email')
    job = data.get('job')

    if not all([firstname, lastname, age, email, job]):
        abort(400, 'Missing required fields')

    # Vérification de l'existence de l'utilisateur
    user_query = f"SELECT * FROM users WHERE id = {user_id}"
    existing_user = run_sql_with_result(user_query).fetchone()
    if not existing_user:
        abort(404, 'User not found')

    # Mise à jour de l'utilisateur dans la base de données
    update_user_query = f"""   
        UPDATE users
        SET firstname='{firstname}', lastname='{lastname}', age={age}, email='{email}', job='{job}'
        WHERE id = {user_id}
    """
    run_sql(update_user_query)

    return jsonify({'message': 'User updated successfully'}), 200

# Route pour supprimer un utilisateur
@app.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # Vérification de l'existence de l'utilisateur
    user_query = f"SELECT * FROM users WHERE id = {user_id}"
    existing_user = run_sql_with_result(user_query).fetchone()
    if not existing_user:
        abort(404, 'User not found')

    # Suppression de l'utilisateur de la base de données
    delete_user_query = f"DELETE FROM users WHERE id = {user_id}"
    run_sql(delete_user_query)

    return jsonify({'message': 'User deleted successfully'}), 200

# Exécuter les requêtes SQL pour créer les tables et remplir les tables
if __name__ == '__main__':
    #run_sql(create_user_table_sql)
    #run_sql(create_application_table_sql)
    #populate_tables()
    app.run(host="0.0.0.0", port=8081, debug=True)

