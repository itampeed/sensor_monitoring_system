-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- MESSPLATTFORM TABLE
CREATE TABLE IF NOT EXISTS messplattform (
    id SERIAL PRIMARY KEY,
    bezeichnung TEXT NOT NULL,
    ort TEXT
);
SELECT create_hypertable('messplattform', 'id', if_not_exists => TRUE, create_default_indexes => FALSE);

-- KANAL TABLE
CREATE TABLE IF NOT EXISTS kanal (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    einheit TEXT,
    messplattform_id INT REFERENCES messplattform(id) ON DELETE CASCADE
);
-- no hypertable required for this one

-- PROBEN TABLE
CREATE TABLE IF NOT EXISTS proben (
    client_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,

    sigstat_mw DOUBLE PRECISION,
    statsig_qmw DOUBLE PRECISION,
    stat_stdaw DOUBLE PRECISION,
    stat_var DOUBLE PRECISION,
    stat_wb DOUBLE PRECISION,
    stat_n6m DOUBLE PRECISION,
    sig_qwm DOUBLE PRECISION,
    sig_grw DOUBLE PRECISION,
    sig_ff DOUBLE PRECISION,

    klasse INT,
    raw_signal TEXT,
    filtered_signal TEXT,

    PRIMARY KEY (timestamp, client_id, channel_id)
);
SELECT create_hypertable('proben', 'timestamp', if_not_exists => TRUE);

-- DATENPUNKT TABLE
CREATE TABLE IF NOT EXISTS datenpunkt (
    kanal_id INT REFERENCES kanal(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    wert DOUBLE PRECISION,
    PRIMARY KEY (timestamp, kanal_id)
);
SELECT create_hypertable('datenpunkt', 'timestamp', if_not_exists => TRUE);

-- MERKMALE TABLE
CREATE TABLE IF NOT EXISTS merkmale (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    kanal_id INT NOT NULL,
    name TEXT,
    wert DOUBLE PRECISION,
    FOREIGN KEY (timestamp, kanal_id) REFERENCES datenpunkt(timestamp, kanal_id) ON DELETE CASCADE
);
