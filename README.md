# 📊 YouTube Channel Monitor

A **full-stack Flask project** that connects to the **YouTube Data API v3**, stores data in **MySQL**, performs **sentiment analysis on comments**, and predicts **7-day subscriber growth** using **machine learning**.  

This project lets you enter a **YouTube Channel ID or Username**, and it fetches **live channel stats, logo, banner, description, latest videos, and comments**. The results are displayed in an interactive **dashboard with Chart.js visualizations**.  

---

## 🚀 Features

- 🔹 Enter **YouTube Channel ID/Username** → Directly view dashboard (no login required).  
- 🔹 Fetch live channel details:  
  - Channel **name, logo, banner, description**  
  - Stats: **Subscribers, Views, Videos**  
- 🔹 Show **last 5 videos** (title, views, likes, comments).  
- 🔹 Perform **sentiment analysis** (Positive/Neutral/Negative) on the last 5 comments.  
- 🔹 Predict **next 7 days subscriber growth** using **Linear Regression**.  
- 🔹 Display interactive **charts** using Chart.js:  
  - Subscriber growth + prediction  
  - Video performance (views, likes, comments)  
  - Sentiment distribution (pie chart)  
- 🔹 Store all fetched data into **MySQL database**.  
- 🔹 Responsive UI built with **Bootstrap 5** and **Dark Mode toggle**.  

---

## 📂 Project Structure
YouTubeChannelMonitor/
│── app.py # Flask backend (routes, API, ML, DB)
│── config.py # API key + MySQL credentials
│── requirements.txt # Python dependencies
│── README.md # Documentation
│
├── templates/
│ ├── index.html # Input form for channel ID
│ ├── dashboard.html # Dashboard page (stats + charts)
│
├── static/
│ ├── css/
│ │ └── style.css # Custom styles
│ ├── js/
│ │ └── charts.js # Chart.js rendering logic
│ └── images/
│ └── placeholder.png

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows


3️⃣ Install Dependencies
pip install -r requirements.txt


4️⃣ Configure API Key & Database
Open config.py and add your details:

5️⃣ Setup Database
Run MySQL and create database:
CREATE DATABASE youtube_monitor;
The app will auto-create tables (channels, video_stats, sentiments).

6️⃣ Run Flask App
python app.py


📊 Example Workflow

Go to Home Page → Enter YouTube Channel ID.

Redirected to Dashboard → Shows:

Channel logo, banner, description, stats

Latest 5 videos (cards)

Charts for subscriber growth & video performance

Last 5 comments with sentiment analysis

7-day prediction of subscriber growth


📦 Dependencies

Flask

Flask-MySQLdb

requests

scikit-learn

nltk (VADER sentiment)

Chart.js (frontend)

Bootstrap 5

pip install flask flask-mysqldb requests scikit-learn nltk


📈 Future Enhancements

Add multi-channel comparison dashboard

Enable scheduled daily updates (Celery/CRON)

Export reports as PDF

Deploy to Heroku/Render with ClearDB MySQL


         ********👨‍💻 Author********:
******Developed by Shreyash Patil ✨******