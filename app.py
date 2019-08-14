from flask import Flask, request,Markup, render_template,make_response
from flask_restful import Resource,Api
import databaseOps as db
import pymongo
from subprocess import Popen
import subprocess
from pymongo import MongoClient,errors
import json

app=Flask(__name__)
api= Api(app)

# running the engine script to fetch data from Twitter at 12am everyday
Popen(["python","engine.py","get_token","60"], stdout=subprocess.PIPE)

#creating a database connection object from databaseOps class
dbops = db.databaseOps()


labels = ['Positive','Negative','Neutral']


class Dashboard(Resource): 
	def get(self):
		
		#gettting the trending tweets from mongo-atlas for a country
		#trend is json with country, trend and tweet volume
		#obtaining the top 10 trending topics in canada

		trends = dbops.get_trends_by_country("canada", order= -1,  count = 10)
		# print(trends)
		# print("-------------------------------------")

		# generating the value list for all the 10 piecharts by calculating the average sentiment
		value_list = []
		for eachtrend in trends:
			
			sentiment_dict = {}
			tweets = dbops.get_tweets_by_trend(eachtrend["trend"])
			#picking positive tweets from tweets 
			ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 

			ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
			#percentage of positive tweets 
			sentiment_dict['positive'] = round(100*len(ptweets)/len(tweets),2)
			sentiment_dict['negative'] = round(100*len(ntweets)/len(tweets),2)
			sentiment_dict['neutral'] = round(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets),2)


			value_list.append(sentiment_dict)
			print(sentiment_dict)

		print(value_list)
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template('charts.html', title='Sentiment Analyzer', max=17000,trends=trends,label=labels,values=value_list))
   
class getlocations(Resource):
	def get(self):
		return dbops.get_lookup_locations()

class get_all_trends(Resource):
	def get(self):
		return dbops.get_all_trends()

class get_trends(Resource):
	def get(self,country):
		return dbops.get_trends_by_country(country)


api.add_resource(Dashboard, "/")
api.add_resource(getlocations,'/locations')
api.add_resource(get_all_trends,'/alltrends')
api.add_resource(get_trends,'/countrytrends/<string:country>')

if __name__ == '__main__':
	app.run(debug=True)