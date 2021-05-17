### News Bot

#### Usage
Username: @ngnhtrg_news_bot

This bot can get data from site [https://www.rbc.ru/story/](https://www.rbc.ru/story/)
and answer for some requests

#### Commands:
```
/new_docs <N> - show N latest news
/new_topics <N> - show N latest topics
/topic <topic_name> - show topic description and headlines of the 5 most recent news in this topic
/doc <doc_title> - show the text of the article with the given title
/words <topic_name> - show 5 words that best describe the topic
/describe_doc <doc_title> - display document statistics
/describe_topic <topic_name> - display statistics on a topic
```
#### Clone:

```bash
# Clone repository
git clone https://github.com/ngnhtrg/NewsBot.git
cd NewsBot/
git branch dev
git pull origin dev
# Install requirements
pip install -r requirements.txt
# Parse site
python3 db.py
# Run bot
python3 bot.py
```

Here are some screen shots:

![alt text](https://github.com/ngnhtrg/NewsBot/blob/dev/demo/start.png)

![alt text](https://github.com/ngnhtrg/NewsBot/blob/dev/demo/help.png)

![alt text](https://github.com/ngnhtrg/NewsBot/blob/dev/demo/new_docs.png)

![alt text](https://github.com/ngnhtrg/NewsBot/blob/dev/demo/new_topics.png)

![alt text](https://github.com/ngnhtrg/NewsBot/blob/dev/demo/topic.png)

