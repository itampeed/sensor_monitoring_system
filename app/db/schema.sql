-- Enable TimescaleDB (if not already enabled)
CREATE EXTENSION IF NOT EXISTS timescaledb;


-- Recreate Tables
DROP TABLE IF EXISTS proben CASCADE;

CREATE TABLE proben (
    id SERIAL,
    client_id TEXT,
    channel_id TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    grw DOUBLE PRECISION,
    ff DOUBLE PRECISION,
    varianz DOUBLE PRECISION,
    klasse INT,
    raw_signal TEXT,
    filtered_signal TEXT,
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('proben', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS messplattform (
    id SERIAL PRIMARY KEY,
    bezeichnung TEXT NOT NULL,
    ort TEXT
);

CREATE TABLE IF NOT EXISTS kanal (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    einheit TEXT,
    messplattform_id INT REFERENCES messplattform(id)
);

CREATE TABLE IF NOT EXISTS datenpunkt (
    id SERIAL PRIMARY KEY,
    kanal_id INT REFERENCES kanal(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    wert DOUBLE PRECISION
);
SELECT create_hypertable('datenpunkt', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS merkmale (
    id SERIAL PRIMARY KEY,
    datenpunkt_id INT REFERENCES datenpunkt(id),
    name TEXT,
    wert DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    reset_token TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);