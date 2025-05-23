from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from datetime import datetime, timedelta
import csv
import io
import os
import pathlib
from detection_butor import detect_bird_call, calculer_tdoas, localiser_butor
from extraction_csv import lire_micros_depuis_csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'
memodir = pathlib.Path(__file__).parent

def init_micros():
    if 'micros' not in session:
        session['micros'] = []

def maj_butor():
    """
    Vérifie si le butor actif est trop vieux (>1 minutes).
    Si oui, le déplace dans l'historique et le supprime de la carte.
    """
    if 'butor' in session:
        detection = session['butor']
        detection_time = datetime.strptime(detection['timestamp'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - detection_time > timedelta(minutes=1):
            # Déplacement dans l'historique
            if 'observations' not in session:
                session['observations'] = []
            session['observations'].append({
                'date': detection['timestamp'],
                'latitude': detection['latitude'],
                'longitude': detection['longitude']
            })
            session.pop('butor')
            session.modified = True

@app.route('/')
def home():
    init_micros()
    maj_butor()
    return render_template('visualisation.html', micros=session['micros'], butor=session.get('butor'))

@app.route('/micros')
def micros():
    init_micros()
    return render_template('micros.html', micros=session['micros'])

@app.route('/manuel', methods=['GET', 'POST'])
def manuel():
    init_micros()
    if request.method == 'POST':
        latitudes = request.form.getlist('latitude')
        longitudes = request.form.getlist('longitude')
        for lat, lon in zip(latitudes, longitudes):
            session['micros'].append({
                'nom': f"Micro {len(session['micros']) + 1}",
                'latitude': float(lat),
                'longitude': float(lon)
            })
        session.modified = True
        return redirect(url_for('home'))
    return render_template('manuel.html')

@app.route('/csv', methods=['GET', 'POST'])
def csv_upload():
    init_micros()
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if file:
            micros_csv = lire_micros_depuis_csv(file, session['micros'])
            session['micros'].extend(micros_csv)
            session.modified = True
        return redirect(url_for('home'))
    return render_template('csv.html')

@app.route('/audio', methods=['GET', 'POST'])
def audio():
    import itertools
    import numpy as np

    init_micros()
    if request.method == 'POST':
        if len(session['micros']) < 3:
            flash("Au moins 3 micros nécessaires pour la localisation.")
            return redirect(url_for('audio'))
        
        t_arrivees = []
        upload_folder = memodir / "data/audio"
        os.makedirs(upload_folder, exist_ok=True)
    
        try:
            # Étape 1 : Sauvegarde des fichiers et détection
            for i, micro in enumerate(session['micros']):
                fichier = request.files.get(f'audio_{i}')
                if not fichier or not fichier.filename:
                    continue

                chemin_fichier = upload_folder / f"micro_{i}.wav"
                fichier.save(chemin_fichier)

                present, t, _ = detect_bird_call(str(chemin_fichier))
                if not present:
                    flash(f"Chant non détecté dans le fichier de {micro['nom']} ({fichier.filename})")
                    return redirect(url_for('audio'))

                t_arrivees.append(t)
                session['audio'] = session.get('audio', [])
                
                session['audio'].append({
                    'fichier': str(chemin_fichier),
                    'micro': session['micros'][i]
                })

            # Étape 2 : Calcul des positions par triplet
            micros = [session['audio'][i]['micro'] for i in range(len(session['audio']))]
            positions = []
            for triplet in itertools.combinations(range(len(micros)), 3):
                triplet_micros = [micros[i] for i in triplet]
                triplet_t = [t_arrivees[i] for i in triplet]
                tdoas = calculer_tdoas(triplet_t)
                result = localiser_butor(triplet_micros, tdoas)

                # Accepte tuple de 2 ou 3 valeurs
                if isinstance(result, (list, tuple)) and len(result) >= 2:
                    lat, lon = result[:2]
                    positions.append((lat, lon))

            if not positions:
                flash("Aucune position valide obtenue à partir des triplets.")
                return redirect(url_for('audio'))

            # Moyenne des positions
            lat_moy = round(np.mean([p[0] for p in positions]), 4)
            lon_moy = round(np.mean([p[1] for p in positions]), 4)

            session['butor'] = {
                'latitude': lat_moy,
                'longitude': lon_moy,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            session.modified = True
            flash("Localisation réussie (moyenne sur triplets)!")
            
        
            # Nettoyage de la session audio
            session.pop('audio', None)
            session.modified = True

            return redirect(url_for('visualisation'))

        except Exception as e:
            flash(f"Erreur lors de la détection/localisation : {e}")
            return redirect(url_for('audio'))

    return render_template('audio.html', micros=session['micros'])


@app.route('/visualisation')
def visualisation():
    init_micros()
    maj_butor()
    return render_template("visualisation.html", micros=session['micros'], butor=session.get('butor'))

@app.route('/audiotheque')
def audiotheque():
    init_micros()
    fichiers_audio = [f for f in os.listdir(memodir / "data/audio") if f.lower().endswith('.wav')]
    return render_template('audiotheque.html', fichiers=fichiers_audio)

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(memodir / "data/audio", filename)

@app.route('/delete_micro/<int:index>', methods=['POST'])
def delete_micro(index):
    init_micros()
    if 0 <= index < len(session['micros']):
        session['micros'].pop(index)
        session.modified = True
    return redirect(url_for('micros'))

@app.route('/historique')
def historique():
    init_micros()
    observations = session.get('observations', [])
    return render_template('historique.html', observations=observations)

@app.route('/delete_observation', methods=['POST'])
def delete_observation():
    observations = session.get('observations', [])
    selected = request.form.getlist('selected')
    selected_indexes = sorted([int(i) for i in selected], reverse=True)
    for idx in selected_indexes:
        if 0 <= idx < len(observations):
            observations.pop(idx)
    session['observations'] = observations
    session.modified = True
    return redirect(url_for('historique'))

if __name__ == '__main__':
    app.run(debug=True)
