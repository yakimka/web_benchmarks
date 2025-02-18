CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    ip_address VARCHAR(15),
    mac_address VARCHAR(17),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'repair', 'decommissioned')) DEFAULT 'active',
    last_online TIMESTAMP,
    purchase_date DATE,
    warranty_expiry DATE,
    location VARCHAR(255),
    firmware_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email, password_hash) VALUES
    ('alice', 'alice@example.com', 'hashed_password_1'),
    ('bob', 'bob@example.com', 'hashed_password_2'),
    ('charlie', 'charlie@example.com', 'hashed_password_3');

INSERT INTO devices (user_id, device_name, device_type, serial_number, ip_address, mac_address, status, last_online, purchase_date, warranty_expiry, location, firmware_version) VALUES
    (1, 'Laptop A', 'Laptop', 'SN123456', '192.168.1.10', '00:1A:2B:3C:4D:5E', 'active', NOW(), '2022-01-15', '2025-01-15', 'Office', '1.2.3'),
    (1, 'Phone A', 'Smartphone', 'SN789012', '192.168.1.11', '00:1A:2B:3C:4D:5F', 'active', NOW(), '2023-05-10', '2026-05-10', 'Home', '1.0.1'),
    (1, 'Router A', 'Router', 'SN345678', '192.168.1.1', '00:1A:2B:3C:4D:60', 'active', NOW(), '2021-07-20', '2024-07-20', 'Office', '3.4.5'),
    (2, 'Laptop B', 'Laptop', 'SN654321', '192.168.2.10', '00:1A:2B:3C:4D:61', 'inactive', NOW(), '2020-09-10', '2023-09-10', 'Lab', '2.1.0'),
    (2, 'Tablet A', 'Tablet', 'SN901234', '192.168.2.12', '00:1A:2B:3C:4D:62', 'active', NOW(), '2022-03-05', '2025-03-05', 'Office', '1.3.2'),
    (2, 'Smartwatch A', 'Smartwatch', 'SN567890', NULL, '00:1A:2B:3C:4D:63', 'repair', NULL, '2021-11-30', '2024-11-30', 'Warehouse', '0.9.5'),
    (3, 'Desktop A', 'Desktop', 'SN098765', '192.168.3.10', '00:1A:2B:3C:4D:64', 'active', NOW(), '2023-06-25', '2026-06-25', 'Office', '2.0.0'),
    (3, 'Printer A', 'Printer', 'SN432109', '192.168.3.15', '00:1A:2B:3C:4D:65', 'inactive', NOW(), '2019-12-15', '2022-12-15', 'IT Room', '1.1.7'),
    (3, 'Server A', 'Server', 'SN876543', '192.168.3.20', '00:1A:2B:3C:4D:66', 'active', NOW(), '2020-02-28', '2025-02-28', 'Data Center', '4.5.6'),
    (3, 'Smart TV A', 'Smart TV', 'SN210987', '192.168.3.30', '00:1A:2B:3C:4D:67', 'decommissioned', NULL, '2018-08-19', '2021-08-19', 'Meeting Room', '3.2.1');
