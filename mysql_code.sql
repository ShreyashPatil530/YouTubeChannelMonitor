CREATE DATABASE IF NOT EXISTS youtube_monitor;
USE youtube_monitor;
DROP DATABASE youtube_monitor;
-- Drop tables if they exist (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS sentiments;
DROP TABLE IF EXISTS video_stats;
DROP TABLE IF EXISTS channels;

-- Create channels table
CREATE TABLE channels (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    thumbnail_url TEXT,
    banner_url TEXT,
    subscriber_count INT,
    view_count INT,
    video_count INT,
    last_updated TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create video_stats table
CREATE TABLE video_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id VARCHAR(255),
    video_id VARCHAR(255),
    title TEXT,
    view_count INT,
    like_count INT,
    comment_count INT,
    published_at TIMESTAMP,
    INDEX channel_idx (channel_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create sentiments table
CREATE TABLE sentiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id VARCHAR(255),
    video_id VARCHAR(255),
    comment_id VARCHAR(255),
    comment_text TEXT,
    positive_score FLOAT,
    neutral_score FLOAT,
    negative_score FLOAT,
    compound_score FLOAT,
    sentiment VARCHAR(10),
    INDEX channel_idx (channel_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Add foreign key constraints (optional)
ALTER TABLE video_stats
ADD CONSTRAINT fk_video_stats_channel
FOREIGN KEY (channel_id) REFERENCES channels(id)
ON DELETE CASCADE;

ALTER TABLE sentiments
ADD CONSTRAINT fk_sentiments_channel
FOREIGN KEY (channel_id) REFERENCES channels(id)
ON DELETE CASCADE;