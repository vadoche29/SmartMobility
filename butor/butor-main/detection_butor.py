import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.optimize import least_squares
import numpy as np
from scipy.io import wavfile

def bandpass_filter(signal, sr, lowcut=100, highcut=300, order=4):
    nyq = 0.5 * sr
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    filtered = filtfilt(b, a, signal)
    return filtered

def reduce_noise(y, sr):
    frame_length = 2048
    hop_length = 512
    energy = np.array([
        np.sum(np.abs(y[i:i+frame_length])**2)
        for i in range(0, len(y) - frame_length, hop_length)
    ])
    threshold = np.percentile(energy, 25)
    # Créer un mask par frame
    mask_frames = energy > threshold
    # Répéter chaque frame hop_length fois
    mask = np.repeat(mask_frames, hop_length)
    # Ajuster la taille du mask à la taille exacte de y
    if len(mask) < len(y):
        mask = np.pad(mask, (0, len(y) - len(mask)), mode='constant')
    elif len(mask) > len(y):
        mask = mask[:len(y)]
    return y * mask


def detect_bird_call(file_path, min_gap=0.1, max_gap=0.7):
    y, sr = librosa.load(file_path, sr=44100)
    y = bandpass_filter(y, sr)
    y = reduce_noise(y, sr)
    frame_length = 2048
    hop_length = 512
    energy = np.array([
        np.sum(np.abs(y[i:i+frame_length])**2)
        for i in range(0, len(y) - frame_length, hop_length)
    ])
    threshold = 0.01 * np.max(energy)
    indices = np.where(energy > threshold)[0]
    #if len(indices) == 0:
    #    return False, None, None
    #t_detect = indices[0] * hop_length / sr
    #return True, t_detect, None
    if len(indices) < 2:
        return False, None, None

    # Chercher deux pics consécutifs séparés par un silence court
    times = indices * hop_length / sr
    for i in range(len(times) - 1):
        gap = times[i+1] - times[i]
        if min_gap <= gap <= max_gap:
            t_detect = times[i]
            return True, t_detect, None

    return False, None, None

def calculer_tdoas(t_arrivees):
    # Calcule les différences de temps d'arrivée relatives au premier micro
    t0 = t_arrivees[0]
    return [t - t0 for t in t_arrivees[1:]]

def localiser_butor(micros, tdoas, vitesse_son=340.29):
    def latlon_to_xy(lat, lon, lat0, lon0):
        R = 6371000  # rayon Terre en mètres
        x = R * np.radians(lon - lon0) * np.cos(np.radians(lat0))
        y = R * np.radians(lat - lat0)
        return x, y

    lat0, lon0 = micros[0]['latitude'], micros[0]['longitude']
    coords = [latlon_to_xy(m['latitude'], m['longitude'], lat0, lon0) for m in micros]

    # Fonction d'erreur : différences entre distances calculées et celles dues aux TDOA
    def residuals(p):
        x, y = p
        res = []
        x0, y0 = coords[0]
        for i in range(1, len(coords)):
            xi, yi = coords[i]
            d_calc = np.sqrt((x - xi)**2 + (y - yi)**2) - np.sqrt((x - x0)**2 + (y - y0)**2)
            d_meas = vitesse_son * tdoas[i-1]
            res.append(d_calc - d_meas)
        return res

    # Estimation initiale : position du premier micro
    x0, y0 = coords[0]
    result = least_squares(residuals, x0=[x0, y0])

    if not result.success:
        return None

    x_res, y_res = result.x

    # Reconvertir xy en lat/lon
    lat_res = lat0 + np.degrees(y_res / 6371000)
    lon_res = lon0 + np.degrees(x_res / (6371000 * np.cos(np.radians(lat0))))
    return lat_res, lon_res

def analyser_micros(micros):
    # Pour info, renvoie liste noms, latitudes, longitudes
    noms = [m.get('nom', f"Micro {i+1}") for i,m in enumerate(micros)]
    latitudes = [m['latitude'] for m in micros]
    longitudes = [m['longitude'] for m in micros]
    return noms, latitudes, longitudes

# --- Fonctions de debug/visualisation ---

def plot_spectrogram(y, sr, title):
    plt.figure(figsize=(10,4))
    S = librosa.stft(y)
    D = librosa.amplitude_to_db(np.abs(S), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.ylim(0, 1000)
    plt.tight_layout()
    plt.show()

def test_analyse_fichier(path_wav):
    print(f"Analyse fichier : {path_wav}")
    y, sr = librosa.load(path_wav, sr=44100)

    plot_spectrogram(y, sr, "Spectrogramme brut")

    y_filt = bandpass_filter(y, sr)
    plot_spectrogram(y_filt, sr, "Spectrogramme filtré (100-500 Hz)")

    y_clean = reduce_noise(y_filt, sr)
    plot_spectrogram(y_clean, sr, "Spectrogramme nettoyé")

    detecte, t, _ = detect_bird_call(path_wav)
    if detecte:
        print(f"Chant détecté à {t:.2f} s")
    else:
        print("Chant non détecté")

def calculer_snr(wav_path, t_bruit=(0, 0.5), t_signal=(1.0, 2.0)):
    fs, audio = wavfile.read(wav_path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)  # convertir en mono

    bruit = audio[int(t_bruit[0]*fs):int(t_bruit[1]*fs)]
    signal = audio[int(t_signal[0]*fs):int(t_signal[1]*fs)]

    p_bruit = np.mean(bruit**2)
    p_signal = np.mean(signal**2)

    if p_bruit == 0:
        return float('inf')

    return 10 * np.log10(p_signal / p_bruit)