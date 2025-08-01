-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- MESSPLATTFORM TABLE
CREATE TABLE IF NOT EXISTS messplattform (
    id SERIAL PRIMARY KEY,
    bezeichnung TEXT NOT NULL,
    ort TEXT
);

-- KANAL TABLE  
CREATE TABLE IF NOT EXISTS kanal (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    einheit TEXT,
    messplattform_id INT REFERENCES messplattform(id) ON DELETE CASCADE
);

-- DATENPUNKT TABLE (raw sensor data points) - Regular table, not hypertable since it's referenced
CREATE TABLE IF NOT EXISTS datenpunkt (
    id SERIAL PRIMARY KEY,
    kanal_id INT REFERENCES kanal(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    wert DOUBLE PRECISION NOT NULL,
    filtered_wert DOUBLE PRECISION
);
-- Create index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_datenpunkt_timestamp ON datenpunkt(timestamp DESC);

-- MERKMALE TABLE (extracted features from data points) - Hypertable for time series
CREATE TABLE IF NOT EXISTS merkmale (
    id SERIAL,
    datenpunkt_id INT REFERENCES datenpunkt(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    wert DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (timestamp, id)
);
SELECT create_hypertable('merkmale', 'timestamp', if_not_exists => TRUE);

-- PROBEN TABLE (classified samples/results) - Hypertable for time series
CREATE TABLE IF NOT EXISTS proben (
    id SERIAL,
    datenpunkt_id INT REFERENCES datenpunkt(id) ON DELETE CASCADE,
    klasse INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (timestamp, id)
);
SELECT create_hypertable('proben', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_datenpunkt_kanal_time ON datenpunkt(kanal_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_merkmale_datenpunkt ON merkmale(datenpunkt_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_proben_datenpunkt ON proben(datenpunkt_id, timestamp DESC);

-- Insert some initial data for testing
INSERT INTO messplattform (id, bezeichnung, ort) VALUES 
    (1, 'Sensor Platform 1', 'Location A'),
    (2, 'Sensor Platform 2', 'Location B')
ON CONFLICT (id) DO NOTHING;

INSERT INTO kanal (id, name, einheit, messplattform_id) VALUES
    (1, 'ch1', 'V', 1),
    (2, 'channel_1', 'A', 1),
    (3, 'channel_2', 'V', 1),
    (4, 'channel_3', 'A', 2)
ON CONFLICT (id) DO NOTHING;
