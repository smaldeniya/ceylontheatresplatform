import datetime
import urllib
import webapp2
import cgi
import logging

from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

from handlers import *
from datamodels import *

from datetime import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	

def testing_key(testing_name=None):
	return db.Key.from_path('Testing', testing_name or 'default_testing')

class AddHallHandler(BaseHandler):
	@user_required
	def get(self):
		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return
			
		self.render_template('addhall.html')
		
	@user_required
	def post(self):
		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return
			
		cinema = CinemaHall(parent=testing_key('default'))
		cinema.code_no = self.request.get('code_no')
		cinema.name = self.request.get('name')
		cinema.place = self.request.get('place')
		cinema.seatplan = self.request.get('seatplan_url').strip()
		cinema.grade = self.request.get('grade')
		cinema.distributor = self.request.get('distributor')
		cinema.nfc = float(self.request.get('nfc'))
		cinema.theatre = float(self.request.get('theatre'))
		cinema.percent = float(self.request.get('percent'))
		
		t = {}
		for i in range(1, 5):
			t[i] = self.request.get('show'+str(i))
			self.response.out.write(datetime.strptime(t[i], "%H:%M").time())
		cinema.show_time1 = datetime.strptime(self.request.get('show1'), "%H:%M").time()
		cinema.show_time2 = datetime.strptime(self.request.get('show2'), "%H:%M").time()
		cinema.show_time3 = datetime.strptime(self.request.get('show3'), "%H:%M").time()
		cinema.show_time4 = datetime.strptime(self.request.get('show4'), "%H:%M").time()
		cinema.put()
		
		#####################
		catagories = ['balcony', 'odc', 'firstclass']
		ticket_types = ['full', 'half', 'service', 'complimentary']
		types = ['basic', 'ent']
		for catagory in catagories:
			seat = Seat(parent=cinema)
			seat.cinema_id = cinema.key().id()
			seat.catagory = catagory
			seat.number = int(self.request.get(catagory+'_total'))
			seat.put()
			for type in ticket_types:
				for type1 in types:
					tariff = Tariff(parent=cinema)
					tariff.cinema_id = cinema.key().id()
					tariff.ticket_type = catagory+'_'+type
					tariff.type = type1
					self.response.out.write(catagory+" "+ type+" " + type1 + " " + self.request.get(catagory+'_'+type+'_'+type1) + '<br>')
					tariff.rate = float(self.request.get(catagory+'_'+type+'_'+type1))
					logging.debug(catagory+" "+ type+" ticket " + self.request.get(catagory+'_'+type+'_ticket') + '<br><br>')
					tariff.opening = int(self.request.get(catagory+'_'+type+'_ticket'))
					tariff.put()
					t = float("20.00")

		catagory = 'box'
		seat = Seat(parent=testing_key('default'))
		seat.cinema_id = cinema.key().id()
		seat.catagory = catagory
		seat.number = int(self.request.get(catagory+'_total'))
		seat.put()
		type = 'full'
		for type1 in types:
			tariff = Tariff(parent=cinema)
			tariff.cinema_id = cinema.key().id()
			tariff.ticket_type = catagory+'_'+type
			tariff.type = type1
			self.response.out.write(catagory+" "+ type+" " + type1 + " " + self.request.get(catagory+'_'+type+'_'+type1) + '<br>')
			tariff.rate = float(self.request.get(catagory+'_'+type+'_'+type1))
			tariff.opening = int(self.request.get(catagory+'_'+type+'_ticket'))
			tariff.put()
			t = float("0")

		self.redirect('/')