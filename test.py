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

from databasefilm import *
from databasehall import *
from databasefilmhallasign import *

from datetime import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def testing_key(testing_name=None):
    return db.Key.from_path('Testing', testing_name or 'default_testing')


class Test(webapp2.RequestHandler):
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


class TestTwo(webapp2.RequestHandler):
    def get(self):
        #
        data = db.GqlQuery('SELECT * FROM Reel WHERE film_id=:1', 93)
        qResult = Reel.gql('WHERE film_id=:1 limit 10', 93).get()
        qResult2 = Reel.all().fetch(10)
        for i in data:
            self.response.out.write(i.reel_no)
        self.response.out.write(qResult.reel_no)
        for i in qResult2:
            self.response.out.write(i.reel_no)
