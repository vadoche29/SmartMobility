import os
import io
import csv

def lire_micros_depuis_csv(fichier, micros_existants=None):
    """
    Lit un fichier CSV et extrait les micros avec leurs coordonnées.
    """

    #Initialisation de la liste des micros
    micros = []

    # Vérification de l'encodage
    try:
        contenu = fichier.read().decode('windows-1252')
    except UnicodeDecodeError:
        fichier.seek(0)
        contenu = fichier.read().decode('utf-8-sig')

    # Lecture du contenu CSV
    flux = io.StringIO(contenu)
    lecteur = csv.reader(flux, delimiter=';')

    # Sauter l’en-tête
    next(lecteur, None)
    num_micro = len(micros_existants) + 1

    # Parcourir chaque ligne du CSV
    for ligne in lecteur:

        # Vérifier si la ligne est vide ou trop courte
        if len(ligne) < 3:
            continue

        # Récupérer le nom et les coordonnées
        
        # Récupérer le nom et les coordonnées
        if micros_existants is None:
            nom = ligne[0].strip()
            print(f"Nom du micro : {nom}")
        else:
            nom = f"Micro {num_micro}"
            num_micro += 1
        try:
            longitude = float(ligne[1].replace(',', '.'))
            latitude = float(ligne[2].replace(',', '.'))
            micros.append({
                "nom": nom,
                "longitude": longitude,
                "latitude": latitude
            })
        except ValueError:
            continue

    return micros