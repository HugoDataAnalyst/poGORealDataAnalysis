#-- script to extract data from main database
#!/bin/bash
# Set the source and target database details
SOURCE_HOST="surcehost"
SOURCE_DB="yoursourcedb"
SOURCE_PASSWORD="sourcedbpassword"
SOURCE_USER="sourcedbusername"

TARGET_HOST="targethost"
TARGET_DB="yourtargetdb"
TARGET_PASSWORD="targetdbpassword"
TARGET_USER="targetdbusername"
# SQL QUERY
SPAWNPOINT_QUERY="INSERT IGNORE INTO targetdb.spawnpoint (targetdb.spawnpoint.id, targetdb.spawnpoint.lat, targetdb.spawnpoint.lon, targetdb.spawnpoint.updated, targetdb.spawnpoint.last_seen, targetdb.spawnpoint.despawn_sec) SELECT sourcedb.spawnpoint.id, sourcedb.spawnpoint.lat, sourcedb.spawnpoint.lon, sourcedb.spawnpoint.updated, sourcedb.spawnpoint.last_seen, sourcedb.spawnpoint.despawn_sec FROM sourcedb.spawnpoint; "

POKEMON_QUERY="CREATE TEMPORARY TABLE temp_pokemon AS
    SELECT
        id, spawn_id, lat, lon, weight, height,
        size, expire_timestamp, first_seen_timestamp, pokemon_id,
        atk_iv, cp, def_iv, sta_iv, form, level,
        weather, costume, expire_timestamp_verified,
        display_pokemon_id, is_ditto, shiny, pvp
    FROM sourcedb.pokemon
    WHERE atk_iv IS NOT NULL;

INSERT IGNORE INTO targetdb.pokemon
    (id, spawn_id, lat, lon, weight, height,
    size, expire_timestamp, first_seen_timestamp, pokemon_id,
    atk_iv, cp, def_iv, sta_iv, form, level,
    weather, costume, expire_timestamp_verified,
    display_pokemon_id, is_ditto, shiny, pvp)
SELECT * FROM temp_pokemon;

DROP TEMPORARY TABLE IF EXISTS temp_pokemon;"

GYM_QUERY="INSERT INTO targetdb.gym2 
(targetdb.gym2.id, 
targetdb.gym2.lat, 
targetdb.gym2.lon, 
targetdb.gym2.name, 
targetdb.gym2.url,
targetdb.gym2.last_modified_timestamp,
targetdb.gym2.guarding_pokemon_id,
targetdb.gym2.team_id,
targetdb.gym2.sponsor_id,
targetdb.gym2.partner_id,
targetdb.gym2.first_seen_timestamp, 
targetdb.gym2.raid_spawn_timestamp, 
targetdb.gym2.raid_battle_timestamp, 
targetdb.gym2.raid_end_timestamp, 
targetdb.gym2.raid_pokemon_id, 
targetdb.gym2.raid_pokemon_form,
targetdb.gym2.raid_level, 
targetdb.gym2.ex_raid_eligible, 
targetdb.gym2.raid_pokemon_gender,
targetdb.gym2.raid_pokemon_costume,
targetdb.gym2.raid_pokemon_evolution,
targetdb.gym2.ar_scan_eligible) 
SELECT 
sourcedb.gym.id, 
sourcedb.gym.lat, 
sourcedb.gym.lon, 
sourcedb.gym.name, 
sourcedb.gym.url,
sourcedb.gym.last_modified_timestamp,
sourcedb.gym.guarding_pokemon_id,
sourcedb.gym.team_id,
sourcedb.gym.sponsor_id,
sourcedb.gym.partner_id,
sourcedb.gym.first_seen_timestamp, 
sourcedb.gym.raid_spawn_timestamp, 
sourcedb.gym.raid_battle_timestamp, 
sourcedb.gym.raid_end_timestamp, 
sourcedb.gym.raid_pokemon_id, 
sourcedb.gym.raid_pokemon_form,
sourcedb.gym.raid_level, 
sourcedb.gym.ex_raid_eligible, 
sourcedb.gym.raid_pokemon_gender,
sourcedb.gym.raid_pokemon_costume,
sourcedb.gym.raid_pokemon_evolution,
sourcedb.gym.ar_scan_eligible 
FROM sourcedb.gym WHERE sourcedb.gym.raid_spawn_timestamp IS NOT NULL;"

