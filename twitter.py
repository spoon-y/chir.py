#!/usr/bin/env python
# Chir.py Twitter Bot
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/chir.py
# twitter.py

import random
import threading
import time

import tweepy

import config
import debug
import functions

api = None
me  = None

def login():
    global api, me
    try:
        auth = tweepy.OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
        auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        me  = api.me()
    except tweepy.TweepError:
        debug.error_exit('Failed to login to Twitter!')

def stats():
    debug.action('SceenName\t: %s'  % me.screen_name)
    debug.action('Registered\t: %s' % me.created_at)
    debug.action('Favorites\t: %s'  % me.favourites_count)
    debug.action('Following\t: %s'  % me.friends_count)
    debug.action('Followers\t: %s'  % me.followers_count)
    debug.action('Tweets\t\t: %s'   % me.statuses_count)

class boost_loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            debug.action('Boost loop starting up.')
            try:
                #if 'boost_tweet' in locals(): api.destroy_status(boost_tweet.id)
                #boost_tweet = api.update_status('Support our Twitter! #' + ' #'.join(config.boost_keywords))
                debug.alert('Re-posted boost tweet... jk')
            except tweepy.TweepError as ex:
                debug.error('Error occured in the boost loop', ex)
            finally:
                random.shuffle(list(config.boost_keywords))
                time.sleep(60*5)

class favorite_loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            debug.action('Favorite loop starting up.')
            try:
                for tweet in tweepy.Cursor(api.home_timeline, exclude_replies=True).items(50):
                    if tweet.user.screen_name != me.screen_name:
                        if not tweet.favorited:
                            if random.choice([True, False, False, False, False]):
                                api.create_favorite(tweet.id)
                                debug.alert('Favorited a friends tweet!')
                                time.sleep(60*20)
            except tweepy.TweepError as ex:
                debug.error('Error occured in the favorite loop!', ex)
            finally:
                debug.alert('Favorite loop sleeping for 15 minutes.')
                time.sleep(60*15)

class follow_loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            me = api.me()
            debug.action('Follow loop starting up.')
            try:
                followers = api.followers_ids(me.screen_name)
                friends   = api.friends_ids(me.screen_name)
                for follower in followers:
                    if not follower in friends:
                        debug.action('Found follower not being followed.')
                        api.create_friendship(follower)
                        #api.send_direct_message(screen_name=follower, text='Thanks for following our Twitter. Be sure to share us with your friends & keep up with the latest sports news!')
                        time.sleep(60)
                if me.friends_count / me.followers_count > 10:
                    debug.action('Following to follower ratio is off! Starting the unfollow loop...')
                    unfollow_loop()

            except tweepy.TweepError as ex:
                debug.error('Error occured in the follow loop!', ex)
            finally:
                debug.alert('Follow loop sleeping for 15 minutes.')
                time.sleep(60*15)

def main_loop():
    stats()
    debug.action('Let\'s roll.')
    #boost_loop().start()
    #time.sleep(15)
    follow_loop().start()
    time.sleep(5)
    favorite_loop().start()
    time.sleep(5)
    news_loop().start()
    time.sleep(5)
    search_loop().start()
    
class news_loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            debug.action('News loop starting up.')
            try:
                news   = functions.get_news()
                debug.alert('Got the news!')
                tweets = list()
                for item in tweepy.Cursor(api.user_timeline, exclude_replies=True).items(50):
                    tweets.append(item.text[:20])
                    dupe = news[:20]
                    if dupe not in tweets:
                        api.update_status(news)
                        debug.alert('A tweet has been posted.')
                        time.sleep(60*15)
            except tweepy.TweepError as ex:
                debug.error('Error occured in the news loop.', ex)
            finally:
                debug.alert('News loop sleeping for a minute.')
                time.sleep(60)

class search_loop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        query_keywords = list()
        for item in config.news_keywords:
            query_keywords = query_keywords + list(config.news_keywords[item])
        query_keywords = query_keywords + list(config.boost_keywords)
        while True:
            debug.action('Search loop starting up.')
            me = api.me()
            if me.friends_count / me.followers_count < 10:
                try:
                    query = random.choice(query_keywords)
                    for item in api.search(q='#' + query, count=50, lang='en', result_type='mixed'):
                        if me.friends_count / me.followers_count < 10:
                            if not item.user.following:
                                try:
                                    #api.create_favorite(item.id)
                                    api.create_friendship(item.user.screen_name)
                                    me = api.me()
                                    debug.alert('Followed a similar twitter! Friends/Followers: ' + str(me.friends_count) + '/' + str(me.followers_count))
                                    time.sleep(60)
                                except tweepy.TweepError as ex:
                                    debug.error('Unknown error occured in the search loop!', ex)
                except tweepy.TweepError as ex:
                    debug.error('Error occured in the search loop!', ex)
                finally:
                    debug.alert('Search loop sleeping for 15 minutes.')
                    time.sleep(60*15)
            else:
                debug.alert('Search loop sleeping for 15 minutes.')
                time.sleep(60*15)

def unfollow_loop():
    try:
        me = api.me()
        followers = me.followers_ids(me.screen_name)
        friends   = me.friends_ids(me.screen_name)
        for friend in friends:
            if me.friends_count / me.followers_count > 10:
                if friend not in followers:
                    api.destroy_friendship(friend)
                    me = api.me()
                    debug.alert('Unfollowed an unsupporting friend!Friends/Followers: ' + str(me.friends_count) + '/' + str(me.followers_count))
                    time.sleep(30)
        debug.alert('Unfollow loop exited cleanly...')
    except tweepy.TweepError as ex:
        debug.error('Error occured in the unfollow loop!', ex)
