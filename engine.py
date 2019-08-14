import re 
import tweepy 
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream 
import pymongo
from pymongo import MongoClient
import json
from textblob import TextBlob
import schedule
import time


class TwitterClient(object): 
	''' 
	Generic Twitter Class for sentiment analysis. 
	'''

	def __init__(self):
		''' 
		Class constructor or initialization method. 
		'''
		# keys and tokens from the Twitter Dev Console 
		consumer_key = 'Jt8JMLQEXAkkuLzP92tpQZ7ES'
		consumer_secret = 'Cie1JWEBom1nnj71EeE1KB6LlehwOKo654A84cjVERpks2OLaW'
		access_token = '1159168806759075841-WhppPbJbtbKKrcE0PfxSl1ttg6lEcB'
		access_token_secret = 'KmTykl1LFvsmXWtNlwpALFNYiDzLuL4Mzp0hGk0d4AqP5'
		
		# attempt authentication 
		try: 
			# create OAuthHandler object 
			self.auth = OAuthHandler(consumer_key, consumer_secret)
			# set access token and secret
			self.auth.set_access_token(access_token, access_token_secret) 
			# create tweepy API object to fetch tweets 
			self.api = tweepy.API(self.auth, wait_on_rate_limit= True, wait_on_rate_limit_notify = True)
		except: 
			print("Error: Authentication Failed") 

	def clean_tweet(self, tweet): 
		''' 
		Utility function to clean tweet text by removing links, special characters 
		using simple regex statements. 
		'''
		return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)', " ", tweet).split()) 

	def get_tweet_sentiment(self, tweet): 
		''' 
		Utility function to classify sentiment of passed tweet 
		using textblob's sentiment method 
		'''
		# create TextBlob object of passed tweet text 
		analysis = TextBlob(self.clean_tweet(tweet)) 
		# set sentiment 
		if analysis.sentiment.polarity > 0: 
			return 'positive'
		elif analysis.sentiment.polarity == 0: 
			return 'neutral'
		else: 
			return 'negative'

	def get_tweets(self, query, count = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets 
		tweets = []

		try: 
			# call twitter api to fetch tweets 
			fetched_tweets = self.api.search(q = query, count = count,lang = 'en') 
			
			# parsing tweets one by one 
			for tweet in fetched_tweets:
				# empty dictionary to store required params of a tweet 
				parsed_tweet = {}

				# saving text of tweet 
				parsed_tweet['text'] = tweet.text
				# saving sentiment of tweet 
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

				# appending parsed tweet to tweets list 
				if tweet.retweet_count > 0: 
					# if tweet has retweets, ensure that it is appended only once 
					if parsed_tweet not in tweets: 
						tweets.append(parsed_tweet) 
				else: 
					tweets.append(parsed_tweet) 

			# return parsed tweets 
			return tweets 

		except tweepy.TweepError as e: 
			#print error (if any) 
			print("Error : " + str(e)) 

	def get_trending_topics_by_loc(self, location_list):
		
		tweets = []
		for location in location_list:
			woeid = location.get("woeid")
			country = location.get("locations")
			
			try:
				woeid_trends = self.api.trends_place(woeid)
				trends = json.loads(json.dumps(woeid_trends, indent=1))

				for trend in trends[0]["trends"]:
					#tweets.append((trend["name"]).strip("#"))
					trend_dic = {}
					trend_dic['country'] = country
					trend_dic['trend'] = (trend["name"]).strip("#")
					trend_dic['tweet_vol'] = trend["tweet_volume"]
					
					if trend_dic not in tweets:
						tweets.append(trend_dic)

				# removing duplicate values by set function for performance 
				#tweets = list(set(tweets))				

			except tweepy.TweepError as e: 
				# print error (if any) 
				print("Error : " + str(e))	
		
		return tweets


def main(): 
	# creating object of TwitterClient Class 
	print("Engine :> Executing the main job")
	api = TwitterClient()
	try: 
		client = MongoClient("mongodb+srv://datapgmuser:datapgmpsswd@mflix-1ez8y.mongodb.net/test?retryWrites=true&w=majority")
		db = client.tweet_db
		db.trend_collection.drop()
		db.tweet_collection.drop()
		countrylist = [x for x in db.lookup_location.find({}, {"_id":0})]

	except Error as e:
		print(e)

	#calling to get a list of trending topics in twitter by sending locations list to target topic extraction
	trends = api.get_trending_topics_by_loc(countrylist)
	#inserting the collected trends per country to mongo
	trend_collection = db.trend_collection
	tweet_collection = db.tweet_collection

	#print(trends)
	trend_collection.insert_many(trends)


	for eachtrend in trends:

		# calling function to get tweets 
		print(eachtrend['trend'] + " and " + eachtrend['country'])

		#tweets  is also a list of dictionaries containing each tweet and its sentiment
		
		tweets = api.get_tweets(query = eachtrend['trend'], count = 200)
		
		for item in tweets:
			item.update( {"country":eachtrend['country']})
			item.update( {"trend":eachtrend['trend']})
		#print(tweets)
		try:
			tweet_collection.insert_many(tweets)

		except:
			print("Not able to insert tweet, for non english")
			trend_collection.remove({"trend":eachtrend['trend']})
			continue


if __name__ == "__main__": 
	# main()
	schedule.every().day.at("00:00").do(main)
	print("Engine :> job scheduled!")
	# calling main() function
	while True:
		schedule.run_pending()
		print("Engine :> sleeping now!, will wake up at 12am")
		time.sleep(60) # wait 
	