import datetime
import urllib
import webapp2
import cgi
import sys
import json

from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os

from datetime import datetime

from handlers import *
from datamodels import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def testing_key(testing_name=None):
    return db.Key.from_path('Testing', testing_name or 'default_testing')


class AssignQuery(webapp2.RequestHandler):
    def get(self):
        test = int(self.request.get('movie_id'))

        reels = db.GqlQuery('SELECT * FROM Reel WHERE film_id=:1', test)

        my_response = []

        for reel in reels:
            my_response.append(str(reel.reel_no))
            my_response.append(str(reel.key().id()))
        jsona = json.dumps(my_response)

        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(jsona)


class AssignHandler(BaseHandler):
    @user_required
    def get(self):
        current_user = self.auth.get_user_by_session()
        admin = current_user['admin']

        if not (admin):
            self.redirect('/')
            return

        films_query = Film.all()
        films = films_query.fetch(10000)
        cinemas_query = CinemaHall.all()
        cinemas = cinemas_query.fetch(10000)
        reels_query = Reel.all()
        reels = reels_query.fetch(10000)

        template_values = {
        'films': films,
        'reels': reels,
        'cinemas': cinemas,
        }

        self.render_template('assign.html', template_values)

    @user_required
    def post(self):

        #check for admin
        current_user = self.auth.get_user_by_session()
        admin = current_user['admin']

        if not (admin):
            self.redirect('/')
            return

        show = ShowHistory(parent=testing_key('default'))
        show.cinema_id = int(self.request.get('cinema'))
        show.reel_id = int(self.request.get('reel'))
        if (self.request.get('3d') == 'True'):
            show.threeD = True
        else:
            show.threeD = False

        start_date = self.request.get('start_date')
        show.start_date = datetime.strptime(start_date, '%m/%d/%Y').date()

        show.put()

        self.redirect('/')
		