INCIDENT_QUERY="INSERT IGNORE INTO targetdb.incident 
(targetdb.incident.id, 
targetdb.incident.pokestop_id, 
targetdb.incident.start, 
targetdb.incident.expiration, 
targetdb.incident.display_type, 
targetdb.incident.style, 
targetdb.incident.character, 
targetdb.incident.updated) 
SELECT 
sourcedb.incident.id, 
sourcedb.incident.pokestop_id, 
sourcedb.incident.start, 
sourcedb.incident.expiration, 
sourcedb.incident.display_type, 
sourcedb.incident.style, 
sourcedb.incident.character, 
sourcedb.incident.updated 
FROM sourcedb.incident;"



# Run the SQL queries
mysql -h $SOURCE_HOST -u $SOURCE_USER -p$SOURCE_PASSWORD $SOURCE_DB -e "$SPAWNPOINT_QUERY"
mysql -h $TARGET_HOST -u $TARGET_USER -p$TARGET_PASSWORD $TARGET_DB -e "$SPAWNPOINT_QUERY"

mysql -h $SOURCE_HOST -u $SOURCE_USER -p$SOURCE_PASSWORD $SOURCE_DB -e "$POKEMON_QUERY"
mysql -h $TARGET_HOST -u $TARGET_USER -p$TARGET_PASSWORD $TARGET_DB -e "$POKEMON_QUERY"

mysql -h $SOURCE_HOST -u $SOURCE_USER -p$SOURCE_PASSWORD $SOURCE_DB -e "$GYM_QUERY"
mysql -h $TARGET_HOST -u $TARGET_USER -p$TARGET_PASSWORD $TARGET_DB -e "$GYM_QUERY"

mysql -h $SOURCE_HOST -u $SOURCE_USER -p$SOURCE_PASSWORD $SOURCE_DB -e "$INCIDENT_QUERY"
mysql -h $TARGET_HOST -u $TARGET_USER -p$TARGET_PASSWORD $TARGET_DB -e "$INCIDENT_QUERY"

# Could create a procedure to execute the pokemon table insertion into the storage warehouse


#DELIMITER //

#CREATE PROCEDURE ProcessPokemonDataInBatches()
#BEGIN
#    DECLARE batch_start INT DEFAULT 0;
#    DECLARE batch_size INT DEFAULT 10000;

#    REPEAT
#        CREATE TEMPORARY TABLE temp_pokemon AS
#        SELECT
#            id, spawn_id, lat, lon, weight, height,
#            size, expire_timestamp, first_seen_timestamp, pokemon_id,
#            atk_iv, cp, def_iv, sta_iv, form, level,
#            weather, costume, expire_timestamp_verified,
#            display_pokemon_id, is_ditto, shiny, pvp
#        FROM sourcedb.pokemon
#        WHERE atk_iv IS NOT NULL
#        LIMIT batch_start, batch_size;

#        INSERT IGNORE INTO targetdb.pokemon
#        SELECT * FROM temp_pokemon;

#        DROP TEMPORARY TABLE IF EXISTS temp_pokemon;

#        SET batch_start = batch_start + batch_size;

#    UNTIL batch_start >= (SELECT COUNT(*) FROM sourcedb.pokemon WHERE atk_iv IS NOT NULL) END REPEAT;

#END //

#DELIMITER ;
#"CALL ProcessPokemonDataInBatches();"
