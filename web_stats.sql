SELECT p.player_id, 
RANK() OVER ( ORDER BY p.mmr DESC ) as "Rank",
p.country_code as "Country", 
p.player_name as "Player Name", 
p.mmr as "MMR", 
p.peak_mmr as "Peak MMR", 
CONCAT(tenpm.wins, "-", tenpm.losses) as "Win/Loss (Last 10)",
tenpm.last_ten_change as "Gain/Loss (Last 10)",
pm.events_played as "Events Played",
pm.largest_gain as "Largest Gain",
pm.largest_loss as "Largest Loss",
p.twitch_link as "Twitch"
FROM player as p 
JOIN (SELECT ten.player_id, SUM(CASE WHEN ten.mmr_change > 0 THEN 1 ELSE 0 END) as wins, SUM(CASE WHEN ten.mmr_change <= 0 THEN 1 ELSE 0 END) as losses, SUM(mmr_change) as last_ten_change
	FROM (SELECT player_id, mmr_change FROM (SELECT mogi_id FROM mogi ORDER BY create_date DESC LIMIT 10) as m JOIN player_mogi ON m.mogi_id = player_mogi.mogi_id) as ten
	GROUP BY player_id) as tenpm
ON p.player_id = tenpm.player_id
JOIN (SELECT player_id, count(*) as events_played, MAX(mmr_change) as largest_gain, MIN(mmr_change) as largest_loss FROM player_mogi GROUP BY player_id) as pm
ON p.player_id = pm.player_id
