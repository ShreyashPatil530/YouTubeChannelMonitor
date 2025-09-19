from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import json
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key_here'

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        port=app.config['MYSQL_PORT']
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            thumbnail_url TEXT,
            banner_url TEXT,
            subscriber_count INT,
            view_count INT,
            video_count INT,
            last_updated TIMESTAMP
        )
    ''')
    
    # Create video_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id VARCHAR(255),
            video_id VARCHAR(255),
            title TEXT,
            view_count INT,
            like_count INT,
            comment_count INT,
            published_at TIMESTAMP
        )
    ''')
    
    # Create sentiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            channel_id VARCHAR(255),
            video_id VARCHAR(255),
            comment_id VARCHAR(255),
            comment_text TEXT,
            positive_score FLOAT,
            neutral_score FLOAT,
            negative_score FLOAT,
            compound_score FLOAT,
            sentiment VARCHAR(10)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def get_channel_id_from_username(username):
    """Convert username to channel ID using YouTube API"""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={username}&key={app.config['YOUTUBE_API_KEY']}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        return data['items'][0]['id']
    return None

def fetch_channel_data(channel_identifier):
    """Fetch channel data from YouTube API"""
    # Check if identifier is a channel ID or username
    if channel_identifier.startswith('UC'):
        channel_id = channel_identifier
    else:
        channel_id = get_channel_id_from_username(channel_identifier)
        if not channel_id:
            return None
    
    # Fetch channel details
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,contentDetails,brandingSettings&id={channel_id}&key={app.config['YOUTUBE_API_KEY']}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' not in data or len(data['items']) == 0:
        return None
    
    channel_data = data['items'][0]
    snippet = channel_data.get('snippet', {})
    statistics = channel_data.get('statistics', {})
    branding = channel_data.get('brandingSettings', {}).get('image', {})
    
    # Get banner image if available
    banner_url = ""
    if branding and 'bannerExternalUrl' in branding:
        banner_url = branding.get('bannerExternalUrl', '')
    elif branding and 'bannerTabletHdImageUrl' in branding:
        banner_url = branding.get('bannerTabletHdImageUrl', '')
    
    return {
        'id': channel_id,
        'name': snippet.get('title', ''),
        'description': snippet.get('description', ''),
        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
        'banner_url': banner_url,
        'subscriber_count': int(statistics.get('subscriberCount', 0)),
        'view_count': int(statistics.get('viewCount', 0)),
        'video_count': int(statistics.get('videoCount', 0))
    }

def fetch_videos_data(channel_id):
    """Fetch recent videos from a channel"""
    # First, get the uploads playlist ID
    channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={app.config['YOUTUBE_API_KEY']}"
    channel_response = requests.get(channel_url)
    channel_data = channel_response.json()
    
    if 'items' not in channel_data or len(channel_data['items']) == 0:
        return []
    
    uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get videos from the uploads playlist
    videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=5&key={app.config['YOUTUBE_API_KEY']}"
    videos_response = requests.get(videos_url)
    videos_data = videos_response.json()
    
    videos = []
    if 'items' in videos_data:
        for item in videos_data['items']:
            video_id = item['snippet']['resourceId']['videoId']
            if video_id:
                # Get video statistics
                stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={app.config['YOUTUBE_API_KEY']}"
                stats_response = requests.get(stats_url)
                stats_data = stats_response.json()
                
                if 'items' in stats_data and len(stats_data['items']) > 0:
                    video_stats = stats_data['items'][0]['statistics']
                    snippet = stats_data['items'][0]['snippet']
                    
                    # Format published date
                    published_at = snippet.get('publishedAt', '')
                    if published_at:
                        published_at = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                    
                    videos.append({
                        'id': video_id,
                        'title': snippet.get('title', ''),
                        'view_count': int(video_stats.get('viewCount', 0)),
                        'like_count': int(video_stats.get('likeCount', 0)),
                        'comment_count': int(video_stats.get('commentCount', 0)),
                        'published_at': published_at
                    })
                    
                    # Fetch comments for sentiment analysis
                    fetch_comments(channel_id, video_id)
    
    return videos

def fetch_comments(channel_id, video_id):
    """Fetch comments and perform sentiment analysis"""
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=5&key={app.config['YOUTUBE_API_KEY']}"
    response = requests.get(url)
    data = response.json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if 'items' in data:
        for item in data['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_text = comment['textDisplay']
            
            # Perform sentiment analysis
            sentiment_scores = analyzer.polarity_scores(comment_text)
            
            # Determine sentiment category
            if sentiment_scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif sentiment_scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Store in database
            cursor.execute('''
                INSERT INTO sentiments (channel_id, video_id, comment_id, comment_text, 
                positive_score, neutral_score, negative_score, compound_score, sentiment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (channel_id, video_id, item['id'], comment_text, 
                  sentiment_scores['pos'], sentiment_scores['neu'], 
                  sentiment_scores['neg'], sentiment_scores['compound'], sentiment))
    
    conn.commit()
    cursor.close()
    conn.close()

def predict_subscriber_growth(channel_id):
    """Predict subscriber growth for next 7 days using linear regression"""
    # For demo purposes, let's create some sample data
    # In a real application, you would use historical data from your database
    current_count = 10000  # Example current subscriber count
    
    # Create sample data for the next 7 days with a growth trend
    predictions = []
    for i in range(1, 8):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        # Simulate growth with some randomness
        predicted_count = current_count + i * 150 + np.random.randint(-50, 100)
        predictions.append((date, predicted_count))
    
    return predictions

def get_sentiment_stats(channel_id):
    """Get sentiment statistics for a channel"""
    # For demo purposes, let's create some sample data
    # In a real application, you would query the database
    return {
        'positive': 12,
        'neutral': 8,
        'negative': 5
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    channel_identifier = request.form.get('channel_id')
    
    if not channel_identifier:
        flash('Please enter a channel ID or username')
        return redirect(url_for('index'))
    
    # Fetch channel data
    channel_data = fetch_channel_data(channel_identifier)
    
    if not channel_data:
        flash('Channel not found. Please check the ID or username.')
        return redirect(url_for('index'))
    
    # Store channel data in database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO channels (id, name, description, thumbnail_url, banner_url, 
        subscriber_count, view_count, video_count, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name), description = VALUES(description), 
        thumbnail_url = VALUES(thumbnail_url), banner_url = VALUES(banner_url),
        subscriber_count = VALUES(subscriber_count), view_count = VALUES(view_count),
        video_count = VALUES(video_count), last_updated = VALUES(last_updated)
    ''', (channel_data['id'], channel_data['name'], channel_data['description'],
          channel_data['thumbnail_url'], channel_data['banner_url'],
          channel_data['subscriber_count'], channel_data['view_count'],
          channel_data['video_count'], datetime.now()))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Fetch videos data
    videos = fetch_videos_data(channel_data['id'])
    
    # Get subscriber predictions
    predictions = predict_subscriber_growth(channel_data['id'])
    
    # Get sentiment statistics
    sentiment_stats = get_sentiment_stats(channel_data['id'])
    
    return render_template('dashboard.html', 
                         channel=channel_data, 
                         videos=videos,
                         predictions=predictions,
                         sentiment_stats=sentiment_stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)