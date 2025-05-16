import requests
import os

# URL officielle du fichier Lottie
url = "https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"

# Chemin de destination
destination_dir = "app/static/js"
destination_file = os.path.join(destination_dir, "lottie-player.js")

# Crée les dossiers s'ils n'existent pas
os.makedirs(destination_dir, exist_ok=True)

# Téléchargement
try:
    print("Téléchargement en cours...")
    response = requests.get(url)
    response.raise_for_status()  # Lève une exception si le téléchargement échoue

    with open(destination_file, "wb") as f:
        f.write(response.content)

    print(f"✅ Fichier téléchargé avec succès dans {destination_file}")
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur pendant le téléchargement : {e}")
