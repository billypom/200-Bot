# 🏁 MK8DX 200cc Lounge Bot
This bot is the primary driver for all things related to the MK8DX 200cc Lounge leaderboard.
- Sign up on [mariokartcentral.com](https://www.mariokartcentral.com/)
- `/verify` your MKC identity 
- Gather for matches in the [Discord server](discord.gg/uR3rRzsjhk) using [MogiBot](https://255mp.github.io/)
- Submit match results
- View player stats on [200-lounge.com](https://200-lounge.com), or use the commands below.

# Development Environment / Installation

## [Create a Discord Developer account](https://discord.com/developers/docs/)

Create a Discord Developer account on Discord's [web page](https://discord.com/developers/docs/) and create a bot for you to develop with. Take note of the token for later use

## Install MySQL Community Server 8.0.36 or MariaDB

### Ubuntu/Debian

- Install MySQL
```bash
apt install mysql-server
```

or

- Install MariaDB

```bash
apt install mariadb-server
```

### Windows

[MySQL Community Server 8.0.36](https://dev.mysql.com/downloads/mysql/) download page

[MariaDB](https://mariadb.org/download) download page

## Install system packages

### Ubuntu/Debian

```bash
apt install git, imagemagick, virtualenv, python3, python3-venv
```

### Windows

[Python](https://www.python.org/downloads/windows/) for Windows

[ImageMagick](https://imagemagick.org/script/download.php) download page

## Clone this repository

```bash
git clone https://github.com/billypom/200-Bot.git
```

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

## Create DB Test data

This user runs integration tests and will handle the creation and deletion of the bot's mysql.user record while testing

Replace 'localhost' with your server hostname, if not running locally

```sql
CREATE USER 'test_runner'@'localhost' IDENTIFIED BY '<YOUR_PASSWORD_HERE>';
CREATE DATABASE test_lounge_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE, DROP on test_lounge_dev.* to 'test_runner'@'localhost';
```

### Create local development database

```sql
-- coming soon
```

### Update `config.py`

```py
# Bot config
TOKEN = ""
BOT_ID = 0

# Guild config - your guild ID goes here
LOUNGE = []

# DB config for Discord Bot
# Create your own mysql.user
HOST = "localhost"
PASS = ""
USER = ""
DTB = "lounge_dev"

# DB config for integration test user (test-runner from the README)
TEST_HOST = "localhost"
TEST_PASS = ""
TEST_USER = "test_runner"
TEST_DTB = "test_lounge_dev"
```

Run the bot

```
python3 main.py
```

:)

# Credits
[Lorenzi Table Maker](https://github.com/hlorenzi/mk8d_ocr)

[150cc Lounge API](https://github.com/VikeMK/Lounge-API)

[mariokartcentral.com](https://www.mariokartcentral.com/)
