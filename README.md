# 🏁 MK8DX 200cc Lounge Bot
This bot is the primary driver for all things related to the MK8DX 200cc Lounge leaderboard.
- Sign up on [mariokartcentral.com](https://www.mariokartcentral.com/)
- `/verify` your MKC identity 
- Gather for matches in the [Discord server](discord.gg/uR3rRzsjhk) using [MogiBot](https://255mp.github.io/)
- Submit match results
- View player stats on [200-lounge.com](https://200-lounge.com)

# Development Environment / Installation

## Discord Developer account

- Create a Discord Developer account on Discord's [web page](https://discord.com/developers/docs/) 
- Make a bot for you to develop with. Take note of the **token** for later use
- Turn on Developer Mode in your Discord client `Settings` -> `Advanced` -> `Developer Mode: ON`

## MySQL or MariaDB

Install one of these database solutions. Both should work.

### Windows

- [MySQL Community Server 8.0.36](https://dev.mysql.com/downloads/mysql/) download page

- [MariaDB](https://mariadb.org/download) download page

### Ubuntu/Debian

```bash
apt install mysql-server
```
or

```bash
apt install mariadb-server
```

## Install system packages

### Windows

- [Python](https://www.python.org/downloads/windows/) for Windows

- [ImageMagick](https://imagemagick.org/script/download.php) download page

### Ubuntu/Debian

```bash
apt install git, imagemagick, virtualenv, python3, python3-venv
```

## Fork & clone the repository

You know how to do this. I believe in you

## Create a virtual environment

Might not be necessary on Windows

```bash
cd 200-Bot
virtualenv venv
activate
```

## Install the project requirements

```bash
pip3 install -r requirements.txt
```

## Database user, schema, & permissions

- Create an account for the bot to access the database
- Use `localhost` or `127.0.0.1` if your database instance is locally hosted

```sql
CREATE USER '200-bot-dev'@'<HOSTNAME_YOURE_TESTING_FROM>' IDENTIFIED BY '<YOUR_PASSWORD_HERE>';
CREATE DATABASE lounge_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE, DROP on lounge_dev.* to '200-bot-dev'@'<HOSTNAME_YOURE_TESTING_FROM>';
FLUSH PRIVILEGES;
```

## Create local development database

*UNFINISHED* - Still writing unit tests and figuring out what minimum data is needed

Run this file: `/200-bot/sql/development_init.sql` on your db instance

## Update `constants.py`

Use the example

```
mv constants_example.py constants.py
echo "constants.py" >> .gitignore
```

*UNFINISHED* - Not sure if it is reasonable for people to set up their own server, or if all devs should be in the same test server. Have not decided yet. There are a lot of constants for channels and roles that would be cumbersome for someone to set up for themselves, but would also be a good experience to understand the context of the project.

Edit the file

```py
TOKEN = "" # bot token from earlier
BOT_ID = 0 # bot user id
LOUNGE = [] # guild id goes here
...
# DB config for Discord Bot
HOST = "localhost" # hostname/ip where your db instance is running
PASS = "" # db user password
USER = "200-bot-dev" # db username
DTB = "lounge_dev" # db name
```

## Run the bot

```
python3 main.py
```

# Pull Requests

- Keep changes small
- All unit tests must pass
- Will refine what my requirements over time

I am normally a solo developer, so I am not sure what collaboration will look like yet

# Credits
[Lorenzi Table Maker](https://github.com/hlorenzi/mk8d_ocr)

[mariokartcentral.com](https://www.mariokartcentral.com/)
