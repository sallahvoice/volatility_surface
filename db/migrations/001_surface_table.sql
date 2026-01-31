CREATE TABLE IF NOT EXISTS surface_snapshots (
    snapshot_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    underlying_con_id INT NOT NULL,
    spot_price DECIMAL(12, 4) NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT NULL,
    INDEX indx_symbol_time (symbol, captured_at)
)ENGINE=InnoDB, DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS suface_data_points (
    data_point_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    snapshot_id INT NOT NULL,
    expiration VARCHAR(8) NOT NULL,
    strike VARCHAR(12, 4) NOT NULL,
    implied_vol VARCHAR(8, 4) NOT NULL,
    option_type CHAR(1) NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES surface_snapshots(snapshot_id)
        ON DELETE CASCADE
    INDEX idx_snapshot (snapshot_id)
)ENGINE=InnoDB, DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW v_surface_full AS
SELECT
    ss.snapshot_id,
    ss.symbol,
    ss.underlying_con_id,
    ss.spot_price,
    ss.captured_at,
    ss.note,
    sdp.data_point_id,
    sdp.expiration,
    sdp.strike,
    sdp.implied_vol,
    sdp.option_type
FROM surface_snapshots as ss
JOIN suface_data_points sdp WHERE ss.snapshot_id = sdp.surface_snapshots: