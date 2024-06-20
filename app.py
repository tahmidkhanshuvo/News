from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import feedparser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
db = SQLAlchemy(app)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(100), nullable=False)

db.create_all()

def fetch_rss_feeds():
    feed_urls = [
        'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'http://feeds.bbci.co.uk/news/rss.xml',
        'http://rss.cnn.com/rss/edition.rss',
        'https://www.jagonews24.com/rss/rss.xml',
        # Add more RSS feed URLs here
    ]

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if not News.query.filter_by(link=entry.link).first():
                news_item = News(title=entry.title, link=entry.link, source=feed.feed.title)
                db.session.add(news_item)
                db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_rss_feeds, trigger="interval", minutes=30)
scheduler.start()

@app.route('/')
def home():
    news_items = News.query.order_by(News.id.desc()).all()
    return render_template('home.html', news=news_items)

if __name__ == '__main__':
    app.run(debug=True)
