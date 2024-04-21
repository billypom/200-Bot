USE lounge_dev;
DROP TABLE IF EXISTS sq_default_schedule;
DROP TABLE IF EXISTS sq_schedule;
DROP TABLE IF EXISTS sq_helper;
DROP TABLE IF EXISTS player_punishment;
DROP TABLE IF EXISTS punishment;
DROP TABLE IF EXISTS suggestion;
DROP TABLE IF EXISTS player_name_request;
DROP TABLE IF EXISTS player_mogi;
DROP TABLE IF EXISTS strike;
DROP TABLE IF EXISTS mogi;
DROP TABLE IF EXISTS tier;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS ranks;

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
    banned_by_strikes_unban_date bigint unsigned default NULL,
    CONSTRAINT playerpk PRIMARY KEY (player_id),
    CONSTRAINT playerfk FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
);

CREATE TABLE tier (
    tier_id bigint unsigned,
    tier_name varchar(4),
    results_id bigint unsigned,
    voting boolean default 0,
    teams_string varchar(800),
    min_mmr int,
    max_mmr int,
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
    has_reduced_loss boolean default 0,
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
    ban_length int,
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

CREATE TABLE sq_helper(
    -- table holds category id's of categories created
    -- when sq runs. to be used to validate /table submission channels
    -- and determine that its a sq being played
    id int unsigned auto_increment,
    category_id bigint unsigned,
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT sq_helperpk PRIMARY KEY (id)
);
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

-- Dev Tiers
insert into tier (tier_id, tier_name, results_id, teams_string, min_mmr, max_mmr)
values (1231044227065053194, 's', 1231044277522665502, "", 7500, 99999),
(1041162013730164812, 'a', 1041162013730164817, "", 6000, 99999),
(1041162013730164813, 'b', 1041162014086668359, "", 3000, 8999),
(1041162013730164814, 'c', 1041162014086668360, "", 0, 5999),
(1041162013730164815, 'all', 1041162014086668362, "", 0, 99999),
(1041162013356855406, 'sq', 1041162013356855407, "", NULL, NULL);

INSERT INTO player (player_id, player_name, mkc_id, country_code, is_chat_restricted, mmr, base_mmr, peak_mmr, rank_id, times_strike_limit_reached, banned_by_strikes_unban_date)
values (1, '1', 1, 'US', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (2, '2', 2, 'FR', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (3, '3', 3, 'GB', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (4, '4', 4, 'DE', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (5, '5', 5, 'NL', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (6, '6', 6, 'BR', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (7, '7', 7, 'KR', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (8, '8', 8, 'JP', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (9, '9', 9, 'ES', 0, 4000, 4000, 4000, 1041162011536527393, 0, NULL),
    (10, '10', 10, 'CA', 0, NULL, NULL, NULL, 1041162011536527393, 0, NULL),
    (11, '11', 11, 'MX', 0, 4000, 4000, 4000, 1041162011536527393, 0, 2147483646),
    (12, '12', 12, 'IT', 1, 4000, 4000, 4000, 1041162011536527393, 0, NULL);

INSERT INTO mogi (mogi_format, tier_id)
values (2, 1231044227065053194), -- s
(3, 1041162013730164812), -- a
(4, 1041162013730164813), -- b
(6, 1041162013730164814), -- c
(2, 1041162013730164815), -- all
(2, 1041162013356855406); -- sq

INSERT INTO strike (player_id, reason, mmr_penalty, penalty_applied, is_active, expiration_date) values
(9, 'has queued penalties', 100, 0, 1, '2037-05-21 13:18:16.290911'),
(9, 'has queued penalties2', 100, 0, 1, '2037-05-21 13:19:16.290911');
