#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import sys
import shutil
from urllib2 import urlopen
from json import loads, dumps

TWEET_URL = 'https://api.twitter.com/1/statuses/show/%i.json'
PAGE_URL = 'https://api.twitter.com/1/statuses/user_timeline.json?screen_name=%s&include_rts=true&count=%i&page=%i'
PAGE_LEN = 100

def needs_history_file(f):
    def new_f(history_path):
        if os.path.exists(history_path):
            return f(history_path)
        else:
            print 'History file not found'
    return new_f

@needs_history_file
def read_history(history_path):
    print 'Reading history file...'
    history = open(history_path, 'r')
    tweets = loads(history.read())
    history.close()
    print 'Done'
    return tweets

@needs_history_file
def backup_history(history_path):
    print 'Creating history backup...'
    shutil.copy(history_path, history_path + '.bak')
    print 'Done'

def save_history(tweets, history_path):
    history = open(history_path, 'w')
    history.write(dumps(tweets, indent=4))
    history.close()

def get_tweet(_id):
    return loads(urlopen(TWEET_URL % _id).read())

def get_page_tweets(user, page):
    return loads(urlopen(PAGE_URL % (user, PAGE_LEN, page)).read())

def id_present(_id, tweets):
    return _id in [t2['id'] for t2 in tweets]

def tweet_present(tweet, tweets):
    return id_present(tweet['id'], tweets)

def parse_ids_file(ids_path, tweets):
    new_ids = []
    print 'Parsing ids from file...'
    ids_file = open(ids_path, 'r')
    for l in ids_file.read().split('\n'):
        if l.strip():
            try:
                _id = int(l)
                if not id_present(_id, tweets):
                    new_ids.append(_id)
                    print 'New id found:', _id
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except:
                print 'Error parsing line:'
                print l
    ids_file.close()

    if new_ids:
        print 'Getting new tweets...'

        for _id in new_ids:
            try:
                print 'Adding tweet with id', _id
                t = get_tweet(_id)
                if not tweet_present(t, tweets):
                    tweets.append(t)
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except:
                print 'Error getting tweet'

OK, EMPTY, ERROR = range(3)

def parse_page(user, page, tweets):
    print 'Parsing new tweets from page', page, '...'
    try:
        page_tweets = get_page_tweets(user, page)
        if page_tweets:
            original_count = len(tweets)
            for t in page_tweets:
                if not tweet_present(t, tweets):
                    tweets.append(t)
            print 'Added', len(tweets) - original_count, 'new tweets'
            return OK
        else:
            print 'Page is empty'
            return EMPTY
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except:
        print 'Error reading page'
        return ERROR

def parse_all_pages(user, tweets):
    page = 1
    while True:
        result = parse_page(user, page, tweets)
        if result == OK:
            page += 1
        elif result == EMPTY:
            break

if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        print '''USE:
python twistory.py TWITTER_USER HISTORY_FILE_PATH [EXTRA_IDS_FILE_PATH]'

HISTORY_FILE_PATH:
Is the path for the json file. If the file doesn't exist, it will be created,
if it already exists, only new tweets will be added to the file.

EXTRA_IDS_FILE_PATH: (optional)
You can create a txt file with tweets ids, and those tweets will be downloaded
and added to the history if they don't exist.
'''
        sys.exit(1)

    user, history_path = sys.argv[1:3]

    backup_history(history_path)
    tweets = read_history(history_path)

    try:
        if len(sys.argv) == 4:
            ids_path = sys.argv[-1]
            parse_ids_file(ids_path, tweets)
            save_history(tweets, history_path)

        parse_all_pages(user, tweets)

    except KeyboardInterrupt:
        print 'Stopping and saving history file...'
        try:
            save_history(tweets, history_path)
        except:
            print 'Error saving history file, may be corrupted'
        sys.exit(0)


