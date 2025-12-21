from bson import ObjectId
from flask import Flask,render_template,request,jsonify,redirect,url_for,abort
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def connect_db():

    print(f"Tentative de connexion à MongoDB: {app.config['MONGO_URI']}")

    try:
        client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000, connectTimeoutMS=10000, socketTimeoutMS=45000)
        client.server_info()  # Force connection on a request as the
                              # connect=True parameter of MongoClient seems
                              # to be useless here

        client.admin.command('ping')
        print("Connexion à MongoDB réussie!")

        db_name = app.config['DB_NAME']
        db = client[db_name]

        collections = db.list_collection_names()
        print(f"Base de données '{db_name}' - Collections: {collections}")

        if "classes" not in collections:
            db.create_collection("classes")
            print("Collection 'classes' créée")


        if "etudiants" not in collections:
            db.create_collection("etudiants")
            print("Collection 'etudiants' créée")

        db.etudiants.create_index("classe_id")

        return db,client
    
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None
    
db,client = connect_db()

@app.route('/')
def home():
    return "Bienvenue dans l'application de gestion des étudiants!"


@app.route('/add_classe', methods=['GET', 'POST'])
def add_classe():
    if request.method == 'POST':
        code = request.form['code']
        nom = request.form['nom']
        niveau = request.form['niveau']
        description = request.form['description']
        classe = {
            "code": code,
            "nom": nom,
            "niveau": niveau,
            "description": description  
        }
        result = db.classes.insert_one(classe)
        return redirect(url_for("list_classes"))
    
    return render_template('add_classe.html')

@app.route('/classes')
def list_classes():
    classes = list(db.classes.find())
    return render_template('classes.html', classes=classes)

@app.route('/add_etudiant', methods=['GET', 'POST'])
def add_etudiant():
    classes = list(db.classes.find())

    if not classes:
        return "Aucune classe disponible. Veuillez ajouter une classe avant d'ajouter des étudiants."
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        age = int(request.form['age'])
        classe_id = request.form['classe_id']

        
        if not classe_id:
            abort(400, "Classe obligatoire")

        classe = db.classes.find_one(
            {"_id": ObjectId(classe_id)}
        )

        if not classe:
            abort(400, "Classe invalide")

        etudiant = {
                    "nom": nom,
                    "prenom": prenom,
                    "age": age,
                    "classe_id": ObjectId(classe_id)
                    }

        result = db.etudiants.insert_one(etudiant)
        return redirect(url_for("list_etudiants"))

    return render_template("add_etudiant.html", classes=classes)

@app.route("/etudiants")
def list_etudiants():
    etudiants = list(
        db.etudiants.aggregate([
            {
                "$lookup": {
                    "from": "classes",
                    "localField": "classe_id",
                    "foreignField": "_id",
                    "as": "classe"
                }
            }
        ])
    )

    return render_template(
        "etudiants.html",
        etudiants=etudiants
    )


if __name__ == '__main__':
    app.run(debug=True)