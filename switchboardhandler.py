import datetime
import logging
import urllib
import webapp2
import cgi
import sys
import json

from webapp2_extras import auth
from webapp2_extras import sessions
from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

from handlers import *
from datamodels import *

from datetime import datetime
from datetime import timedelta

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def testing_key(testing_name=None):
  return db.Key.from_path('Testing', testing_name or 'default_testing')

class SwitchBoardHandler(BaseHandler):
  @user_required
  def get(self):
    users=self.session.get('users')
    passes=self.session.get('passes')
    halls=json.loads(self.session.get('halls'))
    hall_json=self.session.get('halls')
    #halls='halls'
    template_values = {
      'users':users,
      'passes':passes,
      'halls':halls,
      'baseUrl':self.request.host_url,
      'hall_json':hall_json,
    }
    self.auth.unset_session()
    self.render_template('switchboard.html', template_values)