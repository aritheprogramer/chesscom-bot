# ♟️ Chess.com Bot

Un bot Python automatisé qui joue sur Chess.com en utilisant le moteur Stockfish et une interface graphique moderne avec PyQt5.

---

## 🚀 Fonctionnalités

✅ Détection automatique des coups joués via Selenium  
✅ Calcul du meilleur coup avec Stockfish  
✅ Clic automatique sur l’échiquier (optionnel)  
✅ Calibration visuelle simple et sauvegardée automatiquement  
✅ Interface graphique claire et intuitive  
✅ Historique des coups affiché en temps réel

---

## 🛠️ Prérequis

- Python 3.7+
- Google Chrome
- Chromedriver compatible (https://chromedriver.chromium.org/downloads)
- Stockfish (fourni dans le dossier `stockfish/`)

---

## 📂 Structure du projet

```
chesscom-bot/
├── bot.py                 # Script principal
├── requirements.txt       # Dépendances Python
├── README.md              # Ce fichier
├── .gitignore             # Fichiers à ignorer
├── stockfish/             # Contient l'exécutable Stockfish
│   └── stockfish-mac      # Exemple pour MacOS
└── assets/                # (Optionnel) Logos, images
```

---

## 📦 Installation

1️⃣ Clonez le dépôt :
```
git clone https://github.com/votreutilisateur/chesscom-bot.git
```

2️⃣ Entrez dans le dossier :
```
cd chesscom-bot
```

3️⃣ Installez les dépendances :
```
pip install -r requirements.txt
```

4️⃣ Vérifiez que `chromedriver` est installé et disponible dans le PATH.

---

## ⚙️ Utilisation

1️⃣ Lancez le bot :
```
python bot.py
```

2️⃣ Ouvrez Chrome via l'interface (`Ouvrir Chrome`).

3️⃣ Connectez-vous sur [chess.com] et démarrez une partie.

4️⃣ Cliquez sur `Calibrer l’échiquier` :
- Placez la souris sur le coin supérieur gauche et validez.
- Placez la souris sur le coin inférieur droit et validez.

✅ La calibration est sauvegardée automatiquement et sera restaurée aux prochains lancements.

5️⃣ Choisissez votre couleur (`Blanc` ou `Noir`).

6️⃣ Cliquez sur `Démarrer le Bot`.

7️⃣ Pour arrêter le bot, cliquez sur `Arrêter le Bot`.

---

## 🧩 Options disponibles

- **Clic automatique** : active/désactive la saisie automatique du coup sur l’échiquier.
- **Délai** : nombre de secondes entre les vérifications du coup joué (par défaut 1s).

---

## 💾 Calibration

La calibration est stockée dans un fichier `calibration.txt` à la racine du projet :
```
x0,y0,square_width,square_height
```
Pour réinitialiser, supprimez ce fichier et relancez la calibration.

---

## ✨ Contribuer

Les contributions sont les bienvenues !  
Proposez une *issue* ou ouvrez une *pull request* si vous souhaitez apporter des améliorations.

