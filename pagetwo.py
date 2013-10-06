import datetime
import urllib
import webapp2
import cgi

from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

from handlers import *
from models import *

from datetime import datetime


def testing_key(testing_name=None):
    return db.Key.from_path('Testing', testing_name or 'default_testing')


class YetAnotherAuthenticatedHandler(BaseHandler):
    def get(self):
        current_user = self.auth.get_user_by_session()
        cinema_id = current_user['cinema_id']
        cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
        self.response.out.write('Hello Seperately Authenticated World')

        template_values = {
        'cinema_id': cinema_id,
        }
        self.render_template('dailyreport.html', template_values)


class TestTwo(webapp2.RequestHandler):
    def get(self):
        qResult = Reel.gql('WHERE film_id=:1 limit 10', 163).get()
        qResult2 = Film.all().fetch(10000)
        for i in qResult2:
            key = i.key().id()
            self.response.out.write(str(i.key().id()) + '<br>')
        qResult3 = Film.get_by_id(key, parent=testing_key('default'))
        self.response.out.write(qResult3.name)

        qResult4 = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', 243, 'box_full', 'basic').get()
        self.response.out.write(qResult4.opening)
