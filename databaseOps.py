import pymongo
from pymongo import MongoClient,errors
import json

class databaseOps(object):

	def __init__(self):
		try: 
			#self.client = MongoClient("mongodb://localhost:27017/")
			self.client = MongoClient("mongodb+srv://datapgmuser:datapgmpsswd@mflix-1ez8y.mongodb.net/test?retryWrites=true&w=majority")
			self.db = self.client.tweet_db
			print("Authentication to database succeeded")

		except pymongo.errors.ConnectionFailure as e:
			print("Authentication to database failed")
			print(e)
			

	def get_lookup_locations(self):

		countrylist = [x for x in self.db.lookup_location.find({}, {"_id":0})]

		#returning json object of countries
		return json.loads(json.dumps(countrylist))
		

	def get_all_trends(self):

		trend_documents = [x for x in self.db.trend_collection.find({}, {"_id":0})]
		return trend_documents


	def get_trends_by_country(self, country, order = 1, count = 50):

		trend_documents = [x for x in self.db.trend_collection.find({"country" : country}, {"country":0,"_id":0}).limit( count ).sort([ ("tweet_vol", order) ] )]
		return trend_documents	


	def get_tweets_by_trend(self,trend, limit = 10000):
		#function to get tweets for a specific trend
		tweet_documents = [x for x in self.db.tweet_collection.find({"trend" : trend},{"_id":0}).limit( limit )]
		return tweet_documents

	

		