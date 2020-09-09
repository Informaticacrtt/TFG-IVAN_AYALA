#!/usr/bin/python

# Utilities
import sys
import re
import random
import json
import numpy as np
from datetime import datetime


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
RAPID_API_KEY1 = '482ca7d7ddmsh7ed2276672ec59ap1df487jsn7045898e1d24'
RAPID_API_KEY2 = '675d0ce501msh7d4625ce153e682p195e60jsn5d44cc4b5345'
TWITTER_DEV_CONSUMER_KEY = 'ZXp6YUob5JMZYYixAeu65Pw8q'
TWITTER_DEV_CONSUMER_SECRET = 'nJfbKtgNYBwruMOPO5QZd5z5fSNkmW6DhWb6iCMdExLVw1wcFi'
TWITTER_DEV_ACCESS_TOKEN = '1204405321256570886-OC7sCmXWK0QavVLk6yCuYosGAkm6un'
TWITTER_DEV_ACCESS_TOKEN_SECRET = 'aSUbFNTDTqUkN1pAhKGlb8zpY1QButgSbTCTHHZBKRfRe'


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
    """Get user object

    Keyword arguments:
    user -- string to be search
    """

    message = "Checking:" + str(user) + " "

    botometer_instance = random.choice(keys)
    consumer_key = botometer_instance.consumer_key
    consumer_secret = botometer_instance.consumer_secret

    try:
        # Tweepy request
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Obtain by username or id
        return np.array([True, api.get_user(user)])

    except Exception as e:
        message = "Exception. User: " + user + " API: " + \
            TWITTER_DEV_CONSUMER_KEY + " Message:" + str(e)
        return np.array([False, message])

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

def get_botscore_by_userid(user):
    """
    Collects the botscore from Botometer

    Keyword arguments:
    user -- Twitter users' identificator
    """

    user_id = user.id
    try:
        botometer_instance = random.choice(keys)
        consumer_key = botometer_instance.consumer_key
        result = botometer_instance.check_account(user_id)
        return UpdateOne({'_id': make_objid(user_id)},
                         {'$set': {
                             'scores': result,
                             'screen_name': user.screen_name,
                             'id': user.id,
                             'error': 'None',
                             'checked': datetime.now().strftime("%d/%m/%Y")
                         }},
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
                              '$set': {'screen_name': user.screen_name,
                                       'id': user.id,
                                       'error': 'not authorized',
                                       'checked': datetime.now().strftime("%d/%m/%Y")},
                              '$push': {'error_key_used': consumer_key}},
                             upsert=True
                             )
        elif overCapacity_match:
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'screen_name': user.screen_name,
                                       'id': user.id,
                                       'error': 'over capacity',
                                       'checked': datetime.now().strftime("%d/%m/%Y")},
                              '$push': {'error_key_used': consumer_key}},
                             upsert=True
                             )
        elif timeline_match:
            # print("User", user_id, " has no tweets in timeline")
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'screen_name': user.screen_name,
                                       'id': user.id,
                                       'error': 'has no tweets in timeline',
                                       'checked': datetime.now().strftime("%d/%m/%Y")}},
                             upsert=True
                             )
        elif notExist_match:
            # print("User", user_id, " does not exists anymore")
            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {'error': 'does not exists anymore',
                              'checked': datetime.now().strftime("%d/%m/%Y")}},
                             upsert=True
                             )
        else:
            print("Exception. User:", user_id,
                  "API:", consumer_key, "Message:", e)

            return UpdateOne({'_id': make_objid(user_id)},
                             {'$unset': {'scores': ""},
                              '$set': {
                                 'screen_name': user.screen_name,
                                 'id': user.id,
                                 'error': str(e),
                                 'checked': datetime.now().strftime("%d/%m/%Y")}
                              },
                             upsert=True
                             )

def botscore_to_mongodb(user, user_collection):
    """
    Save user' botscore in MongoDB.

    Keyword arguments:
    user -- Twitter user's identificator
    user_collection -- MongoDB Users' Collection
    """

    # print('Getting user botscore...')

    botscore = get_botscore_by_userid(user)
    user_collection.bulk_write([botscore])

def profile_info_to_mongodb(user, user_collection):
    """
    Save user' profile in MongoDB.

    Keyword arguments:
    user -- Twitter user's identificator
    user_collection -- MongoDB Users' Collection
    """

    filter_uid = {'_id': make_objid(user.id)}
    botometer_instance = random.choice(keys)
    consumer_key = botometer_instance.consumer_key
    consumer_secret = botometer_instance.consumer_secret

    try:
        # Tweepy request
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        filter_content = {
            '$set': {
                'name': user.name,
                'screen_name': user.screen_name,
                'id': user.id,
                'description': user.description,
                'verified': user.verified,
                'url': user.url,
                'location': user.location,
                'created_at': user.created_at,
                'profile_image_url_https': user.profile_image_url_https,
                'profile_banner_url': user.profile_banner_url,
                'listed_count': user.listed_count,
                'favourites_count': user.favourites_count,
                'protected': user.protected,
                'friends': user.friends_count,
                'most_recent_post': str(api.user_timeline(user.id, count=1)[0].created_at),
                'followers': user.followers_count,
                'followers_ratio': round((float(user.followers_count)/float(user.friends_count)), 2),
                'average_tweets_per_day': get_average_tweets_per_day(user),
                'most_common_user_location': get_most_common_user_location(api, user),
                'statuses_count': user.statuses_count,
                'lang': user.lang
                # 'retweet_count': tweets[3], #fix
                # 'retweets_of_me' : len(tweets[4]) #fix
            }
        }
        user_collection.update_one(filter_uid, filter_content, upsert=True)

    except Exception as e:
        print("Error profile_info_to_mongodb")

