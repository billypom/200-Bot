# 🏁 MK8DX 200cc Lounge Bot
This bot is the primary driver for all things related to the MK8DX 200cc Lounge leaderboard.
- Sign up on [mariokartcentral.com](https://www.mariokartcentral.com/)
- `/verify` your MKC identity 
- Gather for matches in the [Discord server](discord.gg/uR3rRzsjhk) using [MogiBot](https://255mp.github.io/)
- Submit match results
- View player stats on [200-lounge.com](https://200-lounge.com), or use the commands below.

# Developers

## Development environment
A few things are needed/recommended to work on this project.

I will try to keep things updated as development continues

**Linux/WSL operating system + packages**
- There are some features of the bot that use linux shell comamnds to perform certain tasks that may not translate to Windows. MacOS might work with brew. Namely, imagemagick and subprocess

**Text editor with LSP & linter**

- The code in this repo is auto-formatted by Ruff, and the type choices I make are based on feedback from Pyright

**Local database instance**

- To properly test the bot, you will need a local instance of the 200 Lounge database. I use MySQL. MariaDB or Postgres might also work. If you decide to use a database solution other than MySQL feel free to document your process to using it in an issue and I will considering adding those instructions to this repo.

**Discord bot for your own testing**

- You will need to sign up for a Discord Developer account and create your own bot for testing.

___

## Setup

Install system packages

```bash
sudo apt install imagemagick, virtualenv, python3, python3-venv
```

Clone the repo

```bash
git clone https://github.com/billypom/200-Bot.git
```

Create a virtual environment (recommended)

```bash
cd 200-Bot
virtualenv venv
activate
```

Install the project requirements

```bash
pip install -r requirements.txt
```

# Todo

- [ ] Create reproducable test data

- [ ] Provide resource links for things like Discord dev account, database solutions, etc

- [ ] Finish these instructions


Create database

```
CREATE TABLE player (
    player_id bigint unsigned NOT NULL,
    player_name varchar(16) NOT NULL,
    ...
);
etc
```


```
other stuff
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
