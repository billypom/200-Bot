USE lounge_dev;
DROP TABLE IF EXISTS sq_default_schedule;
DROP TABLE IF EXISTS sq_schedule;
DROP TABLE IF EXISTS player_punishment;
DROP TABLE IF EXISTS punishment;
DROP TABLE IF EXISTS suggestion;
DROP TABLE IF EXISTS sub_leaver;
DROP TABLE IF EXISTS player_name_request;
DROP TABLE IF EXISTS lineups;
DROP TABLE IF EXISTS player_mogi;
DROP TABLE IF EXISTS strike;
DROP TABLE IF EXISTS mogi;
DROP TABLE IF EXISTS tier;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS ranks;
DROP PROCEDURE IF EXISTS copy_data_to_dev;


CREATE TABLE ranks (
    rank_id bigint unsigned,
    rank_name varchar(12),
    mmr_min int,
    mmr_max int,
    placement_mmr int default NULL,
    CONSTRAINT rankspk PRIMARY KEY (rank_id)
);

CREATE TABLE player (
    player_id bigint unsigned NOT NULL,
    player_name varchar(16) NOT NULL,
    mkc_id int unsigned NOT NULL,
    country_code varchar(3) default '',
    fc varchar(15),
    is_host_banned boolean default 0,
    is_chat_restricted boolean default 0,
    mmr int,
    base_mmr int,
    peak_mmr int,
    rank_id bigint unsigned default 846497627508047872,
    times_strike_limit_reached int unsigned default 0,
    twitch_link varchar(50) default NULL,
    mogi_media_message_id bigint unsigned default NULL,
    unban_date TIMESTAMP default NULL,
    CONSTRAINT playerpk PRIMARY KEY (player_id),
    CONSTRAINT playerfk FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
);

CREATE TABLE tier (
    tier_id bigint unsigned,
    tier_name varchar(4),
    results_id bigint unsigned,
    voting boolean default 0,
    teams_string varchar(800),
    CONSTRAINT tierpk PRIMARY KEY (tier_id)
);

CREATE TABLE mogi (
    mogi_id int unsigned auto_increment,
    mogi_format int,
    tier_id bigint unsigned,
    table_url varchar(240),
    table_message_id bigint unsigned default null,
    mmr_message_id bigint unsigned default null,
    create_date TIMESTAMP default CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT mogipk PRIMARY KEY (mogi_id),
    CONSTRAINT mogifk FOREIGN KEY (tier_id) REFERENCES tier(tier_id)
);

CREATE TABLE strike (
    strike_id int unsigned auto_increment,
    player_id bigint unsigned,
    reason varchar(32),
    mmr_penalty int,
    penalty_applied boolean default 1,
    is_active boolean default 1,
    create_date TIMESTAMP default CURRENT_TIMESTAMP NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    CONSTRAINT strikepk PRIMARY KEY (strike_id),
    CONSTRAINT strikefk FOREIGN KEY (player_id) REFERENCES player(player_id)
);

-- match history
CREATE TABLE player_mogi (
    player_id bigint unsigned,
    mogi_id int unsigned,
    place int unsigned,
    score int unsigned,
    prev_mmr int,
    mmr_change int,
    new_mmr int,
    is_sub boolean default 0,
    CONSTRAINT playermogipk PRIMARY KEY (player_id, mogi_id),
    CONSTRAINT playermogifk1 FOREIGN KEY (player_id) REFERENCES player(player_id),
    CONSTRAINT playermogifk2 FOREIGN KEY (mogi_id) REFERENCES mogi(mogi_id)
);

