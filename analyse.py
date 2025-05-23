import os
import librosa
import numpy as np
import pandas as pd

def extract_features(file_path, n_mfcc=13):
    """Extrait les MFCCs d'un fichier audio."""
    try:
        y, sr = librosa.load(file_path, sr=None)  # Charge l'audio
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)  # Calcule les MFCCs
        return np.mean(mfccs, axis=1)  # Retourne la moyenne des MFCCs
    except Exception as e:
        print(f"Erreur avec {file_path}: {e}")
        return None

def prepare_dataset(directory, label):
    """Prépare les données pour un dossier donné."""
    features, labels = [], []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if file_name.endswith(".wav"):
            data = extract_features(file_path)
            if data is not None:
                features.append(data)
                labels.append(label)
    return features, labels

# Préparer les données
butor_features, butor_labels = prepare_dataset(r"I:\Cours M2\Projet Butor Étoilé\butor sons chanteur RNNES 2019\BUTOR_negatifs", 1)
autres_features, autres_labels = prepare_dataset(r"I:\Cours M2\Projet Butor Étoilé\butor sons chanteur RNNES 2019\BUTOR_positifs", 0)

# Combinez les données
X = np.array(butor_features + autres_features)
y = np.array(butor_labels + autres_labels)


from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = SVC(kernel='linear', probability=True)
model.fit(X_train, y_train)

# Évaluer le modèle
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(classification_report(y_test, y_pred))

