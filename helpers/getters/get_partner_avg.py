import DBA
from helpers.senders import send_raw_to_debug_channel
import logging


# Input: discord user id,
# Output: float avg partner score (rounded 2 decimal places)
async def get_partner_avg(
    client,
    uid: int,
    number_of_mogis: int,
    mogi_format_string: str,
    tier_id: str = "%",
    db_name: str = "s6200lounge",
) -> float:
    """Returns the partner average for a certain player
    Args:
    uid - Discord ID
    number_of_mogis: the number of mogis"""
    # logging.info(f'get_partner_avg  | uid={uid} | #mogis={number_of_mogis} | format={mogi_format_string} | tier={tier_id}')
    try:
        with DBA.DBAccess(db_name) as db:
            sql = """
                SELECT pm.mogi_id, pm.place, pm.mmr_change 
                FROM player_mogi as pm 
                JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                WHERE pm.player_id = %s 
                AND m.mogi_format IN (%s)
                AND tier_id like %s 
                ORDER BY m.create_date DESC LIMIT %s
                """ % ("%s", mogi_format_string, "%s", "%s")
            # debug_temp1 = db.query(sql, (uid, tier_id, number_of_mogis))

            sql = """
                SELECT pm.player_id, pm.mogi_id, pm.place, pm.score, pm.mmr_change 
                FROM player_mogi as pm 
                INNER JOIN 
                    (SELECT pm.mogi_id, pm.place, pm.mmr_change 
                    FROM player_mogi as pm 
                    JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                    WHERE pm.player_id = %s 
                    AND m.mogi_format IN (%s)
                    AND tier_id like %s 
                    ORDER BY m.create_date DESC LIMIT %s) as pm2 
                ON pm2.mogi_id = pm.mogi_id 
                AND pm2.place = pm.place 
                AND pm.mmr_change = pm2.mmr_change
                WHERE player_id <> %s """ % ("%s", mogi_format_string, "%s", "%s", "%s")
            # debug_temp2 = db.query(sql, (uid, tier_id, number_of_mogis, uid))

            sql = """
            SELECT AVG(score) 
            FROM 
                (SELECT pm.player_id, pm.mogi_id, pm.place, pm.score, pm.mmr_change 
                FROM player_mogi as pm 
                INNER JOIN 
                    (SELECT pm.mogi_id, pm.place, pm.mmr_change 
                    FROM player_mogi as pm 
                    JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                    WHERE pm.player_id = %s 
                    AND m.mogi_format IN (%s)
                    AND tier_id like %s 
                    ORDER BY m.create_date DESC LIMIT %s) as pm2 
                ON pm2.mogi_id = pm.mogi_id 
                AND pm2.place = pm.place 
                AND pm.mmr_change = pm2.mmr_change
                WHERE player_id <> %s) as a""" % (
                "%s",
                mogi_format_string,
                "%s",
                "%s",
                "%s",
            )
            temp = db.query(sql, (uid, tier_id, number_of_mogis, uid))

            try:
                # logging.info(f'get_partner_avg | SQL Debug 1 returned: {debug_temp1}')
                # logging.info(f'get_partner_avg | SQL Debug 2 returned: {debug_temp2}')
                # logging.info(f'get_partner_avg | SQL returned: {temp}')
                return round(float(temp[0][0]), 2)  # type: ignore
            except Exception:
                logging.info("get_partner_avg | SQL did not return any average")
                return 0
    except Exception as e:
        await send_raw_to_debug_channel(client, "partner average error", e)
    return 0
