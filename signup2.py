from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.api import mail

import logging
import os.path
import os
import webapp2
import sys
import jinja2

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from datamodels import *
from handlers import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def testing_key(testing_name=None):
	return db.Key.from_path('Testing', testing_name or 'default_testing')

def user_required(handler):
  """
    Decorator that checks if there's a user associated with the current session.
    Will also fail if there's no session present.
  """
  def check_login(self, *args, **kwargs):
    auth = self.auth
    if not auth.get_user_by_session():
      self.redirect(self.uri_for('login'), abort=True)
    else:
      return handler(self, *args, **kwargs)

  return check_login

class SignupHandlerTwo(BaseHandler):
  def get(self):
    cinemas_query = CinemaHall.all()
    cinemas = cinemas_query.fetch(10000)
	
    template_values = {'cinemas': cinemas}
    self.render_template('signup.html', template_values)

  def post(self):
	
	user_name = self.request.get('username')
	first_name = self.request.get('firstname')
	last_name = self.request.get('lastname')
	manager = bool(self.request.get('manager') == 'True')
	admin = True
	cinema_id = 1
	if(self.request.get('cinema')):
		cinema_id = int(self.request.get('cinema'))
	password = self.request.get('password')
	unique_properties = []
	user_data = self.user_model.create_user(user_name,
	unique_properties,
	  manager=manager, admin=True, cinema_id=cinema_id,first_name=first_name, password_raw=password,
	  last_name=last_name, verified=False)
	if not user_data[0]: #user_data is a tuple
		self.display_message('Unable to create user for username %s because of duplicate keys %s. To go back and change the name click <a href="/signup">here</a>' % (user_name, user_data[1]))
		return
    
	user = user_data[1]
	user_id = user.get_id()

	token = self.user_model.create_signup_token(user_id)

	verification_url = self.uri_for('verification', type='v', user_id=user_id,
	  signup_token=token, _full=True)

	msg = 'To validate the account, please click on the following link: <a href="{url}">{url}</a>'

	self.display_message(msg.format(url=verification_url))