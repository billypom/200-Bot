import DBA
import logging

async def get_tier_from_room_range(min_mmr, max_mmr):
    """Returns tier_id, tier_name, given (min_mmr, max_mmr)"""
    # Translate min & max mmr to 'tier'
    tier_id = 0
    tier_name = ''
    try:
        with DBA.DBAccess() as db:
            tier_data = db.query('SELECT tier_id, tier_name FROM tier WHERE max_mmr >= %s AND min_mmr <= %s;', (max_mmr, min_mmr))
    except Exception as e:
        logging.warning(f'table error | could not translate lounge queue room data to tier id | {e}')
    
    if len(tier_data) > 1:
        for tier in tier_data:
            if tier[1] == 'all':
                continue
            else:
                tier_id = tier[0]
                tier_name = tier[1]
    else: 
        tier_id = tier_data[0][0]
        tier_name = tier_data[0][1]
        
    return tier_id, tier_name