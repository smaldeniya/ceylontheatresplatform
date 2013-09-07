import datetime
import logging
import urllib
import webapp2
import cgi

from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

from handlers import *
from datamodels import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
	

def testing_key(testing_name=None):
	return db.Key.from_path('Testing', testing_name or 'default_testing')

class AddCopyHandler(BaseHandler):
	
	@user_required
	def get(self):

		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return
			
		films_query = Film.all()
		films = films_query.fetch(10000)
		
		template_values = {
			'films': films,
        }
		
		self.render_template('addcopies.html', template_values)
		
	@user_required
	def post(self):
	
		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return
			
		film_id = int(self.request.get('film_id'))
		for i in range(1, 6):
			logging.debug(self.request.get('film_record_'+str(i)))
			if(self.request.get('film_record_'+str(i))):
				reel = Reel(parent=testing_key('default'))
				reel.film_id = film_id
				reel.reel_no = self.request.get('film_record_'+str(i))
				reel.put()
		
		self.redirect('/')
		

class AddFilmHandler(BaseHandler):
	@user_required
	def get(self):
	
		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return
			
		self.render_template('addfilm.html')
	
	@user_required
	def post(self):
	
		#check for admin
		current_user = self.auth.get_user_by_session()
		admin = current_user['admin']
		
		if not(admin):
			self.redirect('/')
			return

		film = Film(parent=testing_key('default'))
		
		film.name = self.request.get('name')
		
		film.put()
		
		self.redirect('/addcopies')