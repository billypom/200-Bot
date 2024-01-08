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

CREATE TABLE mogi_queue(
    id int unsigned auto_increment,
    channel_id int unsigned,

);

CREATE TABLE player_queue(
    player_id int unsigned,
    create_date TIMESTAMP default CURRENT_TIMESTAMP,
    CONSTRAINT player_queuepk PRIMARY KEY (player_id)
);

insert into punishment(punishment_type)
values ('Restriction'),
('Loungeless')
('Warning');

-- Real Ranks
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

-- Real Tiers
insert into tier (tier_id, tier_name, results_id, teams_string)
values (1010662448715546706, 's', 1010600237880053800, ""),
(1010662448715546706, 'a', 1010600237880053800, ""),
(1010662628793786448, 'b', 1010600376187244655, ""),
(1010663000987934771, 'c', 1010600418524532889, ""),
(1010663109536534539, 'all', 1010600464003387542, ""),
(965286774098260029, 'sq', 1010600944209244210, "");