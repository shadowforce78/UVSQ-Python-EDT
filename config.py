import json
import os

# Définit le chemin du fichier de configuration dans le répertoire AppData de l'utilisateur
USER_APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'MonApp')  # Crée un sous-dossier 'MonApp' dans AppData
os.makedirs(USER_APPDATA_DIR, exist_ok=True)  # Crée le répertoire si il n'existe pas
CONFIG_FILE = os.path.join(USER_APPDATA_DIR, "user_config.json")  # Chemin complet du fichier de config

def load_config():
    """Charge la configuration depuis le fichier si elle existe, sinon retourne la configuration par défaut."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"class": "INF1-b2", "dark_mode": False}

def save_config(config):
    """Sauvegarde la configuration dans le fichier."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)  # Utilisation de l'indentation pour un format JSON plus lisible