def get_average_tweets_per_day(user):
    """
    Get average tweets per day.

    Keyword arguments:
    user -- User object
    """

    tweets = user.statuses_count
    account_created_date = user.created_at
    delta = datetime.utcnow() - account_created_date
    account_age_days = delta.days
    average_tweets = 0

    if account_age_days > 0:
        average_tweets = round((float(tweets)/float(account_age_days)), 2)

    return average_tweets

def get_most_common_user_location(api, user):
    """
    Get most common user location.

    Keyword arguments:
    api -- Tweepy api
    user -- User object
    
    """

    try:
        message = "Checking:" + str(user.id) + " "
        tweets_count = user.statuses_count

        if tweets_count > 0:
            # Collect tweets
            tweets = api.user_timeline(id=user.id)

            locations = []

            for tweet in tweets:
                locations.append(tweet.user.location)

            return Counter(locations).most_common(1)[0][0]
        else:
            return np.array([])

    except tweepy.TweepError as err:
        print(message+"get_most_common_user_location - tweepy.TweepError=", err)

    except Exception as e:
        print(message+" get_most_common_user_location - Exception. User:", user.id, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)

def most_used_hashtags_and_mentioned_Twitter_users_to_mongodb(user, user_collection):
    """
    Save most used hashtags and mentioned Twitter users in MongoDB.

    Keyword arguments:
    user -- User object
    user_collection -- MongoDB Users' Collection
    """
    filter_uid = {'_id': make_objid(user.id)}
    botometer_instance = random.choice(keys)
    consumer_key = botometer_instance.consumer_key
    consumer_secret = botometer_instance.consumer_secret
    try:
       # Tweepy request
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        message = "Checking:" + str(user.id) + " "

        tweets = user.statuses_count

        if tweets > 0:
            hashtags = []
            mentions = []
            end_date = datetime.utcnow() - timedelta(days=30)

            for status in Cursor(api.user_timeline, id=user.id, include_rts=True).items(200):

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

            filter_content = {
                '$push': {
                    'most_used_hashtags': {
                        '$each': Counter(mentions).most_common(10)
                    },
                    'most_mentioned_Twitter_users': {
                        '$each': Counter(hashtags).most_common(10)
                    },
                }
            }
            user_collection.update_one(filter_uid, filter_content, upsert=True)

    except tweepy.TweepError as err:
        print(message+"tweepy.TweepError=", err)

    except Exception as e:
        print(message+"Exception. User:", user.id, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)

def average_of_tweets_by_day_of_week_to_mongodb(user_id, user_collection):
    """
    Save average of tweets by day of week of user in MongoDB.

    Keyword arguments:
    user_id -- Twitter user's identificator
    user_collection -- MongoDB Users' Collection
    """
    filter_uid = {'_id': make_objid(user_id)}
    botometer_instance = random.choice(keys)
    consumer_key = botometer_instance.consumer_key
    consumer_secret = botometer_instance.consumer_secret
    message = "Checking:" + str(user_id) + " "

    try:
        # Tweepy request
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN,
                              TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        recents_tweets = api.user_timeline(id=user_id, count=200)
        tweets = [0, 0, 0, 0, 0, 0, 0, 0]
        analyzed = 0
        for tweet in recents_tweets:
            date = (tweet.created_at).weekday()
            tweets[date-1] += 1
            analyzed += 1

        tweets[7] = analyzed

        filter_content = {
            '$push': {
                'average_of_tweets_by_day_of_week': {
                        '$each': tweets
                }
            }
        }
        user_collection.update_one(filter_uid, filter_content, upsert=True)

    except tweepy.TweepError as err:
        print(message+"tweepy.TweepError=", err)

    except Exception as e:
        print(message+"Exception. User:", user_id, "API:",
              TWITTER_DEV_CONSUMER_KEY, "Message:", e)

def friendships_by_userid_to_mongodb(user_id, user_collection):
    """
    Get information about followers and followings of a user and save in MongoDB.

    Keyword arguments:
    user_id -- Twitter user's identificator
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
                'followers_bots': []
            }

            for name, method in zip(['friends', 'followers'], [api.friends_ids, api.followers_ids]):
                # print("\tQuerying", name, method)
                for friendships in tweepy.Cursor(method, user_id=user_id).items(70):

                    # We check if the account is private
                    user_friendships = api.get_user(friendships)
                    protected_friendships = user_friendships.protected

                    if not protected_friendships == True:

                        botometer_instance_friendships = random.choice(keys)

                        try:

                            botscore = botometer_instance_friendships.check_account(
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
                    }
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



def main():

    # We try to get user
    result = get_user(sys.argv[1])
    user_collection = db.users
    # If user is founded
    if (result[0] != 'False'):
        # update the database with botscore
        botscore_to_mongodb(result[1], user_collection)
        found = user_collection.find_one(
            {'_id': make_objid(result[1].id), 'error': 'None'})
        # If db added botscore correctly to user
        if (found is not None):
            profile_info_to_mongodb(result[1], user_collection)
            most_used_hashtags_and_mentioned_Twitter_users_to_mongodb(
                result[1], user_collection)
            average_of_tweets_by_day_of_week_to_mongodb(result[1].id,user_collection)
            # update the database with friendships
            friendships_by_userid_to_mongodb(result[1].id, user_collection)
    else:
        print("get_user fail")
        return result[1]


# Run the script
main()
