import secretly
import csv
import DBA


with DBA.DBAccess() as db:
    temp = db.query('SELECT * FROM player;', ())
    with open("players.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(['player_id', 'player_name', 'mkc_id', 'country_code', 'fc', 'is_host_banned', 'is_chat_restricted', 'mmr', 'base_mmr', 'peak_mmr', 'rank_id', 'times_strike_limit_reached', 'twitch_link', 'mogi_media_message_id'])
        for player in temp:
            print(player)
            writer.writerow(player)
        

