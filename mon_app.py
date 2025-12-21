from flask import Flask,render_template,request
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/heure')
def heure():
    date_heure = datetime.datetime.now()
    h = date_heure.hour
    m = date_heure.minute
    s = date_heure.second
    return render_template('heure.html', heure=f"Heure actuelle : {h}h {m}m {s}s",hour=h,minute=m,seconde=s)
    # return render_template('heure.html', heure=f"Heure actuelle : {h}h {m}m {s}s")


liste_eleves=[
    {'nom':'Dupont','prenom':'Jean','age':20},
    {'nom':'Martin','prenom':'Sophie','age':22},
    {'nom':'Durand','prenom':'Paul','age':19},
    {'nom':'Bernard','prenom':'Marie','age':21}
]
@app.route('/eleves')
def eleve():
    age = request.args.get('age')
    eleves_selectionnes = [eleve for eleve in liste_eleves if str(eleve['age']) == age] if age else liste_eleves

    return render_template('eleves.html', eleves=liste_eleves,search = eleves_selectionnes)
 
if __name__ == '__main__':
    app.run(debug=True)