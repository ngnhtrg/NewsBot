import urllib.request
import re
import html
import json
from bs4 import BeautifulSoup
from datetime import datetime


date = datetime(year=2021, month=5, day=4, hour=20, minute=55)


def get_site_from_url(url):
    response = urllib.request.urlopen(url)
    HTML = response.read()
    HTML = HTML.decode('utf-8')
    return HTML


def convert_to_time(time_str):
    time = re.split(r' |, |:', time_str)
    hour = int(time[-2])
    minute = int(time[-1])

    if len(time) != 2:
        month = int(months[time[1]])
        day = int(time[0])
    else:
        month = datetime.now().month
        day = datetime.now().day

    if len(time) == 5:
        year = int(time[2])
    else:
        year = datetime.now().year
    return datetime(year, month, day, hour, minute)


def get_text(HTML):
    string = re.findall(r'<p.*?>(.*?)<\/p>', HTML)
    _text = ''
    for item in string:
        _text += ' ' + item
    _text = re.sub('<[^>]+>', '', _text)
    _text = html.unescape(_text)
    return _text


def get_tags(HTML):
    soup = BeautifulSoup(HTML, "html.parser")
    tags = set([tag.name for tag in soup.find_all()])
    return json.dumps(list(tags))


url1 = 'https://www.rbc.ru/story/'
url2 = 'http://www.interfax.ru/story/'

site = get_site_from_url(url1)

with open('data1.txt', 'w', encoding='utf-8') as f:
    f.write(site)

months = {
    'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4,
    'мая': 5, 'июн': 6, 'июл': 7, 'авг': 8,
    'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12}

name_of_topics = re.findall(r'<meta itemprop="name" content="(.*)">', site)

url_of_topics = re.findall(r'<meta itemprop="url" content="(.*)">', site)

description_of_topics = []
articles = []
topics_time = []
arcticles_in_topics = []
for url in url_of_topics:
    site = get_site_from_url(url)
    descript = re.findall(
        r'<meta name="Description" content="(.*)" />', site)

    description_of_topics.append(descript[0])

    articles_url = re.findall(
        r'<meta itemprop="url" content="(.*)">', site)

    articles_name = re.findall(
        r'<meta itemprop="name" content="(.*)">', site)

    articles_update_time_str = re.findall(
        r'<span class="item__category">(.*)</span>', site)

    arcticles_in_topics.append('\n'.join(articles_name))
    articles_update_time = []
    articles_texts = []
    articles_tags = []

    for item in articles_update_time_str:
        articles_update_time.append(convert_to_time(item))
    topics_time.append(sorted(articles_update_time)[-1])
    for item in articles_url:
        HTML = get_site_from_url(item)
        articles_texts.append(get_text(HTML))
        articles_tags.append(get_tags(HTML))
    articles.extend(zip(
        articles_url, articles_name, articles_update_time,
        articles_texts, articles_tags))


topics = zip(
    name_of_topics, url_of_topics, description_of_topics,
    arcticles_in_topics, topics_time)
