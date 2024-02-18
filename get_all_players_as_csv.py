import DBA
import csv

try:
    with DBA.DBAccess() as db:
        data = db.query('SELECT player_name, mmr, base_mmr, peak_mmr FROM player;', ())
except Exception as e:
    print(e)

with open('players.csv', 'w') as file:
    writer = csv.writer(file)
    
    for player in data:
        writer.writerow(player)