DROP TABLE IF EXISTS sub_leaver;
DROP TABLE IF EXISTS player_name_request;
DROP TABLE IF EXISTS lineups;
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
    unban_date TIMESTAMP default NULL,
    CONSTRAINT playerpk PRIMARY KEY (player_id),
    CONSTRAINT playerfk FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
);

CREATE TABLE tier (
    tier_id bigint unsigned,
    tier_name varchar(4),
    results_id bigint unsigned,
    voting boolean default 0,
    teams_string varchar(800), --using 713 maximum right now
    CONSTRAINT tierpk PRIMARY KEY (tier_id)
);

CREATE TABLE mogi (
    mogi_id int unsigned auto_increment,
    mogi_format int,
    tier_id bigint unsigned,
    table_url varchar(240),
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
-- null = suggestion sent but not responded to
-- 0 = suggestion denied
-- 1 = suggestion approved

insert into ranks (rank_id, rank_name, mmr_min, mmr_max, placement_mmr)
values (791874714434797589, 'Grandmaster', 11000, 99999, NULL),
(794262638518730772, 'Master', 9000, 10999, NULL),
(794262898423627857, 'Diamond', 7500, 8999, NULL),
(794262916627038258, 'Platinum', 6000, 7499, NULL),
(794262925098745858, 'Gold', 4500, 5999, 5250),
(794262959084797984, 'Silver', 3000, 4499, 3750),
(794263467581374524, 'Bronze', 1500, 2999, 2250),
(970028275789365368, 'Iron', 0, 1499, 1000),
(846497627508047872, 'Placement', -2, -1, 2500);

insert into tier (tier_id, tier_name, results_id, teams_string)
values (1010662448715546706, 'a', 1010600237880053800, ""),
(1010662628793786448, 'b', 1010600376187244655, ""),
(1010663000987934771, 'c', 1010600418524532889, ""),
(1010663109536534539, 'all', 1010600464003387542, ""),
(965286774098260029, 'sq', 1010600944209244210, "");

-- insert into player (player_id, player_name, mkc_id, mmr, fc, country_code, rank_id, twitch_link) 
-- values (166818526768791552,'popuko',154, 3000, NULL, 'us', 846497627508047872, 'toppomeranian'),
-- (999835318104625252,'biggie-bag',155, 5000, NULL, 'us', 846497627508047872, 'pokemongo'),
-- (285950464556531712, '1p', 20, 4000, NULL, 'gb', 846497627508047872, NULL),
-- (285950464556531713, '2p', 20, 6000, NULL, 'de', 846497627508047872, NULL),
-- (285950464556531714, '3p', 20, 1500, NULL, 'nl', 846497627508047872, NULL),
-- (177162177432649728, 'Toad', 20, 7500, NULL, 'br', 846497627508047872, 'worldfriendtv1'),
-- (963579785861279754, 'sq', 20, 8999, NULL, 'jp', 846497627508047872, 'finalfantasyxiv'),
-- (474389780067778580, 'BooBot', 20, 4499, NULL, 'mx', 846497627508047872, NULL),
-- (235148962103951360, 'Carl-bot', 20, 4499, NULL, 'ca', 846497627508047872, 'LCK'),
-- (159985870458322944, 'MEE6', 20, 4499, NULL, 'es', 846497627508047872, NULL),
-- (450127943012712448, 'MogiBot', 20, 4499, NULL, 'fr', 846497627508047872, NULL),
-- (898251551183896586, 'Netty', 20, 4499, NULL, 'kr', 846497627508047872, NULL),
-- (459860530618695681, 'RandomBot', 20, 4499, NULL, 'co', 846497627508047872, NULL),
-- (180070755415883776, 'Technical', 6764, NULL, '4139-9521-7609', 'US', 846497627508047872, NULL),
-- (355173440678002698, 'Ty', 2990, NULL, '3602-9259-9893', 'US', 846497627508047872, NULL),
-- (501862194825265153, 'Nino', 9420, NULL, '3062-9403-5535', 'DE', 846497627508047872, NULL),
-- (316670571012161538, 'Francis', 1818, NULL, NULL, 'PT', 846497627508047872, NULL);


-- insert into lineups (player_id, tier_id, vote)
-- values (285950464556531712, 970019818671599706, 2),
-- (285950464556531713, 970019818671599706, 3),
-- (285950464556531714, 970019818671599706, 4),
-- (177162177432649728, 970019818671599706, 6),
-- (963579785861279754, 970019818671599706, 2),
-- (474389780067778580, 970019818671599706, 3),
-- (235148962103951360, 970019818671599706, 4),
-- (159985870458322944, 970019818671599706, 6),
-- (898251551183896586, 970019818671599706, 2),
-- (459860530618695681, 970019818671599706, 2),
-- (999835318104625252, 970019818671599706, 2);