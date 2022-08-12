SELECT ten.player_id, SUM(CASE WHEN ten.mmr_change > 0 THEN 1 ELSE 0 END) as wins, SUM(CASE WHEN ten.mmr_change <= 0 THEN 1 ELSE 0 END) as losses, SUM(mmr_change) as last_ten_change
FROM (SELECT player_id, mmr_change FROM (SELECT mogi_id FROM mogi ORDER BY create_date DESC LIMIT 10) as m JOIN player_mogi ON m.mogi_id = player_mogi.mogi_id) as ten
GROUP BY player_id