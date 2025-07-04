# ♟️ Chess.com Bot

A Python automated bot that plays on Chess.com using the Stockfish engine and a modern graphical interface built with PyQt5.

---

## 🚀 Features

✅ Automatic detection of moves played via Selenium  
✅ Best move calculation with Stockfish  
✅ Optional automatic clicking on the chessboard  
✅ Simple visual calibration saved automatically  
✅ Clear and intuitive graphical interface  
✅ Real-time display of move history

---

## 🛠️ Requirements

- Python 3.7+
- Google Chrome
- Compatible Chromedriver (https://chromedriver.chromium.org/downloads)
- Stockfish (provided in the `stockfish/` folder)

---

## ⚠️ Chromedriver

This project requires `chromedriver`.  
Please download the version matching your installed Chrome here:

https://chromedriver.chromium.org/downloads

Then, place the executable either in your system PATH or in the project folder.

---

## 📂 Project Structure

```
chesscom-bot/
├── bot.py                 # Main script
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Ignored files
├── stockfish/             # Contains the Stockfish executable
    └── stockfish-mac      # Example for macOS
```

---

## 📦 Installation

1️⃣ Clone the repository:
```
git clone https://github.com/aritheprogramer/chesscom-bot.git
```

2️⃣ Enter the directory:
```
cd chesscom-bot
```

3️⃣ Install dependencies:
```
pip install -r requirements.txt
```

4️⃣ Make sure `chromedriver` is installed and available in your PATH.

---

## ⚙️ Usage

1️⃣ Launch the bot:
```
python bot.py
```

2️⃣ Open Chrome via the interface (`Open Chrome`).

3️⃣ Log in to [chess.com](https://www.chess.com/play/computer) and start a game.

4️⃣ Click `Calibrate Board`:
- Place the mouse over the top-left corner and confirm.
- Place the mouse over the bottom-right corner and confirm.

✅ The calibration is saved automatically and will be restored in future sessions.

5️⃣ Choose your color (`White` or `Black`).

6️⃣ Click `Start Bot`.

7️⃣ To stop the bot, click `Stop Bot`.

---

## 🧩 Available Options

- **Auto-click**: enable or disable automatic move input on the board.
- **Delay**: number of seconds between move checks (default: 1s).

---

## 💾 Calibration

The calibration is stored in a `calibration.txt` file at the project root:
```
x0,y0,square_width,square_height
```
To reset, delete this file and re-run the calibration process.

---

## ✨ Contributing

Contributions are welcome!  
Feel free to open an *issue* or submit a *pull request* if you would like to improve the project.

---

## 🖥️ Disclaimer and Support

This project was developed and tested on **macOS** and has **not been tested on other platforms**.  
The program itself is in **French 🇫🇷**, I may do a language update in the future.
If you encounter any issues or bugs, please open an issue on the [GitHub repository](https://github.com/aritheprogramer/chesscom-bot) to report them.

---
