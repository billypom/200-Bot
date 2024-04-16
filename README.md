# 🏁 MK8DX 200cc Lounge Bot
This bot is the primary driver for all things related to the MK8DX 200cc Lounge leaderboard.
- Sign up on [mariokartcentral.com](https://www.mariokartcentral.com/)
- `/verify` your MKC identity 
- Gather for matches in the [Discord server](discord.gg/uR3rRzsjhk) using [MogiBot](https://255mp.github.io/)
- Submit match results
- View player stats on [200-lounge.com](https://200-lounge.com), or use the commands below.

# Developers
Install system packages
```bash
sudo apt install imagemagick, virtualenv, python3, python3-venv
```
Clone the repo
```bash
git clone https://github.com/billypom/200-Bot
```
Create a virtual environment [optional]
You may choose not to do this if you are running Windows or some other operating system that handles global python packages for you
```bash
cd 200-Bot
virtualenv venv
activate
```
Install the project requirements
```bash
pip install -r requirements.txt
```
Create the database and insert the test data
```
instructions coming soon...
```
Fill in the config.py file with information from your development Discord server, local database, and Bot config
I may open up my dev server for all developers, since the config is very verbose
```
instructions coming soon...
```
Run the bot
```
python3 main.py
```

I strongly suggest using pyright and ruff as LSP/linter

# Credits
[Lorenzi Table Maker](https://github.com/hlorenzi/mk8d_ocr)
[150cc Lounge API](https://github.com/VikeMK/Lounge-API)
[mariokartcentral.com](https://www.mariokartcentral.com/)
