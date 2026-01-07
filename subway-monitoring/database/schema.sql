-- Create the table for storing real-time train positions
CREATE TABLE IF NOT EXISTS realtime_train_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    subway_id VARCHAR(50),
    subway_name VARCHAR(100),
    station_id VARCHAR(50),
    station_name VARCHAR(100),
    train_number VARCHAR(50),
    last_reception_date VARCHAR(8),
    reception_time TIMESTAMP,
    message_direction VARCHAR(10), -- 0:Up/Inner, 1:Down/Outer
    destination_station_id VARCHAR(50),
    destination_station_name VARCHAR(100),
    train_status VARCHAR(10), -- 0:Entry, 1:Arrived, 2:Departed...
    is_express BOOLEAN,
    is_last_train BOOLEAN
);

-- Index for faster querying by time and line
CREATE INDEX idx_rtp_created_at ON realtime_train_positions(created_at);
CREATE INDEX idx_rtp_subway_id ON realtime_train_positions(subway_id);