-- player_tier
-- temporary table for ongoing mogis
CREATE TABLE lineups (
    player_id bigint unsigned,
    tier_id bigint unsigned,
    vote int unsigned,
    is_sub boolean default 0,
    can_drop boolean default 1,
    create_date TIMESTAMP default CURRENT_TIMESTAMP NOT NULL,
    last_active TIMESTAMP,
    wait_for_activity boolean default 0,
    mogi_start_time TIMESTAMP default NULL,
    CONSTRAINT lineupspk PRIMARY KEY (player_id, tier_id),
    CONSTRAINT lineupsfk1 FOREIGN KEY (player_id) REFERENCES player(player_id),
    CONSTRAINT lineupsfk2 FOREIGN KEY (tier_id) REFERENCES tier(tier_id)
);

CREATE TABLE player_name_request(
    id int unsigned auto_increment,
    player_id bigint unsigned,
    requested_name varchar(16),
    was_accepted boolean default 0,
    embed_message_id bigint unsigned,
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT playernamerequestpk PRIMARY KEY (id),
    CONSTRAINT playernamerequestfk FOREIGN KEY (player_id) REFERENCES player(player_id)
);

CREATE TABLE sub_leaver(
    id int unsigned auto_increment,
    player_id bigint unsigned,
    tier_id bigint unsigned,
    CONSTRAINT subleaverspk PRIMARY KEY (id),
    CONSTRAINT subleaversfk1 FOREIGN KEY (player_id) REFERENCES player(player_id),
    CONSTRAINT subleaversfk2 FOREIGN KEY (tier_id) REFERENCES tier(tier_id)
);

-- null = suggestion sent but not responded to
-- 0 = suggestion denied
-- 1 = suggestion approved
CREATE TABLE suggestion(
    id int unsigned auto_increment,
    content varchar(1000),
    was_accepted boolean default NULL,
    author_id bigint unsigned,
    admin_id bigint unsigned,
    message_id bigint unsigned,
    reason varchar(1000),
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT suggestionpk PRIMARY KEY (id)
);

CREATE TABLE punishment(
    id int unsigned auto_increment,
    punishment_type varchar(24),
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT punishmentpk PRIMARY KEY (id)
);

CREATE TABLE player_punishment(
    id int unsigned auto_increment,
    punishment_id int unsigned,
    player_id bigint unsigned,
    reason varchar(1000),
    unban_date bigint unsigned,
    admin_id bigint unsigned,
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT player_punishmentpk PRIMARY KEY (id)
);

CREATE TABLE sq_schedule(
    id int unsigned auto_increment,
    start_time bigint unsigned,
    queue_time bigint unsigned,
    mogi_format int unsigned,
    mogi_channel bigint unsigned,
    CONSTRAINT sq_schedulepk PRIMARY KEY (id)
);

CREATE TABLE sq_default_schedule(
    id int unsigned auto_increment,
    day_of_week int unsigned,
    start_time varchar(16),
    mogi_format int unsigned,
    mogi_channel bigint unsigned,
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT default_sq_schedulepk PRIMARY KEY (id)
);

-- Migrate production data to dev db
CREATE PROCEDURE copy_data_to_dev(IN source_schema VARCHAR(255))
BEGIN
  SET @sql = CONCAT('INSERT INTO lounge_dev.ranks SELECT * FROM ', source_schema, '.ranks');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.tier SELECT * FROM ', source_schema, '.tier');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.punishment SELECT * FROM ', source_schema, '.punishment');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.mogi SELECT * FROM ', source_schema, '.mogi');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.player SELECT * FROM ', source_schema, '.player');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.player_mogi SELECT * FROM ', source_schema, '.player_mogi');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.player_name_request SELECT * FROM ', source_schema, '.player_name_request');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.player_punishment SELECT * FROM ', source_schema, '.player_punishment');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.sq_default_schedule SELECT * FROM ', source_schema, '.sq_default_schedule');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.sq_schedule SELECT * FROM ', source_schema, '.sq_schedule');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.strike SELECT * FROM ', source_schema, '.strike');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.sub_leaver SELECT * FROM ', source_schema, '.sub_leaver');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;

  SET @sql = CONCAT('INSERT INTO lounge_dev.suggestion SELECT * FROM ', source_schema, '.suggestion');
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END;

