-- Startup PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_Full_Version();

/* #######################################
For storing data related to things of interest
####################################### */

-- Create table for AOIs
CREATE TABLE IF NOT EXISTS area_of_interest (
	area_of_interest_id SERIAL PRIMARY KEY,
	area_of_interest_timestamp TIMESTAMPTZ DEFAULT NOW(),

	area_of_interest_name TEXT UNIQUE NOT NULL,
	area_of_interest_description TEXT,
	area_of_interest_polygon GEOMETRY(POLYGON, 4326) NOT NULL
);

-- Create table for geofences
CREATE TABLE IF NOT EXISTS geofence (
	geofence_id SERIAL PRIMARY KEY,
	geofence_timestamp TIMESTAMPTZ DEFAULT NOW(),

	geofence_name TEXT UNIQUE NOT NULL,
	geofence_description TEXT,
	geofence_polygon GEOMETRY(POLYGON, 4326) NOT NULL
);

-- Create table for vessels of interest
-- mmsi and imo whacky behaviour, so no foriegn key to vessel_data
CREATE TABLE IF NOT EXISTS vessel_of_interest(
	vessel_of_interest_id SERIAL PRIMARY KEY,

	vessel_of_interest_desc_name TEXT UNIQUE NOT NULL,
	vessel_of_interest_description TEXT,
	
	vessel_of_interest_mmsi VARCHAR(9) CHECK (length(vessel_of_interest_mmsi) = 9),
	vessel_of_interest_imo VARCHAR(7) CHECK (length(vessel_of_interest_imo) = 7)
);



/* #######################################
For logging purposes
####################################### */

-- Create table to track data sources
CREATE TYPE data_source_input_types AS ENUM(
	'web_scraper',
	'web_api',
	'receiver',
	'others'
);
CREATE TABLE IF NOT EXISTS data_source (
	data_source_id SERIAL PRIMARY KEY,
	data_source_name TEXT UNIQUE NOT NULL,
	data_source_type data_source_input_types,
	data_source_desc TEXT
);

-- Create table for auditing logs
-- Ingestion events NOT included here
CREATE TYPE log_severity AS ENUM (
    'INFO',
    'WARN',
    'ERROR',
    'CRITICAL'
);
CREATE TABLE IF NOT EXISTS audit_log (
	audit_log_id BIGSERIAL PRIMARY KEY,
	audit_log_timestamp TIMESTAMPTZ DEFAULT NOW(),
	audit_log_event_type TEXT,
	audit_log_severity log_severity,
	audit_log_triggered_by TEXT,
	audit_log_event_desc JSONB
);

-- Create table for data ingest events
-- Store the raw data received
CREATE TABLE IF NOT EXISTS raw_data (
	raw_data_id BIGSERIAL PRIMARY KEY,
	raw_data_timestamp TIMESTAMPTZ DEFAULT NOW(),

	raw_data_payload JSONB NOT NULL,
	
	raw_data_data_source_id INT NOT NULL,
	CONSTRAINT fk_raw_data_data_source_id FOREIGN KEY (raw_data_data_source_id)
	REFERENCES data_source(data_source_id)
);

-- Create table for any errors regarding data ingestion
-- Ignore successes, only log failures
CREATE TABLE IF NOT EXISTS data_ingestion_audit_log (
	data_ingestion_audit_log_id BIGSERIAL PRIMARY KEY,
	data_ingestion_audit_log_timestamp TIMESTAMPTZ DEFAULT NOW(),

	data_ingestion_audit_log_triggered_by TEXT,
	data_ingestion_audit_log_event_desc JSONB,
	
	data_ingestion_audit_log_raw_data_id BIGINT NOT NULL,
	CONSTRAINT fk_data_ingestion_audit_log_raw_data_id FOREIGN KEY (data_ingestion_audit_log_raw_data_id)
	REFERENCES raw_data(raw_data_id)
);



/* #######################################
For storing data related to vessels
####################################### */

-- Create table to store 'staic' vessel info
CREATE TABLE IF NOT EXISTS vessel_data (
	vessel_data_id SERIAL PRIMARY KEY,
	vessel_data_mmsi VARCHAR(9) CHECK (length(vessel_data_mmsi) = 9), -- mmsi is fixed length, and for leading 0s
	vessel_data_imo VARCHAR(7) CHECK (length(vessel_data_imo) = 7), -- imo is fixed length, and for leading 0s
	vessel_data_ship_name TEXT,
	vessel_data_ship_type TEXT,
	vessel_data_flag TEXT, -- registered to country
	vessel_data_length_meters INT,
	vessel_data_beam_meters INT, -- width
	vessel_data_user_tags TEXT[]
);
-- Search by MMSI
CREATE INDEX vessel_data_mmsi_index ON vessel_data(vessel_data_mmsi);

-- Create table to store vessel location info
CREATE TABLE IF NOT EXISTS vessel_location (
	vessel_location_id BIGSERIAL PRIMARY KEY,
	vessel_location_coords GEOMETRY(POINT, 4326) NOT NULL,
	vessel_location_timestamp TIMESTAMPTZ DEFAULT NOW(),
	
	vessel_location_speed_knots REAL,
	vessel_location_course_deg REAL,
	vessel_location_heading_deg REAL,
	vessel_location_rate_of_turn_deg_per_sec REAL,
	vessel_location_nav_status SMALLINT  CHECK (vessel_location_nav_status BETWEEN 0 AND 15), -- as defined by AIS standards
	
	vessel_location_vessel_data_id INT NOT NULL,
	CONSTRAINT fk_vessel_location_vessel_data_id FOREIGN KEY (vessel_location_vessel_data_id)
	REFERENCES vessel_data(vessel_data_id),

	vessel_location_raw_data_id BIGSERIAL NOT NULL,
	CONSTRAINT fk_vessel_location_raw_data_id FOREIGN KEY (vessel_location_raw_data_id)
	REFERENCES raw_data(raw_data_id)
);
-- Search by location
CREATE INDEX vessel_location_coords_index ON vessel_location USING GIST (vessel_location_coords);
-- Search by vessel and time (ie see vessel track)
CREATE INDEX vessel_location_timestamp_vessel_index ON vessel_location (vessel_location_vessel_data_id, vessel_location_timestamp DESC);
-- Search by time (eg in the past day...)
CREATE INDEX vessel_location_timestamp_index ON vessel_location (vessel_location_timestamp DESC);


/* #######################################
For storing data related to alerts
####################################### */

-- Create table to store alert rules
CREATE TABLE IF NOT EXISTS alert_rule (
	alert_rule_id SERIAL PRIMARY KEY,
	alert_rule_timestamp TIMESTAMPTZ DEFAULT NOW(),
	
	alert_rule_name TEXT UNIQUE NOT NULL,
	alert_rule_description TEXT,
	alert_rule_params JSONB NOT NULL,
	
	alert_rule_enabled BOOLEAN NOT NULL
);

-- Create table to store alert history
CREATE TABLE IF NOT EXISTS alert_history (
	alert_history_id SERIAL PRIMARY KEY,
	alert_history_timestamp TIMESTAMPTZ DEFAULT NOW(),

	alert_history_read BOOLEAN NOT NULL,
	alert_history_read_at TIMESTAMPTZ,
	
	alert_history_alert_rule_id INT NOT NULL,
	CONSTRAINT fk_alert_history_alert_rule_id FOREIGN KEY (alert_history_alert_rule_id)
	REFERENCES alert_rule(alert_rule_id)
);
