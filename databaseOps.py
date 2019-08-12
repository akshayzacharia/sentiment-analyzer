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

		trendcollection = [x for x in self.db.trend_collection.find({}, {"_id":0})]
		return trendcollection


	def get_trends(self,country):

		trendcollection = [x for x in self.db.trend_collection.find({}, {"_id":0})]
		return trendcollection	
		
