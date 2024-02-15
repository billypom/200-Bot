import DBA
import sys
import time

def add_random_players_to_queue(number_of_players):
    number_of_players = int(number_of_players)
    player_list = []
    # Get random players from db
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player ORDER BY RAND() LIMIT %s;', (number_of_players,))
    except Exception as e:
        print(f'what the hck 1 | {e}')
        return False
    
    for player in temp:
        player_list.append(player[0])
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO lounge_queue_player (player_id) VALUES (%s);', (player[0],))
        time.sleep(0.2)
    return True

add_random_players_to_queue(sys.argv[1])