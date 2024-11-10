# Steps to Run

## 1. Clone the repository
Run the following commands to clone the repository:
```bash
git clone https://github.com/lighterbird/AR_AirHockey.git
```

## 2. Setup conda environment
Using conda setup the environment using the following commands/
```bash
cd AR_AirHockey
conda env create -f environment.yml
conda activate AirHockey
```

## 3. Run the Server
Run the flask server to start the game, using the following commands:
```bash
python server.py
```

## 4. Join as a player from other devices
Send the link provided by flask (in terminal on starting the server) to other devices for them to join
