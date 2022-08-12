SELECT player_id, SUM(CASE WHEN mmr_change > 0 THEN 1 ELSE 0 END)/count(*) as win_rate
FROM player_mogi
GROUP BY player_id