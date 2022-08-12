SELECT player_id, count(*) as events_played, MAX(mmr_change) as largest_gain, MIN(mmr_change) as largest_loss FROM player_mogi
GROUP BY player_id