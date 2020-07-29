#!/usr/bin/python

# Utilities
import sys
import re
import random
import json
import numpy as np

# Botometer API
import botometer

# MongoDB functionality
from pymongo.errors import BulkWriteError
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne, UpdateMany, DeleteMany
from pymongo.bulk import BulkOperationBuilder
from bson import ObjectId

# Tweet API for friendships
import tweepy
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from collections import Counter

# Keys
RAPID_API_KEY1 = '1f55d0ab51msh268beee8ad68316p1d2487jsnad4f4c078ce1'
RAPID_API_KEY2 = '993c6874ebmshbca407607da9d84p187434jsn092252ca8935'
TWITTER_DEV_CONSUMER_KEY = 'VdGSvaMeaEiP05SCcV9KjnbAc'
TWITTER_DEV_CONSUMER_SECRET = 'liE7kQEF8RMIuCJ3qIi0JSU0mMHpg6f0Df2aGzJDqd7LyXrj5q'
TWITTER_DEV_ACCESS_TOKEN = '1204405321256570886-YX0aH39im3yif9DuoAF1boKxmD9GBH'
TWITTER_DEV_ACCESS_TOKEN_SECRET = 'r42UcOqPAjjVmoGvDcWo5DJefZfBWFKXZ8v8Gj1WwUIT2'


# Botometer and Twitter Keys for parallel processing
keys = {
    0: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=RAPID_API_KEY1, **{'consumer_key': TWITTER_DEV_CONSUMER_KEY, 'consumer_secret': TWITTER_DEV_CONSUMER_SECRET}),
    1: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=RAPID_API_KEY2, **{'consumer_key': TWITTER_DEV_CONSUMER_KEY, 'consumer_secret': TWITTER_DEV_CONSUMER_SECRET}),
}

# MongoDB parameters
mongoclient = MongoClient('127.0.0.1', 27017)
db = mongoclient.SFM

MINIMUM_BOTSCORE = 0.43


def get_user(user):

    message = "Checking:" + str(user) + " "
    try:
        # Tweepy request
        auth = tweepy.OAuthHandler(
            TWITTER_DEV_CONSUMER_KEY, TWITTER_DEV_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Obtain by username
        return api.get_user(user)

    except Exception as e:
        print(message+"Exception. User:", user, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)
        return False


def make_objid(text):
    """Makes an ObjectId of 4 bytes

    Keyword arguments:
    text -- string to be converted into Object ID
    """
    text = str(text)
    if not text.strip():
        return None
    try:
        return ObjectId(text.rjust(24, "0"))
    except Exception as ex:
        print(text, ex)
        return None


def get_botscore_by_userid(user_id):
    """
    Collects the botscore from Botometer

    Keyword arguments:
    user_id -- Twitter users' identificator
    """

    try:
        botometer_instance = random.choice(keys)
        consumer_key = botometer_instance.consumer_key
        result = botometer_instance.check_account(user_id)
        return UpdateOne({'_id': make_objid(user_id)},
                         {'$set': {'scores': result}},
                         upsert=True
                         )
    except Exception as e:
        # Locked account (private)
        auth_match = re.search('Not authorized', str(e))
        timeline_match = re.search('has no tweets in timeline', str(e))
        notExist_match = re.search('Sorry, that page does not exist', str(e))
        overCapacity_match = re.search('Over capacity', str(e))

        if auth_match:
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'error': 'not authorized'},
                              '$push': {'error_key_used': consumer_key}},
                             upsert=True
                             )
        elif overCapacity_match:
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'error': 'over capacity'},
                              '$push': {'error_key_used': consumer_key}},
                             upsert=True
                             )
        elif timeline_match:
            #print("User", user_id, " has no tweets in timeline")
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'error': 'has no tweets in timeline'}},
                             upsert=True
                             )
        elif notExist_match:
            #print("User", user_id, " does not exists anymore")
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'ignore': True, 'ignore_reason': 'does not exists anymore'}},
                             upsert=True
                             )
        else:
            print("Exception. User:", user_id,
                  "API:", consumer_key, "Message:", e)
        return None


