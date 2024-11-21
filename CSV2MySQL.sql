CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;


CREATE TABLE IF NOT EXISTS road_events_3 (
    id VARCHAR(255),
    type VARCHAR(255),
    data_source_id VARCHAR(255),
    event_type VARCHAR(255),
    road_names TEXT,
    direction VARCHAR(255),
    description TEXT,
    creation_date DATETIME,
    update_date DATETIME,
    start_date DATETIME,
    end_date DATETIME,
    event_status VARCHAR(255),
    start_date_accuracy VARCHAR(255),
    end_date_accuracy VARCHAR(255),
    beginning_accuracy VARCHAR(255),
    ending_accuracy VARCHAR(255),
    location_method VARCHAR(255),
    vehicle_impact VARCHAR(255),
    beginning_cross_street TEXT,
    ending_cross_street TEXT,
    type_name VARCHAR(255),
    are_workers_present VARCHAR(255),
    worker_presence_definition TEXT,
    worker_presence_confidence VARCHAR(255),
    worker_presence_last_confirmed_date DATETIME,
    geometry_type VARCHAR(255),
    geometry_coordinates TEXT,
    PRIMARY KEY (id)
);

LOAD DATA INFILE '/tmp/road_events_511_5.csv'
INTO TABLE road_events_3
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS


