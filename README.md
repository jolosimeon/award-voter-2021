# Project Scientist

pls vote for twice on mama

### Prerequisites

1. Python 3.9.9
2. Twitch/Kakao Accounts linked to MAMA accounts (Gmail not working)

### Installing

1. Pull the latest branch
2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate
```
3. Install the requirements under requirements.txt using:
```
pip install -r requirements.txt
```
3.5. For Mac OS users, you can install the requirements the following to skip failing installations:
```
cat requirements.txt | xargs -n 1 pip install
```

### Running the Project
To run the project, enter:
```
python scientist.py
```

### Bundling the Project (Windows)
To create a .exe file for Windows, enter:
```
pyinstaller --onefile --noconsole --add-data="assets/icons/potion.ico;assets/icons/potion.ico" -i assets/icons/potion.ico scientist.py
```

### Bundling the Project (MacOS)
To create an .app file using MacOS, enter:
```
pyinstaller --onefile --noconsole --add-data="assets/icons/potion.icns:assets/icons/potion.icns" -i assets/icons/potion.icns scientist.py
```