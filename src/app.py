from flask import Flask, render_template
import requests

app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/home')
def home():
    # Appel HTTP à notre API pour récupérer les informations sur les utilisateurs
    users_response = requests.get('http://localhost:8080/user')
    if users_response.status_code == 200:
        users = users_response.json()
        return render_template('home.html', users=users)
    else:
        return "Une erreur s'est produite lors de la récupération des données des utilisateurs."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