-- Call the stored procedure with the current database name as a parameter
CALL copy_data_to_dev('s6200lounge');

-- Dev Ranks
insert into ranks (rank_id, rank_name, mmr_min, mmr_max, placement_mmr)
values (1041162011536527398, 'Grandmaster', 11000, 99999, NULL),
(1041162011536527397, 'Master', 9000, 10999, NULL),
(1041162011536527396, 'Diamond', 7500, 8999, NULL),
(1041162011536527395, 'Platinum', 6000, 7499, NULL),
(1041162011536527394, 'Gold', 4500, 5999, 5250),
(1041162011536527393, 'Silver', 3000, 4499, 3750),
(1041162011536527392, 'Bronze', 1500, 2999, 2250),
(1041162011536527391, 'Iron', 0, 1499, 1000),
(1041162011536527390, 'Placement', -2, -1, 2500);

-- Replace live rank foreign keys with dev rank foreign keys
UPDATE player SET rank_id = 1041162011536527398 WHERE rank_id = 791874714434797589;
UPDATE player SET rank_id = 1041162011536527397 WHERE rank_id = 794262638518730772;
UPDATE player SET rank_id = 1041162011536527396 WHERE rank_id = 794262898423627857;
UPDATE player SET rank_id = 1041162011536527395 WHERE rank_id = 794262916627038258;
UPDATE player SET rank_id = 1041162011536527394 WHERE rank_id = 794262925098745858;
UPDATE player SET rank_id = 1041162011536527393 WHERE rank_id = 794262959084797984;
UPDATE player SET rank_id = 1041162011536527392 WHERE rank_id = 794263467581374524;
UPDATE player SET rank_id = 1041162011536527391 WHERE rank_id = 970028275789365368;
UPDATE player SET rank_id = 1041162011536527390 WHERE rank_id = 846497627508047872;

-- Replace live ranks with dev ranks
DELETE FROM ranks WHERE rank_id = 791874714434797589;
DELETE FROM ranks WHERE rank_id = 794262638518730772;
DELETE FROM ranks WHERE rank_id = 794262898423627857;
DELETE FROM ranks WHERE rank_id = 794262916627038258;
DELETE FROM ranks WHERE rank_id = 794262925098745858;
DELETE FROM ranks WHERE rank_id = 794262959084797984;
DELETE FROM ranks WHERE rank_id = 794263467581374524;
DELETE FROM ranks WHERE rank_id = 970028275789365368;
DELETE FROM ranks WHERE rank_id = 846497627508047872;

-- Dev Tiers
insert into tier (tier_id, tier_name, results_id, teams_string)
values(1041162013730164812, 'a', 1041162013730164817, ""),
(1041162013730164813, 'b', 1041162014086668359, ""),
(1041162013730164814, 'c', 1041162014086668360, ""),
(1041162013730164815, 'all', 1041162014086668362, ""),
(1041162013356855406, 'sq', 1041162013356855407, "");

-- Replace live mogi foreign keys with dev mogi foreign keys
UPDATE mogi SET tier_id = 1041162013730164812 WHERE tier_id = 1010662448715546706; -- a
UPDATE mogi SET tier_id = 1041162013730164813 WHERE tier_id = 1010662628793786448; -- b
UPDATE mogi SET tier_id = 1041162013730164814 WHERE tier_id = 1010663000987934771; -- c
UPDATE mogi SET tier_id = 1041162013730164815 WHERE tier_id = 1010663109536534539; -- all
UPDATE mogi SET tier_id = 1041162013356855406 WHERE tier_id = 965286774098260029; -- sq

-- Remove live tier references
DELETE FROM tier WHERE tier_id = 1010662448715546706; -- a
DELETE FROM tier WHERE tier_id = 1010662628793786448; -- b
DELETE FROM tier WHERE tier_id = 1010663000987934771; -- c
DELETE FROM tier WHERE tier_id = 1010663109536534539; -- all
DELETE FROM tier WHERE tier_id = 965286774098260029; -- sq