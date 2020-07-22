#!/usr/bin/python

# Utilities
import sys
import re
import random
import json

# Botometer API
import botometer

# MongoDB functionality
from pymongo.errors import BulkWriteError
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne, UpdateMany, DeleteMany
from pymongo.bulk import BulkOperationBuilder
from bson import ObjectId

# Tweet API for friendships
import tweepy

# Keys
RAPID_API_KEY1 = ''
RAPID_API_KEY2 = ''
TWITTER_DEV_CONSUMER_KEY = ''
TWITTER_DEV_CONSUMER_SECRET = ''
TWITTER_DEV_ACCESS_TOKEN = ''
TWITTER_DEV_ACCESS_TOKEN_SECRET = ''


# Botometer and Twitter Keys for parallel processing
keys = {
     0: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=RAPID_API_KEY1, **{'consumer_key': TWITTER_DEV_CONSUMER_KEY, 'consumer_secret': TWITTER_DEV_CONSUMER_SECRET}),
     1: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key=RAPID_API_KEY2, **{'consumer_key': TWITTER_DEV_CONSUMER_KEY, 'consumer_secret': TWITTER_DEV_CONSUMER_SECRET}),
}

# MongoDB parameters
mongoclient = MongoClient('127.0.0.1', 27017)
db = mongoclient.SFM

MINIMUM_BOTSCORE = 0.43
MAX_DEPTH = 1
DEPTH = 0

def get_user(user):

    message = "Checking:" + str(user) + " "
    try:
        # Tweepy request
        auth = tweepy.OAuthHandler(TWITTER_DEV_CONSUMER_KEY, TWITTER_DEV_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN, TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
    
        # Obtain by username
        return api.get_user(user)

    except Exception as e:
        print(message+"Exception. User:", user, "API:", TWITTER_DEV_CONSUMER_KEY, "Message:", e)
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
        return ObjectId(text.rjust(24,"0"))
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
                             {'$unset': {'scores':""},
                              '$set': {'ignore': False, 'ignore_reason': 'not authorized'},
                              '$push': {'ignore_key_used': consumer_key}},
                             upsert=True
                            )
        elif overCapacity_match:
            return UpdateOne({'_id': make_objid(user_id)}, 
                             {'$unset': {'scores':""},
                              '$set': {'ignore': False, 'ignore_reason': 'over capacity'},
                              '$push': {'ignore_key_used': consumer_key}},
                             upsert=True
                            )
        elif timeline_match:
            #print("User", user_id, " has no tweets in timeline")
            return UpdateOne({'_id': make_objid(user_id)}, 
                             {'$unset': {'scores':""},
                              '$set': {'ignore': True, 'ignore_reason': 'has no tweets in timeline'}},
                              upsert=True
                            )
        elif notExist_match:
            #print("User", user_id, " does not exists anymore")
            return UpdateOne({'_id': make_objid(user_id)}, 
                             {'$unset': {'scores':""},
                              '$set': {'ignore': True, 'ignore_reason': 'does not exists anymore'}},
                              upsert=True
                            )
        else:
            print("Exception. User:", user_id, "API:", consumer_key, "Message:", e)
        return None
    botometer_instance = random.choice(keys)
    
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
    #print("M:", str(results.matched_count).rjust(8, " "),
    #          " I:", str(results.inserted_count).rjust(8, " "),
    #          " U:", str(results.upserted_count).rjust(8, " "))

def get_user_ids(user_collection):
    """
    Extracts the ObjectID of all users
    
    Keyword arguments:
    user_collection -- MongoDB Users' Collection
    """
    
    total_users = list(user_collection.find({},{'_id': 1}))
    total_users = [u['_id'] for u in total_users]
    #print("Number of total users:",len(total_users))
    return total_users

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
        auth.set_access_token(TWITTER_DEV_ACCESS_TOKEN, TWITTER_DEV_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        political_friendship_ids = {
            'friends' : [],
            'followers': []
        }

        political_bots_friendship_ids = {
            'friends_bots' : [],
            'followers_bots': []
        }
        
        for name,method in zip(['friends','followers'],[api.friends_ids,api.followers_ids]):
            #print("\tQuerying", name, method)
            for friendships in tweepy.Cursor(method, user_id = user_id).items(200):
                botscore = botometer_instance.check_account(friendships)
                # We are only interested in bot's friends
                if (botscore['cap']['universal'] >= MINIMUM_BOTSCORE):
                    botscore['_id'] = make_objid(friendships)
                    political_bots_friendship_ids[name + '_bots'].append(botscore)
                else:
                    political_friendship_ids[name].append(botscore)

                

        message += "\tFriends:" + str(len(political_friendship_ids['friends']))
        message += "\tFollowers:" + str(len(political_friendship_ids['followers']))
        message += "\tFriends_bots:" + str(len(political_bots_friendship_ids['friends_bots']))
        message += "\tFollowers_bots:" + str(len(political_bots_friendship_ids['followers_bots']))
        filter_content = {
            '$push': {
                'friends' : {
                    '$each' : political_friendship_ids['friends']
                },
                'followers' : {
                    '$each' : political_friendship_ids['followers']
                },
                'friends_bots' : {
                    '$each' : political_bots_friendship_ids['friends_bots']
                },
                'followers_bots' : {
                    '$each' : political_bots_friendship_ids['followers_bots']
                }
            }
        }


    except tweepy.TweepError as err:
        print(message+"tweepy.TweepError=", err)
        filter_content = {
            '$set': {
                'ignore': True, 'ignore_reason': str(err)
            },
            '$push': {
                'ignore_key_used': consumer_key}
        }
    except Exception as e:
        print(message+"Exception. User:", user_id, "API:", consumer_key, "Message:", e)
        return False

    #print(filter_uid,filter_content)
    res = user_collection.update_one(filter_uid, filter_content, upsert=True)
    #print(message + "\tMa:", res.matched_count, "\tMo:", res.modified_count, "\tUp:", res.upserted_id, ";\tDONE!")
    return True

     
# update the database with botscore
user = get_user(sys.argv[1])
botscore_to_mongodb(user.id, db.users)
total_users = get_user_ids(db.users)
# upodate the database with friendships
get_friendships_by_userid(user.id, total_users, db.users)





