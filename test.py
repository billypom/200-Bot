import DBA
import logging

host_string = '    '
player_list = [779325331605684244, 514549516297568257, 885986278439542834, 619555029451538432, 474688986854719490, 457722151919943681, 717795542016720916, 782070166049652746, 998666400539353178, 879070237042020402, 618619294871191593, 980357898871906314]

player_list_tuple = tuple(player_list)

try:
    with DBA.DBAccess() as db:
        host_temp = db.query('SELECT fc, player_id FROM player WHERE fc IS NOT NULL AND is_host_banned = 0 AND player_id IN %s ORDER BY RANDOM() LIMIT 1;', (player_list_tuple,))


        host_temp = db.query('SELECT fc, player_id FROM (SELECT )')


        host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
except Exception as e:
    logging.warning(f'create_teams error | Unable to find host in list: {player_list} | error: {e}')
    host_string = '`No FC found` - Choose amongst yourselves'