def botscore_to_mongodb(user, user_collection):
    """
    Save user' botscore in MongoDB.

    Keyword arguments:
    user -- Twitter user's identificator
    user_collection -- MongoDB Users' Collection
    """

    #print('Getting user botscore...')

    botscore = get_botscore_by_userid(user)
    operations = [botscore]
    user_collection.bulk_write(operations)


def get_user_ids(user_collection):
    """
    Extracts the ObjectID of all users

    Keyword arguments:
    user_collection -- MongoDB Users' Collection
    """

    total_users = list(user_collection.find({}, {'_id': 1}))
    total_users = [u['_id'] for u in total_users]
    return total_users


def get_tweets_by_userid(user_id):
    try:
       # Tweepy request
        auth = tweepy.OAuthHandler(
            TWITTER_DEV_CONSUMER_KEY, TWITTER_DEV_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        message = "Checking:" + str(user_id) + " "

        user = api.get_user(user_id)
        tweets = user.statuses_count

        if tweets > 0:
            account_created_date = user.created_at
            delta = datetime.utcnow() - account_created_date
            account_age_days = delta.days
            #print("Account age (in days): " + str(account_age_days))
            average_tweets = 0
            if account_age_days > 0:
                average_tweets = "%.2f" % (
                    float(tweets)/float(account_age_days))
            #print("Average tweets per day: " + "%.2f"%(float(tweets)/float(account_age_days)))

            hashtags = []
            mentions = []
            tweet_count = 0
            end_date = datetime.utcnow() - timedelta(days=30)

            for status in Cursor(api.user_timeline, id=user.id).items():
                tweet_count += 1
                if hasattr(status, "entities"):
                    entities = status.entities
                    if "hashtags" in entities:
                        for ent in entities["hashtags"]:
                            if ent is not None:
                                if "text" in ent:
                                    hashtag = ent["text"]
                                    if hashtag is not None:
                                        hashtags.append(hashtag)
                    if "user_mentions" in entities:
                        for ent in entities["user_mentions"]:
                            if ent is not None:
                                if "screen_name" in ent:
                                    name = ent["screen_name"]
                                    if name is not None:
                                        mentions.append(name)
                if status.created_at < end_date:
                    break

            return np.array([Counter(mentions).most_common(10), Counter(hashtags).most_common(10), average_tweets])
        else:
            return np.array([None, None, None])

    except tweepy.TweepError as err:
        print(message+"tweepy.TweepError=", err)

    except Exception as e:
        print(message+"Exception. User:", user_id, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)


def get_most_common_user_location(user_id):

    try:
       # Tweepy request
        auth = tweepy.OAuthHandler(
            TWITTER_DEV_CONSUMER_KEY, TWITTER_DEV_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        message = "Checking:" + str(user_id) + " "

        user = api.get_user(user_id)
        tweets_count = user.statuses_count

        if tweets_count > 0:
            # Collect tweets
            tweets = api.user_timeline(id=user_id)

            locations = []

            for tweet in tweets:
                locations.append(tweet.user.location)

            return Counter(locations).most_common(1)[0][0]
        else:
            return np.array([])

    except tweepy.TweepError as err:
        print(message+"tweepy.TweepError=", err)

    except Exception as e:
        print(message+"Exception. User:", user_id, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)


def get_friendships_by_userid(user_id, total_users, user_collection):
    """
    Consults followers and followings of a user and save in MongoDB
    those who are within the total recollected sample of users.

    Keyword arguments:
    user_id -- Twitter user's identificator
    total_users -- List of the total of Twitter users' identificators within our database
    user_collection -- MongoDB Users' Collection
    """
    botometer_instance = random.choice(keys)
    consumer_key = botometer_instance.consumer_key
    consumer_secret = botometer_instance.consumer_secret

    filter_uid = {'_id': make_objid(user_id)}
    message = "Checking:" + str(user_id) + " "
    filter_content = {}

    try:
       # Tweepy request
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        user = api.get_user(user_id)
        protected_user = user.protected

        if not protected_user == True:

            political_friendship_ids = {
                'friends': [],
                'followers': [],
                'friends_bots': [],
                'followers_bots': [],
                'average_tweets_per_day': [],
                'most_used_hashtags': [],
                'most_mentioned_Twitter_users': [],
                'most_common_user_location': []
            }

            tweets = []
            location = []
            tweets = get_tweets_by_userid(user_id)
            location = get_most_common_user_location(user_id)

            for name, method in zip(['friends', 'followers'], [api.friends_ids, api.followers_ids]):
                #print("\tQuerying", name, method)
                for friendships in tweepy.Cursor(method, user_id=user_id).items(200):

                    # We check if the account is private
                    user_friendships = api.get_user(friendships)
                    protected_friendships = user_friendships.protected

                    if not protected_friendships == True:
                        try:
                            botscore = botometer_instance.check_account(
                                friendships)
                            # We are first interested in bot's friends
                            botscore['_id'] = make_objid(friendships)
                            botscore['protected'] = protected_friendships
                            '''
                            tweets_friendships = get_tweets_by_userid(friendships)
                            if tweets_friendships.any():
                                botscore['most_used_hashtags'] = [
                                    tweet for tweet in tweets_friendships[1]]
                                botscore['most_mentioned_Twitter_users'] = [
                                    tweet for tweet in tweets_friendships[0]]
                                botscore['average_tweets_per_day'] = tweets_friendships[2]
                                botscore['most_common_user_location'] = get_most_common_user_location(
                                    friendships)
                            '''
                            if (botscore['cap']['universal'] >= MINIMUM_BOTSCORE):
                                political_friendship_ids[name +
                                                         '_bots'].append(botscore)
                            else:
                                political_friendship_ids[name].append(botscore)

                        except tweepy.TweepError as err:
                            political_friendship_ids[name].append(
                                {'error': str(err)})
                            continue

                        except Exception as e:
                            political_friendship_ids[name].append(
                                {'error': str(e)})
                            continue

            message += "\tFriends:" + \
                str(len(political_friendship_ids['friends']))
            message += "\tFollowers:" + \
                str(len(political_friendship_ids['followers']))
            message += "\tFriends_bots:" + \
                str(len(political_friendship_ids['friends_bots']))
            message += "\tFollowers_bots:" + \
                str(len(political_friendship_ids['followers_bots']))


            filter_content = {
                '$set': {
                    'username': user.screen_name,
                    'id': user.id,
                    'description': user.description,
                    'url': user.url,
                    'created_at': user.created_at,
                    'error': 'None',
                    'protected': protected_user,
                    'friends': user.friends_count,
                    'followers' : user.followers_count,
                    'average_tweets_per_day': tweets[2],
                    'most_common_user_location': location
                },
                '$push': {
                    'friends_analyzed': {
                        '$each': political_friendship_ids['friends']
                    },
                    'followers_analyzed': {
                        '$each': political_friendship_ids['followers']
                    },
                    'friends_bots_analyzed': {
                        '$each': political_friendship_ids['friends_bots']
                    },
                    'followers_bots_analyzed': {
                        '$each': political_friendship_ids['followers_bots']
                    },
                    'most_used_hashtags': {
                        '$each': tweets[1]
                    },
                    'most_mentioned_Twitter_users': {
                        '$each': tweets[0]
                    }
                }
            }
        else:
            filter_content = {
                '$set': {
                    'username': user.screen_name,
                    'id': user.id,
                    'protected': protected_user,
                }
            }

        user_collection.update_one(filter_uid, filter_content, upsert=True)
        return True

    except tweepy.TweepError as err:
        filter_content = {
            '$set': {
                'Error': str(err)
            }
        }

    except Exception as e:
        filter_content = {
            '$set': {
                'Error': str(e)
            }
        }
    return False


# update the database with botscore
user = get_user(sys.argv[1])
botscore_to_mongodb(user.id, db.users)
total_users = get_user_ids(db.users)
# upodate the database with friendships
get_friendships_by_userid(user.id, total_users, db.users)
