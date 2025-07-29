-- Enable TimescaleDB (if not already enabled)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Proben table
CREATE TABLE IF NOT EXISTS proben (
    client_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    grw DOUBLE PRECISION,
    ff DOUBLE PRECISION,
    varianz DOUBLE PRECISION,
    klasse INT,
    raw_signal TEXT,
    filtered_signal TEXT,
    PRIMARY KEY (timestamp, client_id, channel_id)
);
SELECT create_hypertable('proben', 'timestamp', if_not_exists => TRUE);

-- Messplattform table
CREATE TABLE IF NOT EXISTS messplattform (
    id SERIAL PRIMARY KEY,
    bezeichnung TEXT NOT NULL,
    ort TEXT
);

-- Kanal table
CREATE TABLE IF NOT EXISTS kanal (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    einheit TEXT,
    messplattform_id INT REFERENCES messplattform(id) ON DELETE CASCADE
);

-- Datenpunkt table (no ID due to Timescale constraints)
CREATE TABLE IF NOT EXISTS datenpunkt (
    kanal_id INT REFERENCES kanal(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    wert DOUBLE PRECISION,
    PRIMARY KEY (timestamp, kanal_id)
);
SELECT create_hypertable('datenpunkt', 'timestamp', if_not_exists => TRUE);

-- Merkmale table (fix FK by referencing timestamp + kanal_id)
CREATE TABLE IF NOT EXISTS merkmale (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    kanal_id INT NOT NULL,
    name TEXT,
    wert DOUBLE PRECISION,
    FOREIGN KEY (timestamp, kanal_id) REFERENCES datenpunkt(timestamp, kanal_id) ON DELETE CASCADE
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    reset_token TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
