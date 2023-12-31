import datetime
import feedparser
import json
from urllib.request import urlopen
from urllib.parse import quote

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'
             }

DEFAULT = {'publication': 'bbc', 'city': 'London,UK'}
WEATHER_URL = f'https://api.openweathermap.org/data/2.5/weather?lat=33.44&lon=-94.04&appid={api_key}'


""" @app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed['entries'][0]
    return render_template("home.html", articles=feed['entries']) """


""" @app.route("/")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = 'bbc'
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    weather = get_weather("London,UK")
    return render_template("home.html", articles=feed['entries'], weather=weather) """


@app.route("/")
def home():
    # get customized headlines, base on user input or default
    publication = get_value_with_fallback("publication")

    articles = get_news(publication)
    # get cutomized weather base on user input or default
    city = get_value_with_fallback('city')

    weather = get_weather(WEATHER_URL)

    response = make_response(render_template(
        "home.html", articles=articles, weather=weather))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULT['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = quote(query)
    url = WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name']
                   }
    return weather


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
