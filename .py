#!/usr/bin/python

# Utilities
import sys
from fastprogress.fastprogress import master_bar, progress_bar
import random
import re
from multiprocessing import Pool


# Botometer API
import botometer

# MongoDB functionality
from pymongo.errors import BulkWriteError
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne, UpdateMany, DeleteMany
from pymongo.bulk import BulkOperationBuilder
from bson import ObjectId

# Tweet API for friendships
import tweepy


# Botometer and Twitter Keys for parallel processing
keys = {
     0: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key='996b6059b5msh054ffbac53e17a0p15482ajsna37d1925b5a2', **{'consumer_key':'JAtCAECeGWpyeoTscmBpWQBsZ', 'consumer_secret':'m3K33k9Zq6jNUHSi3hgjn7pJ9RFXgCUgf4bgegaZMXmjRPAOL2'}),
     1: botometer.Botometer(wait_on_ratelimit=True, rapidapi_key='996b6059b5msh054ffbac53e17a0p15482ajsna37d1925b5a2', **{'consumer_key':'JAtCAECeGWpyeoTscmBpWQBsZ', 'consumer_secret':'m3K33k9Zq6jNUHSi3hgjn7pJ9RFXgCUgf4bgegaZMXmjRPAOL2'}),
}

# MongoDB parameters
mongoclient = MongoClient('127.0.0.1', 27017)
db = mongoclient.SFM
# It will automatically create the tweets' and users' collections.


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
        return UpdateOne({'_id': user_id}, 
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

    
def botscores_to_mongodb(users, user_collection, processes=18):
    """
    Saves a list of users' botscores in MongoDB.
    The process can be paralelized with available keys for more speed and handle API Twitter limits
    Note: This method should be improved by implementing non-blocking calls

    Keyword arguments:
    users -- list of Twitter users' identificator
    processes -- number of processes to employ (must be less or equal to the number of available keys)
    """
    
    pool = Pool(processes=processes)
    processes = []

    for uid in progress_bar(users):       
        processes.append(pool.apply_async(
            get_botscore_by_userid, 
            (uid,)
        ))

    pool.close()


    #pool.join()
    print('Getting user botscores...')
    operations = []
    for p in progress_bar(processes):
        #p.wait()
        response = p.get()
        if response is not None:
            operations.append(response)
        
        
        if len(operations) > 1000:
            results = user_collection.bulk_write(operations)
            print("M:", str(results.matched_count).rjust(8, " "),
                  " I:", str(results.inserted_count).rjust(8, " "),
                  " U:", str(results.upserted_count).rjust(8, " "))
            operations = []

    if len(operations) > 0: 
        results = user_collection.bulk_write(operations)
        print("M:", str(results.matched_count).rjust(8, " "),
              " I:", str(results.inserted_count).rjust(8, " "),
              " U:", str(results.upserted_count).rjust(8, " "))


# update the database with botscores
botscores_to_mongodb(sys.argv[1], db.users, 12)


