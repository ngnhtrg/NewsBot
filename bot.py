import logging
import sqlite3
import re
from collections import defaultdict
from telegram.ext import Updater, CommandHandler


MAX_MESSAGE_LENGTH = 4096
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_parts_of_text(text, character):
    """
    If text is too long, exceed MAX_MESSAGE_LENGTH,
    we have to separate into small texts (part)
    :param text: text to be handled
    :param character: character used to separate text
    """
    _text = text
    if len(text) > MAX_MESSAGE_LENGTH:
        parts = []
        while len(_text) > MAX_MESSAGE_LENGTH:
            part = _text[:MAX_MESSAGE_LENGTH]
            first_lnbr = part.rfind(character)
            parts.append(part[:first_lnbr + 1])
            _text = _text[first_lnbr + 1:]
        parts.append(_text)
        return parts
    else:
        return text


def select_new_docs(conn, number_of_docs):
    """
    Select a given number of newest documents
    :param conn: A SQLite database connection
    :param number_of_docs: number of documents to select
    """
    query = '''SELECT Heading, LastUpdateTime
               FROM doc
               ORDER BY LastUpdateTime DESC
               '''
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows[:number_of_docs]


def select_new_topics(conn, number_of_topics):
    """
    Select a given number of newest topics
    :param conn: A SQLite database connection
    :param number_of_topics: number of topics to select
    """
    query = '''SELECT name
               FROM topic
               ORDER BY LastUpdateTime DESC
               '''
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows[:number_of_topics]


def select_new_doc_from_topic(conn, topic_name, number_of_docs):
    """
    Select a given number of newest topics from the topic
    :param conn: A SQLite database connection
    :param topic_name: topic to select
    :param number_of_docs: number of topics to select
    """

    query = '''SELECT row.articles
               FROM topic row
               WHERE row.name = ?
               '''
    cur = conn.cursor()
    cur.execute(query, (topic_name,))
    docs = cur.fetchall()[0][0]
    list_of_docs = docs.split('\n')
    return list_of_docs[:number_of_docs]


def select_doc(conn, doc_title):
    """
    Get a document by the given title
    :param conn: A SQLite database connection
    :param doc_title: title of document
    """

    query = '''SELECT row.text
               FROM doc row
               WHERE row.Heading = ?
               '''
    cur = conn.cursor()
    cur.execute(query, (doc_title,))
    text = cur.fetchall()
    return text[0][0]


def select_topic(conn, topic_name):
    """
    Get a topic by the given title
    :param conn: A SQLite database connection
    :param topic_name: name of topic
    return description of topic
    """

    query = '''SELECT row.description
               FROM topic row
               WHERE row.name = ?
               '''
    cur = conn.cursor()
    cur.execute(query, (topic_name,))
    text = cur.fetchall()
    return text[0][0]


