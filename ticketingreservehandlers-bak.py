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

class TicketingReserveHandler(BaseHandler):
	@user_required
	def get(self):
		view=self.request.get('view',default_value='public')#service, complimentary, public
		current_user = self.auth.get_user_by_session()
		cinema_id = current_user['cinema_id']
		logging.debug(cinema_id)
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		access = 'Cashier'
		if(current_user['manager']):
			access = 'Manager'
		if(current_user['admin']):
			access = 'Admin'
		d = timedelta(hours=5, minutes=30)
		dtime = datetime.combine(datetime.date(datetime.now()+d), datetime.time(datetime.strptime("9", "%H")))
		logging.debug(" "+str(dtime) + " 9hrs")
		
		dtime = datetime.now()
		dtime = d + dtime
		time = datetime.time(dtime)
		today = datetime.date(dtime)
		
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
		
		if(dtime < show[1]):
			s = 1
		elif(dtime < show[2]):
			s = 2
		elif(dtime < show[3]):
			s = 3
		elif(dtime < show[4]):
			s = 4
		else:
			self.display_message('No more shows for today. Click <a href="/"> here </a> to go back!')
			return
		
		time_diff = show[s] - dtime
		time_diff = time_diff - mins15
		time_in_s = time_diff.total_seconds()
		time_in_millis = time_in_s * 1000
		show_text = "Std. Sale"
		
		if(time_in_millis < 0):
			time_diff = show[s] - dtime
			time_in_s = time_diff.total_seconds()
			time_in_millis = time_in_s * 1000
			show_text = "Late Sale"
		
		logging.debug("Show "+ str(s) + " " + str(show[s]))
		
		limit = [0,0,0,0,0,0]
		limit[0] = show[s].year
		limit[1] = show[s].month
		limit[2] = show[s].day
		limit[3] = show[s].hour
		limit[4] = show[s].minute
		limit[5] = show[s].second
		
		logging.debug("**************"+str(show[s].month))
		
		autosubmit = datetime.time(show[s])
		showtime = datetime.time(show[s] - mins45)
		
		showtimeview = show[s]
		show=str(s)
		types = ['box', 'balcony', 'odc', 'firstclass',]
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
		logging.debug(str(show)+" "+str(today)+" "+str(cinema_id))
		showrecord = ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', show, today, cinema_id).get()
		logging.debug(showrecord)
		seatListOutString=''
		if(showrecord):
			logging.debug(str(showrecord.key().id()))
			types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
					'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary','box_full_late', 'balcony_full_late', 'balcony_half_late', 'balcony_service_late', 'balcony_complimentary_late', 'odc_full_late', 'odc_half_late', 'odc_service_late', 
					'odc_complimentary_late', 'firstclass_full_late', 'firstclass_half_late', 'firstclass_service_late', 'firstclass_complimentary_late',]
			
			notickets = 0
			for type in types:
				ticketsale =  TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord.key().id(), type).get()
				if(ticketsale):
					seats1[type.split('_')[0]] += ticketsale.sales
					logging.debug(type.split('_')[0] + str(seats[type.split('_')[0]]))
			ticketreserve=TicketReservation.gql('WHERE show_record_id=:1', showrecord.key().id())
			if(ticketreserve):
				reservedSeatList=[]
				for ticket in ticketreserve.run():
					reservedSeatList.append(ticket.seat_number)
				seatListOutString=','.join(reservedSeatList)
				seatListOutString=','+seatListOutString+','
		qResult = ShowHistory.gql('WHERE cinema_id=:1 AND start_date<=:2 ORDER BY start_date DESC', cinema_id, today).get()
		reel = Reel.get_by_id(qResult.reel_id, parent=testing_key('default'))
		film = Film.get_by_id(reel.film_id, parent=testing_key('default'))
		#film = "Film"
		reel = "Reel"
		cinema = cinema1.name
		place = cinema1.place
		
		no_late_types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
				'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
		
		template_values = {
				'show_text' : show_text,
				'seats' : seats,
				'seats1' : seats1,
				'limit': limit,
				'cinema_id': cinema_id,
				'film': film.name,
				'reel': reel,
				'cinema' : cinema,
				'place' : place,
				'show' : show,
				'autosubmit' : autosubmit,
				'time_in_millis' : time_in_millis,
				'access' : access,
				'showtime' : showtime,
				'showtimeview' : showtimeview,
				'seatListOutString':seatListOutString,
				'seat_types':no_late_types,
				'seat_view':view,
			}
		
		self.render_template(cinema1.seatplan, template_values)
	
	@user_required
	def post(self):
		is_reprint =self.request.get('is_reprint',default_value='false')
		if(is_reprint=='true'):
			reprint_data=self.session.get('reprint_data')
			if(reprint_data):
				self.render_template('sample-reserve.html', reprint_data)	
				return
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
		logging.debug(str(show)+" "+str(today)+" "+str(cinema_id))
		showrecord = ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', show, today, cinema_id).get()
		logging.debug(showrecord)
		
		qResult = ShowHistory.gql('WHERE cinema_id=:1 AND start_date<=:2 ORDER BY start_date DESC', cinema_id, today).get()
		reel = Reel.get_by_id(qResult.reel_id, parent=testing_key('default'))
		film = Film.get_by_id(reel.film_id, parent=testing_key('default'))
		
		if(qResult.threeD):
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
		
		if(dtime > show[s] + mins1):
			latesale = True
			
		show = s
		
		if not(showrecord):
			showrecord = ShowRecord(parent=testing_key('default'))
			showrecord.cinema_id = int(self.request.get('cinema_id'))
			showrecord.show = self.request.get('show')
			current_user = self.auth.get_user_by_session()
			showrecord.user_nic = current_user['first_name'] + " " + current_user['last_name']
			showrecord.date = today
		
		showrecord.weather = ''
		#self.request.get('weather')
		showrecord.remarks = ''
		#self.request.get('remarks')
		# self.response.out.write('Success')
		
		showrecord.put()

		show_id = showrecord.key().id()

		ticket_text = []
		ticket_details = {}
		prices = []
		
		#types = [ 'odc_full', 'odc_half', 'odc_service','odc_complimentary']
		types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
				'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
		
		notickets = 0
		new_ticketsale = False
		total_price = 0
		
		inc = 0
		
		ticketprint = {}
		seatNumbers=list(set(self.request.get('seatListString').split(','))) # deduplication n splitting
		seatNumbersIndex=0
		for type in types:
			type_inc = 0
			if(latesale):
				ticketsale =  TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', show_id, type+'_late').get()
				# self.redirect('www.google.com')
			else:
				ticketsale =  TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', show_id, type).get()
			if not(ticketsale):
				new_ticketsale = True
				ticketsale = TicketSale(parent=showrecord)
				ticketsale.show_record_id = show_id
				ticketsale.ticket_type = type
				if(latesale):
					ticketsale.ticket_type = ticketsale.ticket_type+'_late'
					# self.redirect(ticketsale.ticket_type)
				ticketsale.sales = 0
			#ticketreserve=TicketReservation(parent=showrecord)
			qResult = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type, 'basic').get()
			qResult2 = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type, 'ent').get()
			
			if(int(self.request.get(type)) >0):
				ticketsale.sales += len(seatNumbers)
			else:
				ticketsale.sales += int(self.request.get(type))
			
			if(len(seatNumbers) and int(self.request.get(type)) > 0):
				price = qResult.rate
				price += qResult2.rate
				price += (cinema_nfc + cinema_theatre)
				if(is3D):
					price += 100.0
				price2 = price * int((self.request.get(type)))
				if(type.split('_')[1] == 'complimentary'):
					price = price2 = 0.0
				total_price += price2
				ticket_text.append("" +type + " : " + (self.request.get(type)) + " x " + str(price) + " = "+ str(price2))
				#for x in range (0, int((self.request.get(type)))):  ***since in reservation, only ONE type working, we can safely go for numbers of seats selected from the plan (after de-duplicating)
				for x in range (0, len(seatNumbers)):
					ticketprint[inc] = TicketPrint()
					ticketprint[inc].cinema_hall = cinema1.name
					ticketprint[inc].cinema_place = cinema1.place
					ticketprint[inc].film_name = film.name
					ticketprint[inc].show_time = showtime
					ticketprint[inc].seat_type = str.upper(type.split('_')[0])
					ticketprint[inc].ticket_type = str.upper(type.split('_')[1])
					ticketprint[inc].ticket_no = (qResult.opening + type_inc)
					ticketprint[inc].price = "LKR " + str(price) + "0"
					ticketprint[inc].seat_number=seatNumbers[x];
					
					TicketReservation(parent=showrecord, seat_number=seatNumbers[x],ticket_type=str.upper(type.split('_')[0]+"_"+type.split('_')[1]),show_record_id=show_id,late_sale=latesale).put()
					
					
					if(type.split('_')[1] == 'complimentary'):
						ticketprint[inc].price = "FREE"
					prices.append(price)
					notickets += 1
					inc += 1
					type_inc += 1
					seatNumbersIndex+=1
					
			
			if(qResult):
				if(new_ticketsale):
					ticketsale.opening_number = qResult.opening
				if(int(self.request.get(type)) >0):
					qResult.opening += len(seatNumbers)
				else:
					qResult.opening += int(self.request.get(type))
				
				qResult.put()
			else:
				ticketsale.opening_number = 0
			ticketsale.put()
			
			
		logging.info(ticket_text)
		
		ticket_text.append("Total Price : " + str(total_price))
		
		template_values = {
			"ticketprint" : ticketprint,
			"total_price" :total_price,
			"prices" : prices,
			"ticket_text" : ticket_text,
			"ticket_details" : ticket_details,
			"seat_list":seatNumbers
			}
			
		
		if(notickets > 0):
			self.session['reprint_data']=template_values
			self.render_template('sample-reserve.html', template_values)	
			return
		
		self.redirect('/seatplan')
