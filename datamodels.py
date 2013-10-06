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
from datetime import time


class CinemaHall(db.Model):
    code_no = db.StringProperty()
    name = db.StringProperty()
    place = db.StringProperty()
    seatplan = db.StringProperty()
    seatplan_balcony = db.StringProperty()
    seatplan_box = db.StringProperty()
    grade = db.StringProperty()
    distributor = db.StringProperty()
    show_time1 = db.TimeProperty()
    show_time2 = db.TimeProperty()
    show_time3 = db.TimeProperty()
    show_time4 = db.TimeProperty()

    nfc = db.FloatProperty()
    theatre = db.FloatProperty()
    percent = db.FloatProperty()


class Seat(db.Model):
    cinema_id = db.IntegerProperty()
    catagory = db.StringProperty()
    number = db.IntegerProperty()
    update = db.DateTimeProperty()


class ShowTime(db.Model):
    cinema_id = db.IntegerProperty()
    show_title = db.StringProperty()
    start_time = db.TimeProperty()
    update = db.DateTimeProperty(auto_now_add=True)


class Tariff(db.Model):
    cinema_id = db.IntegerProperty()
    ticket_type = db.StringProperty()
    type = db.StringProperty()
    rate = db.FloatProperty()
    opening = db.IntegerProperty()
    update = db.DateTimeProperty(auto_now_add=True)
    opening = db.IntegerProperty()

##
# Can include starting number
##


class Film(db.Model):
    name = db.StringProperty()


class Reel(db.Model):
    reel_no = db.StringProperty()
    film_id = db.IntegerProperty()


class ShowHistory(db.Model):
    cinema_id = db.IntegerProperty()
    start_date = db.DateProperty()
    reel_id = db.IntegerProperty()
    threeD = db.BooleanProperty()
    update = db.DateTimeProperty(auto_now_add=True)


class ShowRecord(db.Model):
    show = db.StringProperty()
    date = db.DateProperty()
    cinema_id = db.IntegerProperty()
    weather = db.StringProperty()
    remarks = db.StringProperty()
    user_nic = db.StringProperty()
    update = db.DateTimeProperty(auto_now_add=True)


class TicketSale(db.Model):
    show_record_id = db.IntegerProperty()
    ticket_type = db.StringProperty()
    sales = db.IntegerProperty()
    opening_number = db.IntegerProperty()

class TicketReservation(db.Model):
    seat_number = db.StringProperty()
    ticket_type = db.StringProperty()
    show_record_id = db.IntegerProperty()
    late_sale = db.BooleanProperty()
    sale_person = db.StringProperty()
    sale_time = db.DateProperty()


class DailyRecord(db.Model):
    comment = db.StringProperty()
    comment1 = db.StringProperty()
    comment2 = db.StringProperty()
    comment3 = db.StringProperty()
    date = db.DateProperty()
    cinema_id = db.IntegerProperty()
    shows = db.IntegerProperty()
    patrons = db.IntegerProperty()
    revenue = db.FloatProperty()
    tax = db.FloatProperty()
    complimentary = db.IntegerProperty()