def select_words_best_describe(conn, topic_name, number_of_words):
    """
    Select words that best describe the topic
    :param conn: A SQLite database connection
    :param topic_name: name of topic
    :param number_of_words: number of words to select
    return: list of words
    """

    query = '''SELECT row.articles
           FROM topic row
           WHERE row.name = ?
           '''
    cur = conn.cursor()
    cur.execute(query, (topic_name,))
    docs = cur.fetchall()[0][0]
    list_of_docs = docs.split('\n')
    dic = defaultdict(int)
    for item in list_of_docs:
        text = select_doc(conn, item)
        text = re.split(r', | ', text)
        for word in text:
            word = ''.join(ch for ch in word if ch.isalnum())
            if len(word) <= 3:
                continue
            dic[word] += 1
    dic = sorted(dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    key_word = []
    for index in range(number_of_words):
        key_word.append(dic[index][0])
    return key_word


def get_distribution_from_doc(conn, doc_title):
    """
    Get frequency and length of words distribution of given document
    :param conn: A SQLite database connection
    :param doc_title: title of document
    return: frequency distribution, length distribution (type dict)
    """

    text = select_doc(conn, doc_title)
    text = re.split(r', | ', text)
    freq_dic = defaultdict(int)
    len_dic = defaultdict(int)
    for word in text:
        word = ''.join(ch for ch in word if ch.isalnum())
        if len(word) == 0:
            continue
        len_dic[str(len(word))] += 1
        freq_dic[word] += 1

    freq_dic = sorted(
        freq_dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    len_dic = sorted(
        len_dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    return freq_dic, len_dic


def get_discribe_from_topic(conn, topic_name):
    """
    Get informations from topic
    :param conn: A SQLite database connection
    :param topic_name: name of topic
    return: number of documents in topic
            average of length of documents
            frequency distribution
            length distribution
    """

    query = '''SELECT row.articles
               FROM topic row
               WHERE row.name = ?
               '''
    cur = conn.cursor()
    cur.execute(query, (topic_name,))
    articles = cur.fetchall()[0][0]

    articles = re.split(r'\n', articles)
    number_docs = len(articles)
    sum_of_len_docs = 0
    freq_dic = defaultdict(int)
    len_dic = defaultdict(int)
    for item in articles:
        text = select_doc(conn, item)
        sum_of_len_docs += len(text)
        doc_freq_dic, doc_len_dic = get_distribution_from_doc(conn, item)
        for (key, value) in doc_freq_dic:
            freq_dic[key] += value

        for (key, value) in doc_len_dic:
            len_dic[key] += value

    average_of_len = sum_of_len_docs / number_docs

    freq_dic = sorted(
        freq_dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    len_dic = sorted(
        len_dic.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    return number_docs, average_of_len, freq_dic, len_dic


# Define a few command handlers
# These usually take the two arguments update and
# context. Error handlers also receive the raised
# TelegramError object in error
def start(update, context):
    """Send a message when the command /start is issued."""
    text = """
Welcome to NewsBot
This Bot will give you news from site https://www.rbc.ru/story/
Check /help for more informations
"""
    update.message.reply_text(text)


def help(update, context):
    """Send a message when the command /help is issued."""
    text = """
These are what I can do:
/new_docs <N> - показать N самых свежих новостей
/new_topics <N> - показать N самых свежих тем
/topic <topic_name> - показать описание темы и заголовки
5 самых свежих новостей в этой теме
/doc <doc_title> - показать текст документа с заданным заголовком
/words <topic_name> - показать 5 слов, лучше всего характеризующих тему
/describe_doc <doc_title> - вывести статистику по документу
/describe_topic <topic_name> - вывести статистику по теме
"""
    update.message.reply_text(text)


def new_docs(update, context):
    """Show N latest news"""
    try:
        number1 = int(context.args[0])
        with sqlite3.connect('data.db') as conn:
            rows = select_new_docs(conn, number1)
            texts = ''
            index = 1
            for item in rows:
                texts += '{}. [{}] {}\n'.format(index, item[1][:-3], item[0])
                index += 1
            update.message.reply_text(texts)
    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def new_topics(update, context):
    """Show N latest topics"""
    try:
        number1 = int(context.args[0])
        with sqlite3.connect('data.db') as conn:
            rows = select_new_topics(conn, number1)
            texts = ''
            index = 1
            for item in rows:
                texts += '{}. {}\n'.format(index, item[0])
                index += 1
            update.message.reply_text(texts)
    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def topic(update, context):
    """
    Show topic description and headlines
    of the 5 most recent news in this topic
    """
    try:
        topic_name = ' '.join(list(context.args))
        with sqlite3.connect('data.db') as conn:
            descript = select_topic(conn, topic_name)
            rows = select_new_doc_from_topic(conn, topic_name, 5)
            texts = 'Заголовки 5 самых свежих новостей в этой теме:\n'
            for index, value in enumerate(rows, start=1):
                texts += '{}. {}\n'.format(index, value)
            update.message.reply_text(descript + '\n' + texts)

    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def doc(update, context):
    """Show the text of the document with the given title"""
    try:
        doc_title = ' '.join(list(context.args))
        with sqlite3.connect('data.db') as conn:
            text = select_doc(conn, doc_title)
            if len(text) > MAX_MESSAGE_LENGTH:
                parts = get_parts_of_text(text, '.')
                for part in parts:
                    update.message.reply_text(part)
            else:
                update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def words(update, context):
    """Show 5 words that best describe the topic"""
    try:
        topic_name = ' '.join(list(context.args))
        text = '5 слов, лучше всего характеризующих тему:\n'
        with sqlite3.connect('data.db') as conn:
            key_words = select_words_best_describe(conn, topic_name, 5)
            for word in key_words:
                text += word + ', '
            text = text[:-2]
        update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def describe_doc(update, context):
    """Display document statistics"""
    try:
        doc_title = ' '.join(list(context.args))
        with sqlite3.connect('data.db') as conn:
            freq_dic, len_dic = get_distribution_from_doc(conn, doc_title)
            freq_distr = 'Распределение частот слов:\n'
            len_distr = 'Распределение длин слов:\n'
            for (key, value) in freq_dic:
                freq_distr += '{}: {}'.format(key, value)
            for (key, value) in len_dic:
                len_distr += '{}: {}'.format(key, value)
            text = '{}\n{}\n{}'.format(
                                doc_title, freq_distr[:-2], len_distr[:-2])
            update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def describe_topic(update, context):
    """Display statistics on a topic"""
    try:
        topic_name = ' '.join(list(context.args))
        with sqlite3.connect('data.db') as conn:
            discriber = get_discribe_from_topic(conn, topic_name)
            number_docs, average_of_len, freq_dic, len_dic = discriber
            freq_distr = 'Распределение частот слов:\n'
            len_distr = 'Распределение длин слов:\n'
            for (key, value) in freq_dic:
                freq_distr += '{}: {}, '.format(key, value)
            for (key, value) in len_dic:
                len_distr += '{}: {}, '.format(key, value)
            number_docs_str = 'Количество документов в теме: '
            number_docs_str += '{}\n'.format(number_docs)
            average_of_len_str = 'Cредняя длина документов: '
            average_of_len_str += '{}\n'.format(average_of_len)
            text = '{}\n{}{}'.format(
                                topic_name, number_docs_str, number_docs_str)
            text += '{}\n{}\n'.format(freq_distr[:-2], len_distr[:-2])

            if len(text) > MAX_MESSAGE_LENGTH:
                parts = get_parts_of_text(text, ',')
                for part in parts:
                    update.message.reply_text(part)
            else:
                update.message.reply_text(text)
    except (IndexError, ValueError):
        update.message.reply_text('Input Error!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    api = '1774694275:AAFlE1pz2_2gCNciPlVT-tidq2YQbUir5CM'
    updater = Updater(api, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("new_docs", new_docs))
    dp.add_handler(CommandHandler("new_topics", new_topics))
    dp.add_handler(CommandHandler("topic", topic))
    dp.add_handler(CommandHandler("doc", doc))
    dp.add_handler(CommandHandler("words", words))
    dp.add_handler(CommandHandler("describe_doc", describe_doc))
    dp.add_handler(CommandHandler("describe_topic", describe_topic))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
