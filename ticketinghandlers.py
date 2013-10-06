import datetime
import logging
import urllib
import webapp2
import cgi
import sys
import json

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


class TicketPrint(db.Expando):
    cinema_hall = db.StringProperty()


class TicketingHandler(BaseHandler):
    @user_required
    def get(self):
        current_user = self.auth.get_user_by_session()
        cinema_id = current_user['cinema_id']

        logging.debug(cinema_id)
        # self.response.out.write(cinema_id)

        cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))

        access = 'Cashier'
        if (current_user['manager']):
            access = 'Manager'
        if (current_user['admin']):
            access = 'Admin'
        d = timedelta(hours=5, minutes=30)
        dtime = datetime.combine(datetime.date(datetime.now() + d), datetime.time(datetime.strptime("9", "%H")))
        logging.debug(" " + str(dtime) + " 9hrs")

        dtime = datetime.now()
        dtime = d + dtime

        # dtime = datetime(2013, 03, 10, 11, 14, 30, 0)

        # self.response.out.write(dtime)
        # self.response.out.write('<br>')

        time = datetime.time(dtime)
        # self.response.out.write(time)

        today = datetime.date(dtime)
        # self.response.out.write(today)
        # self.response.out.write('<br>')

        show = {}

        show[1] = datetime.combine(today, cinema1.show_time1)
        show[2] = datetime.combine(today, cinema1.show_time2)
        show[3] = datetime.combine(today, cinema1.show_time3)
        show[4] = datetime.combine(today, cinema1.show_time4)

        mins45 = timedelta(minutes=45)
        show[1] += mins45
        show[2] += mins45
        show[3] += mins45
        show[4] += mins45

        mins30 = timedelta(minutes=30)
        mins15 = timedelta(minutes=15)

        # self.response.out.write(show[1])
        # self.response.out.write('<br>')
        # self.response.out.write(show[2])
        # self.response.out.write('<br>')
        # self.response.out.write(show[3])
        # self.response.out.write('<br>')
        # self.response.out.write(show[4])
        # self.response.out.write('<br>')

        if (dtime < show[1]):
            s = 1
        elif (dtime < show[2]):
            s = 2
        elif (dtime < show[3]):
            s = 3
        elif (dtime < show[4]):
            s = 4
        else:
            self.display_message('No more shows for today. Click <a href="/"> here </a> to go back!')
            return

        time_diff = show[s] - dtime
        time_diff = time_diff - mins15
        time_in_s = time_diff.total_seconds()
        time_in_millis = time_in_s * 1000
        show_text = "Std. Sale"

        if (time_in_millis < 0):
            time_diff = show[s] - dtime
            time_in_s = time_diff.total_seconds()
            time_in_millis = time_in_s * 1000
            show_text = "Late Sale"

        logging.debug("Show " + str(s) + " " + str(show[s]))

        limit = [0, 0, 0, 0, 0, 0]
        limit[0] = show[s].year
        limit[1] = show[s].month
        limit[2] = show[s].day
        limit[3] = show[s].hour
        limit[4] = show[s].minute
        limit[5] = show[s].second

        logging.debug("**************" + str(show[s].month))

        autosubmit = datetime.time(show[s])
        showtime = datetime.time(show[s] - mins45)

        show = str(s)
        types = ['box', 'balcony', 'odc', 'firstclass', ]
        seats = {}
        seats1 = {}
        for type in types:
            s = Seat.gql('WHERE cinema_id=:1 AND catagory=:2', cinema1.key().id(), type).get()
            seats[type] = s.number
            seats1[type] = 0

        dtime = datetime.now()
        d = timedelta(hours=5, minutes=30)
        dtime = d + dtime
        today = datetime.date(dtime)
        #check whether the show record exists:
        logging.debug(str(show) + " " + str(today) + " " + str(cinema_id))
        showrecord = ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', show, today, cinema_id).get()
        logging.debug(showrecord)
        if (showrecord):
            logging.debug(str(showrecord.key().id()))
            types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full',
                     'odc_half', 'odc_service',
                     'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service',
                     'firstclass_complimentary', 'box_full_late', 'balcony_full_late', 'balcony_half_late',
                     'balcony_service_late', 'balcony_complimentary_late', 'odc_full_late', 'odc_half_late',
                     'odc_service_late',
                     'odc_complimentary_late', 'firstclass_full_late', 'firstclass_half_late',
                     'firstclass_service_late', 'firstclass_complimentary_late', ]
            notickets = 0
            for type in types:
                ticketsale = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord.key().id(),
                                            type).get()
                if (ticketsale):
                    seats1[type.split('_')[0]] += ticketsale.sales
                    logging.debug(type.split('_')[0] + str(seats[type.split('_')[0]]))


        # self.response.out.write(show)
        # self.response.out.write('<br>')

        # place = code_no = "B"
        # run = cinema_id
        film = "Film"
        reel = "Reel"
        # day = 4
        # date = datetime.date.today()
        cinema = cinema1.name
        place = cinema1.place
        # code_no = cinema1.code_no
        # grade = cinema1.grade
        # time_in_millis = 10000

        template_values = {
        'show_text': show_text,
        'seats': seats,
        'seats1': seats1,
        'limit': limit,
        'cinema_id': cinema_id,
        'film': film,
        'reel': reel,
        'cinema': cinema,
        'place': place,
        'show': show,
        'autosubmit': autosubmit,
        'time_in_millis': time_in_millis,
        'access': access,
        'showtime': showtime,
        }

        self.render_template('tickets.html', template_values)

    @user_required
    def post(self):
        dtime = datetime.now()
        d = timedelta(hours=5, minutes=30)
        dtime = d + dtime
        today = datetime.date(dtime)
        show = self.request.get('show')
        s = int(show)
        cinema_id = int(self.request.get('cinema_id'))
        cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
        cinema_nfc = cinema1.nfc
        cinema_theatre = cinema1.theatre
        #check whether the show record exists:
        logging.debug(str(show) + " " + str(today) + " " + str(cinema_id))
        showrecord = ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', show, today, cinema_id).get()
        logging.debug(showrecord)

        qResult = ShowHistory.gql('WHERE cinema_id=:1 AND start_date<=:2 ORDER BY start_date DESC', cinema_id,
                                  today).get()
        #querySort=db.GqlQuery('select * from ShowHistory WHERE cinema_id=:1 AND start_date<=:2 ORDER BY start_date DESC', cinema_id, today)
        #qResult = querySort.get()
        reel = Reel.get_by_id(qResult.reel_id, parent=testing_key('default'))
        film = Film.get_by_id(reel.film_id, parent=testing_key('default'))

        if (qResult.threeD):
            is3D = True
        else:
            is3D = False

        show = {}

        show[1] = datetime.combine(today, cinema1.show_time1)
        show[2] = datetime.combine(today, cinema1.show_time2)
        show[3] = datetime.combine(today, cinema1.show_time3)
        show[4] = datetime.combine(today, cinema1.show_time4)

        showtime = datetime.time(show[s])

        mins30 = timedelta(minutes=30)
        show[1] += mins30
        show[2] += mins30
        show[3] += mins30
        show[4] += mins30

        mins1 = timedelta(minutes=1)

        latesale = False

        if (dtime > show[s] + mins1):
            latesale = True

        show = s

        if not (showrecord):
            showrecord = ShowRecord(parent=testing_key('default'))
            showrecord.cinema_id = int(self.request.get('cinema_id'))
            showrecord.show = self.request.get('show')
            current_user = self.auth.get_user_by_session()
            showrecord.user_nic = current_user['first_name'] + " " + current_user['last_name']
            showrecord.date = today

        showrecord.weather = self.request.get('weather')
        showrecord.remarks = self.request.get('remarks')
        # self.response.out.write('Success')

        showrecord.put()

        show_id = showrecord.key().id()

        ticket_text = []
        ticket_details = {}
        prices = []

        types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full',
                 'odc_half', 'odc_service',
                 'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service',
                 'firstclass_complimentary', ]
        notickets = 0
        new_ticketsale = False
        total_price = 0

        inc = 0

        ticketprint = {}

        for type in types:
            type_inc = 0
            if (latesale):
                ticketsale = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', show_id, type + '_late').get()
            # self.redirect('www.google.com')
            else:
                ticketsale = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', show_id, type).get()
            if not (ticketsale):
                new_ticketsale = True
                ticketsale = TicketSale(parent=showrecord)
                ticketsale.show_record_id = show_id
                ticketsale.ticket_type = type
                if (latesale):
                    ticketsale.ticket_type = ticketsale.ticket_type + '_late'
                # self.redirect(ticketsale.ticket_type)
                ticketsale.sales = 0

            qResult = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type,
                                 'basic').get()
            qResult2 = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type,
                                  'ent').get()

            ticketsale.sales += int(self.request.get(type))
            if (int(self.request.get(type))):
                price = qResult.rate
                price += qResult2.rate
                price += (cinema_nfc + cinema_theatre)
                if (is3D):
                    price += 100.0
                price2 = price * int((self.request.get(type)))
                if (type.split('_')[1] == 'complimentary'):
                    price = price2 = 0.0
                total_price += price2
                ticket_text.append(
                    "" + type + " : " + (self.request.get(type)) + " x " + str(price) + " = " + str(price2))
                for x in range(0, int((self.request.get(type)))):
                    ticketprint[inc] = TicketPrint()
                    ticketprint[inc].cinema_hall = cinema1.name
                    ticketprint[inc].cinema_place = cinema1.place
                    ticketprint[inc].film_name = film.name
                    ticketprint[inc].show_time = showtime
                    ticketprint[inc].seat_type = str.upper(type.split('_')[0])
                    ticketprint[inc].ticket_type = str.upper(type.split('_')[1])
                    ticketprint[inc].ticket_no = (qResult.opening + type_inc)
                    ticketprint[inc].price = "LKR " + str(price) + "0"
                    if (type.split('_')[1] == 'complimentary'):
                        ticketprint[inc].price = "FREE"
                    prices.append(price)
                    # ticket_details[notickets] = (self.request.get(type))
                    # ticket_details[notickets].price = str(price)
                    # ticket_detaisl[notickets].aggregrate = str(price2)
                    notickets += 1
                    inc += 1
                    type_inc += 1

            if (qResult):
                if (new_ticketsale):
                    ticketsale.opening_number = qResult.opening
                qResult.opening += int(self.request.get(type))
                qResult.put()
            else:
                ticketsale.opening_number = 0
            ticketsale.put()

        logging.info(ticket_text)

        ticket_text.append("Total Price : " + str(total_price))

        template_values = {
        "ticketprint": ticketprint,
        "total_price": total_price,
        "prices": prices,
        "ticket_text": ticket_text,
        "ticket_details": ticket_details,
        }

        if (notickets > 0):
        #if(False):
            self.render_template('sample.html', template_values)
            # self.display_message('Ticket Sale Information<br>'+str(dtime)+'<br>'+ticket_text+'</ol><br>Click <a href="/tickets"> here </a> to go back to sales!')

            return

        self.redirect('/tickets')

        # class ShowRecord(db.Model):
        # show = db.StringProperty()
        # cinema_id = db.IntegerProperty()
        # weather = db.StringProperty()
        # remarks = db.StringProperty()
        # user_id = db.IntegerProperty()
        # update = db.DateTimeProperty(auto_now_add=True)

        # class TicketSale(db.Model):
        # show_record_id = db.IntegerProperty()
        # opening_number = db.IntegerProperty()
        # ticket_type = db.StringProperty()
        # sales = db.IntegerProperty()