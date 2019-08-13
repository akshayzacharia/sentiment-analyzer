from flask import Flask, request,Markup, render_template,make_response
from flask_restful import Resource,Api
import databaseOps as db
import pymongo
from pymongo import MongoClient,errors
import json

app=Flask(__name__)
api= Api(app)
dbops = db.databaseOps()

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


class Dashboard(Resource): 
	def get(self):
		pie_labels = labels
		pie_values = values
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template('dashboard.html', title='test', max=17000, set=zip(values, labels, colors)))
		
 
class barc(Resource):
	def get(self):
		bar_labels=labels
		bar_values=values
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template('bar_chart.html', title='test', max=17000, labels=bar_labels, values=bar_values))

class Multi(Resource):
	def get(self,num):
		return {'result':num*100}
   
class getlocations(Resource):
	def get(self):
		return dbops.get_lookup_locations()

class get_all_trends(Resource):
	def get(self):
		return dbops.get_all_trends()

class get_trends(Resource):
	def get(self,country):
		return dbops.get_trends(country)


api.add_resource(Dashboard, "/")
api.add_resource(barc, "/bar")
api.add_resource(Multi,'/multi/<int:num>')
api.add_resource(getlocations,'/locations')
api.add_resource(get_all_trends,'/alltrends')

if __name__ == '__main__':
	app.run(debug=True)