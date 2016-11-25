#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import gzip
import shutil
from json import loads, dumps
import tweepy

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

PAGE_LEN = 100

class Twistorpy(object):

    """ Clase Twistorpy """

    def __init__(self, _user):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        self.user = _user

    def get_tweet(self, _id):
        """ retrive tweet with the given id """
        return self.api.get_status(_id)._json

    def get_page_tweets(self, page):
        """ retrive page with PAGE_LEN tweets"""
        return [t._json for t in self.api.user_timeline(self.user, count=PAGE_LEN, page=page)]


    #def id_present(self, _id,tweets):
    #return _id in [t2['id'] for t2 in tweets]
    #def tweet_present(tweet, tweets):
    #    return id_present(tweet['id'], tweets)

    def id_present(self,  id):
        """ TODO: DB strucure must be defined before complete this method """
        return False

    def tweet_present(self, tweet):
        """ TODO: DB strucure must be defined before complete this method """
        return False

    def parse_ids_file(self,ids_path):
        """ Obtaining tweets corresponding to the ids in the given file """
        new_ids = []
        print('Parsing ids from file...')
        ids_file = open(ids_path, 'r')
        for l in ids_file.read().split('\n'):
            if l.strip():
                try:
                    _id = int(l)
                    if not self.id_present(_id):
                        new_ids.append(_id)
                        print('New id found:', _id)
                except KeyboardInterrupt:
                    raise
                except Exception as err:
                    print('Error parsing line:')
                    print(l)
                    print(str(err))
        ids_file.close()

        if new_ids:
            print('Getting %i new tweets...' % len(new_ids))

            for _id in new_ids:
                import time
                import random
                time.sleep(random.random())
                try:
                    print('Adding tweet with id', _id)
                    tweet = self.get_tweet(_id)
                    if not self.tweet_present(tweet):
                        tweets.append(tweet)
                except KeyboardInterrupt:
                    raise
                except Exception as err:
                    print('Error getting tweet')
                    print(str(err))



    def parse_page(self,page):
        """ Parsing new tweets from a page """
        print('Parsing new tweets from page', page, '...')
        tweets=[]
        try:
            page_tweets = self.get_page_tweets(page)
            if page_tweets:
                original_count = len(tweets)
                for t in page_tweets:
                    if not self.tweet_present(t):
                        tweets.append(t)
                print('Added', len(tweets) - original_count, 'new tweets')
                return OK
            else:
                print('Page is empty')
                return EMPTY
        except KeyboardInterrupt:
            raise
        except Exception as err:
            print('Error reading page')
            print(str(err))
            return ERROR


    def parse_all_pages(self):
        """ Retreive all the tweets from the user account """
        page = 1
        retries = 0
        while True:
            result = self.parse_page(page)
            if result == OK:
                page += 1
                retries = 0
            elif result == ERROR:
                if retries < 5:
                    retries += 1
                else:
                    print('Stopped after 5 errors with the same page')
                    break
            elif result == EMPTY:
                break


if __name__ == '__main__':

    if len(sys.argv) not in (3, 4):
        print('''USAGE:
    python twistorpy.py TWITTER_USER HISTORY_FILE_PATH [EXTRA_IDS_FILE_PATH]

    HISTORY_FILE_PATH:
    Is the path for the json file. If the file doesn't exist, it will be created,
    if it already exists, only new tweets will be added to the file.

    EXTRA_IDS_FILE_PATH: (optional)
    You can create a txt file with tweets ids, and those tweets will be downloaded
    and added to the history if they don't exist.
    (each line of the file must be a different tweet id)
    ''')
        sys.exit(1)

    OK, EMPTY, ERROR = range(3)
    # TODO: history_path ya no sería necesario porque se toma desde DB
    user, history_path = sys.argv[1:3]
    twitter = Twistorpy(user)
    #backup_history(history_path)
    #tweets = read_history(history_path) or []

    try:
        if len(sys.argv) == 4:
            ids_path = sys.argv[-1]
            twitter.parse_ids_file(ids_path)
        else:
        # con fines de optimizar red, si se da un ids_path, se obtienen solo los tweets
        # especificados por el mismo, de lo contrario, se obtienen todos los existentes
            twitter.parse_all_pages()

        # TODO: implementar save_history según como quede la DB
        #save_history(tweets, history_path)

    except KeyboardInterrupt:
        print('Stopped by the user.')
        try:
            pass
        #  save_history(tweets, history_path)
        except Exception as err:
            print('Error saving history file, may be corrupted')
            print(str(err))
        sys.exit(0)
