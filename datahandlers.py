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
	
class ReportHandler(BaseHandler):
	@user_required
	def post(self):
		current_user = self.auth.get_user_by_session()
		cinema_id = current_user['cinema_id']
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		
		today = datetime.date(dtime)
		
		report_date = self.request.get('report_date')
		today2 = datetime.strptime(report_date,'%Y-%m-%d').date()
		
		today = today2
		
		record = DailyRecord.gql('WHERE date=:1 AND cinema_id=:2', today, cinema_id).get()
		if(self.request.get('comment')):
			record.comment = self.request.get('comment')
		if(self.request.get('comment1')):
			record.comment1 = self.request.get('comment1')
		if(self.request.get('comment2')):
			record.comment2 = self.request.get('comment2')
		if(self.request.get('comment3')):
			record.comment3 = self.request.get('comment3')
		
		record.put()
		
		self.redirect('/dailyreport?report_date='+report_date)

	@user_required
	def get(self):
		current_user = self.auth.get_user_by_session()
		cinema_id = current_user['cinema_id']
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		# cinema_leavy = cinema1.leavy
		cinema_nfc = cinema1.nfc
		cinema_theatre = cinema1.theatre
		cinema_percent = cinema1.percent
		
		if not(cinema_nfc):
			cinema_nfc = 2.9
		if not(cinema_theatre):
			cinema_theatre = 3.1
		if not(cinema_percent):
			cinema_percent = 55
		
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		
		today = datetime.date(dtime)
		
		report_date = self.request.get('report_date')
		try:
			today2 = datetime.strptime(report_date,'%Y-%m-%d').date()
		except:
			self.display_message('Invalid Date! <br>Click <a href="/"> here </a> to go back!')
			return
		
		today = today2
		
		qResult = ShowHistory.gql('WHERE cinema_id=:1 AND start_date<=:2 ORDER BY start_date DESC', cinema_id, today).get()
	
		if not(qResult):
			self.display_message('Invalid Date! <br>Click <a href="/"> here </a> to go back!')
			return
		
		day_no = (today - qResult.start_date + timedelta(days=1)).days
		
		logging.info(qResult.reel_id)
		
		reel = Reel.get_by_id(qResult.reel_id, parent=testing_key('default'))
		
		logging.info(reel.film_id)
		
		film = Film.get_by_id(reel.film_id, parent=testing_key('default'))
		
		logging.info(film.name)
		
		types = ['box', 'balcony', 'odc', 'firstclass',]
		seats = {}
		for type in types:
			s = Seat.gql('WHERE cinema_id=:1 AND catagory=:2', cinema1.key().id(), type).get()
			seats[type] = s.number
		
		types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'odc_full', 'odc_half', 'odc_service',
		 'firstclass_full', 'firstclass_half', 'firstclass_service',
		]
		
		FINALS = [{}, {}, {}, {}]
		TOTAL_SHOWS = 0
		tariff = {}
		inc = 0
		TOTAL = {0:[0, 0, 0, 0], 1:[0, 0, 0, 0], 2:[0, 0, 0, 0], 3:[0, 0, 0, 0], 4:[0, 0, 0, 0], 5:[0, 0, 0, 0], 6:[0, 0, 0, 0], 
				 7:[0, 0, 0, 0], 8:[0, 0, 0, 0], 9:[0, 0, 0, 0],}
		for type in types:
			tariff[inc] = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', cinema_id, type, 'basic').get()
			TOTAL[inc][2] = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', cinema_id, type, 'ent').get().rate
			inc += 1
		
		
		##Show 1
		show = [{},{},{},{}]
		
		showrecord = [ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', str(i), today, cinema_id).get() for i in range (1,5)]
		
		total_revenue = [0,0,0,0]
		total_sales = [0,0,0,0]
		
		closing_numbers = [{}, {}, {}, {}]
		show_names = ['1st Show', '2nd Show', '3rd Show', '4th Show', ]
		show_times = [cinema1.show_time1, cinema1.show_time2, cinema1.show_time3, cinema1.show_time4]
		colours = ["background-color:rgba(204,253,204,1);", "background-color:rgba(102,204,204,1);", "background-color:rgba(102,204,204,1);", "background-color:rgba(204,153,204,1);",]
		weather = ""
		for i in range(0, 4):
			if(showrecord[i]):
				TOTAL_SHOWS += 1
				inc = 0
				logging.info(str(i)+'<br>')
				weather = showrecord[i].weather
				for type in types:
					show[i][inc] = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord[i].key().id(), type).get()
					show[i][inc].rs = show[i][inc].sales * tariff[inc].rate
					show[i][inc].show_name = show_names[i]
					show[i][inc].show_time = show_times[i]
					show[i][inc].colour = colours[i]
					total_sales[i] += show[i][inc].sales
					TOTAL[inc][0] += show[i][inc].sales
					TOTAL[inc][3] = TOTAL[inc][0] * TOTAL[inc][2]
					TOTAL[inc][1] += show[i][inc].rs
					total_revenue[i] += show[i][inc].rs
					show[i][inc].total_sales = total_sales[i]
					show[i][inc].total_revenue = total_revenue[i]
					FINALS[i]['P'] = show[i][inc].total_sales
					FINALS[i]['R'] = show[i][inc].total_revenue
					logging.debug(type+" "+str(show[i][inc].rs)+"="+str(show[i][inc].sales) +"*"+ str(tariff[inc].rate) + " " +tariff[inc].ticket_type)
					
					if(show[i][inc]):
						logging.info(type+'='+str(show[i][inc].opening_number)+' - ')
						show[i][inc].show_record_id = show[i][inc].opening_number + show[i][inc].sales
					inc += 1
		
		TOTS = [0, 0, 0, 0]
		inc = 0
		for type in types:
			TOTS[0] += TOTAL[inc][0]
			TOTS[1] += TOTAL[inc][1]
			TOTS[2] += TOTAL[inc][2]
			TOTS[3] += TOTAL[inc][3]
			inc += 1
			
		# Late Sale Calculations Start Here!
		
		types = ['box_full_late', 'balcony_full_late', 'balcony_half_late', 'balcony_service_late', 'odc_full_late', 'odc_half_late', 'odc_service_late',
		 'firstclass_full_late', 'firstclass_half_late', 'firstclass_service_late',
		]
		inc = 0
		TOTAL2 = {0:[0, 0, 0, 0], 1:[0, 0, 0, 0], 2:[0, 0, 0, 0], 3:[0, 0, 0, 0], 4:[0, 0, 0, 0], 5:[0, 0, 0, 0], 6:[0, 0, 0, 0], 
				 7:[0, 0, 0, 0], 8:[0, 0, 0, 0], 9:[0, 0, 0, 0],}
		for type in types:
			TOTAL2[inc][2] = TOTAL[inc][2]
			inc += 1
		
		show2 = [{},{},{},{}]
		
		total_revenue = [0,0,0,0]
		total_sales = [0,0,0,0]
		
		closing_numbers = [{}, {}, {}, {}]
		for i in range(0, 4):
			if(showrecord[i]):
				inc = 0
				logging.info(str(i)+'<br>')
				for type in types:
					show2[i][inc] = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord[i].key().id(), type).get()
					if not(show2[i][inc]):
						showrecord[i] = None
						break
					logging.debug("***********"+str(show2)+" "+str(i)+" "+str(show2[i]) + " " + str(tariff[inc]))
					show2[i][inc].show_name = show_names[i]
					show2[i][inc].rs = show2[i][inc].sales * tariff[inc].rate
					show2[i][inc].show_time = show_times[i]
					show2[i][inc].colour = colours[i]
					total_sales[i] += show2[i][inc].sales
					TOTAL2[inc][0] += show2[i][inc].sales
					TOTAL2[inc][3] = TOTAL2[inc][0] * TOTAL2[inc][2]
					TOTAL2[inc][1] += show2[i][inc].rs
					total_revenue[i] += show2[i][inc].rs
					show2[i][inc].total_sales = total_sales[i]
					show2[i][inc].total_revenue = total_revenue[i]
					
					FINALS[i]['P'] += show2[i][inc].sales
					FINALS[i]['R'] += show2[i][inc].rs
				
					if(show2[i][inc]):
						logging.info(type+'='+str(show[i][inc].opening_number)+' - ')
						show2[i][inc].show_record_id = show2[i][inc].opening_number + show2[i][inc].sales
					inc += 1
		
		TOTS2 = [0, 0, 0, 0]
		inc = 0
		for type in types:
			TOTS2[0] += TOTAL2[inc][0]
			TOTS2[1] += TOTAL2[inc][1]
			TOTS2[2] += TOTAL2[inc][2]
			TOTS2[3] += TOTAL2[inc][3]
			inc += 1
		
		# Late Sale Calculations End Here!
		
		# Complimentary Calculations Start Here!
		
		types = ['balcony_complimentary', 'odc_complimentary', 'firstclass_complimentary','balcony_complimentary_late', 'odc_complimentary_late', 'firstclass_complimentary_late',]
		inc = 0
		TOTAL3 = {0:[0, 0, 0, 0], 1:[0, 0, 0, 0], 2:[0, 0, 0, 0], 3:[0, 0, 0, 0], 4:[0, 0, 0, 0], 5:[0, 0, 0, 0],}
		for type in types:
			TOTAL3[inc][2] = 0
			inc += 1
		
		show3 = [{},{},{},{}]
		
		total_revenue = [0,0,0,0]
		total_sales = [0,0,0,0]
		
		showrecord = [ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', str(i), today, cinema_id).get() for i in range (1,5)]
		
		closing_numbers = [{}, {}, {}, {}]
		
		try:	
			for i in range(0, 4):
				if(showrecord[i]):
					inc = 0
					logging.info(str(i)+'<br>')
					for type in types:
						show3[i][inc] = TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord[i].key().id(), type).get()
						if(show3[i][inc]):
							logging.debug("***********"+str(show3)+" "+str(inc)+" "+str(show3[i][inc].ticket_type) + " " + str(tariff[inc]))
							show3[i][inc].show_name = show_names[i]
							show3[i][inc].rs = show3[i][inc].sales * tariff[inc].rate
							show3[i][inc].show_time = show_times[i]
							show3[i][inc].colour = colours[i]
							total_sales[i] += show3[i][inc].sales
							TOTAL3[inc][0] += show3[i][inc].sales
							TOTAL3[inc][3] = TOTAL3[inc][0] * TOTAL3[inc][2]
							TOTAL3[inc][1] += show3[i][inc].rs
							total_revenue[i] += show3[i][inc].rs
							show3[i][inc].total_sales = total_sales[i]
							show3[i][inc].total_revenue = total_revenue[i]
					
						if(show3[i][inc]):
							logging.info(type+'='+str(show[i][inc].opening_number)+' - ')
							show3[i][inc].show_record_id = show3[i][inc].opening_number + show3[i][inc].sales
						inc += 1
		except:
			self.display_message('Late Sale Information Incomplete!<br>Click <a href="/"> here </a> to go back!')
			return	
		TOTS3 = [0, 0, 0, 0]
		inc = 0
		for type in types:
			TOTS3[0] += TOTAL3[inc][0]
			TOTS3[1] += TOTAL3[inc][1]
			TOTS3[2] += TOTAL3[inc][2]
			TOTS3[3] += TOTAL3[inc][3]
			inc += 1		
		# Complimentary Calculations End Here!
		
		GRAND = {}		
				
		GRAND['P'] = TOTS[0] + TOTS2[0]
		GRAND['R'] = TOTS[1] + TOTS2[1]
		GRAND['T'] = TOTS[3] + TOTS2[3]
		GRAND['C'] = TOTS3[0]
		
		LEAVY = GRAND['P'] * (cinema_nfc + cinema_theatre)
		NFC = GRAND['P'] * (cinema_nfc)
		THEATRE = GRAND['P'] * (cinema_theatre)
		GRAND_TOTAL = LEAVY + GRAND['R'] + GRAND['T']
		SHARE = GRAND['R']*(cinema_percent/100)
		
		GRAND['P'] = TOTS[0] + TOTS2[0] + TOTS3[0]
		
		BFTOTAL_SHOWS_M = BFLEAVY = BFGRAND_P = BFGRAND_C = BFGRAND_T = BFGRAND_R = BFGRAND_R_M = BFTOTAL_SHOWS = BFSHARE = 0
		BFGRAND_P_M = BFGRAND_C_M = 0
		
		## Creating History!
		date = qResult.start_date
		while(date < today):
			record = DailyRecord.gql('WHERE date=:1 AND cinema_id=:2', date, cinema_id).get()
			if(date.day == 1):
				BFGRAND_R_M = 0
				BFTOTAL_SHOWS_M = 0
				BFGRAND_P_M = 0
				BFGRAND_C_M = 0
			if(record):
				BFTOTAL_SHOWS += record.shows
				BFTOTAL_SHOWS_M += record.shows
				BFGRAND_P += record.patrons
				BFGRAND_P_M += record.patrons
				BFGRAND_R += record.revenue
				BFGRAND_R_M += record.revenue
				BFGRAND_T += record.tax
				BFGRAND_C += record.complimentary
			date = date + timedelta(days=1)
		##
		
		BFLEAVY = (BFGRAND_P - BFGRAND_C) * (cinema_nfc + cinema_theatre)
		BFNFC = (BFGRAND_P - BFGRAND_C) * (cinema_nfc)
		BFTHEATRE = (BFGRAND_P - BFGRAND_C) * (cinema_theatre)

		BFSHARE = BFGRAND_R*(cinema_percent/100)
		
		FINLEAVY = BFLEAVY + LEAVY
		FINNFC = BFNFC + NFC
		FINTHEATRE = BFTHEATRE + THEATRE
		FINGRAND_T = BFGRAND_T + GRAND['T']
		FINSHARE = BFSHARE + SHARE
		FINGRAND_R = BFGRAND_R + GRAND['R']
		FINGRAND_R_M = BFGRAND_R_M + GRAND['R']
		FINGRAND_P_M = BFGRAND_P_M + GRAND['P']
		FINTOTAL_SHOWS_M = BFTOTAL_SHOWS_M + TOTAL_SHOWS
		
		#no of patrons EXcluding complimentary
		PAT_TD = GRAND['P'] - TOTS3[0]
		PAT_BF = BFGRAND_P - BFGRAND_C
		PAT_BF_M = BFGRAND_P_M - BFGRAND_C_M
		
		
		record = DailyRecord.gql('WHERE date=:1 AND cinema_id=:2', today, cinema_id).get()
		if not(record):
			record = DailyRecord(parent=testing_key('default'))
			record.date = today
			record.cinema_id = cinema1.key().id()
		
		no_comment = no_comment1 = no_comment2 = no_comment3 = current_user['manager']
		comment = comment1 = comment2 = comment3 = ""
		if(record.comment):
			no_comment = False
			comment = record.comment
		
		if(record.comment1):
			no_comment1 = False
			comment1 = record.comment1
		
		if(record.comment2):
			no_comment2 = False
			comment2 = record.comment2
		
		if(record.comment3):
			no_comment3 = False
			comment3 = record.comment3
		
		
		record.shows = TOTAL_SHOWS
		record.patrons = GRAND['P']
		record.revenue = float(GRAND['R'])
		record.tax = float(GRAND['T'])
		record.complimentary = GRAND['C']
		
		record.put()
		
		template_values = {
				'PAT_TD' : PAT_TD,
				'PAT_BF' : PAT_BF,
				'PAT_BF_M' : PAT_BF_M,
				'weather' : weather,
				'comment' : comment,
				'comment1' : comment1,
				'comment2' : comment2,
				'comment3' : comment3,
				'report_date' : report_date,
				'no_comment' : no_comment,
				'no_comment1' : no_comment1,
				'no_comment2' : no_comment2,
				'no_comment3' : no_comment3,
				'BFNFC' : BFNFC,
				'BFTHEATRE' : BFTHEATRE,
				'BFLEAVY' : BFLEAVY, 'BFGRAND_P': BFGRAND_P, 'BFGRAND_T': BFGRAND_T, 'BFGRAND_R': BFGRAND_R, 
				'BFGRAND_R_M': BFGRAND_R_M, 'BFTOTAL_SHOWS': BFTOTAL_SHOWS, 'BFSHARE': BFSHARE,
				'FINLEAVY' : FINLEAVY, 'FINGRAND_T': FINGRAND_T, 'FINGRAND_R': FINGRAND_R, 
				'FINGRAND_R_M': FINGRAND_R_M,'FINSHARE': FINSHARE,
				'FINTOTAL_SHOWS_M': FINTOTAL_SHOWS_M, 'FINGRAND_P_M': FINGRAND_P_M,
				'FINNFC' : FINNFC,
				'FINTHEATRE' : FINTHEATRE,
				'SHARE' : SHARE,
				'TOTAL_SHOWS' : TOTAL_SHOWS,
				'LEAVY' : LEAVY,
				'NFC' : NFC,
				'THEATRE' : THEATRE,
				'GRAND_TOTAL' : GRAND_TOTAL,
				'GRAND' : GRAND,
				'FINALS' : FINALS,
				'show' : show,
				'show2': show2,
				'show3': show3,
				'showrecord' : showrecord,
				'closing_numbers' : closing_numbers,
				'day_no': day_no,
				'reel': reel,
				'cinema': cinema1,
				'date': today,
				'film': film,
				'tariff' : tariff,
				'TOTAL' : TOTAL,
				'TOTS' : TOTS,
				'TOTAL2' : TOTAL2,
				'TOTS2' : TOTS2,
				'TOTAL3' : TOTAL3,
				'TOTS3' : TOTS3,
				'seats' : seats,
				# 'TOTAL_REVENUE' : TOTAL_REVENUE,
				# 'TOTAL_ENT' : TOTAL_ENT,
				}
		self.render_template('dailyreportviewer.html', template_values)

class EntryHandler(BaseHandler):
	@user_required
	def get(self):
		current_user = self.auth.get_user_by_session()
		cinema_id = current_user['cinema_id']
		
		logging.debug(cinema_id)
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		
		access = 'Cashier'
		if(current_user['manager']):
			access = 'Manager'
		if(current_user['admin']):
			access = 'Admin'
			
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		time = datetime.time(dtime)
		today = datetime.date(dtime)
		show = {}
		
		show[1] = datetime.combine(today, cinema1.show_time1)
		show[2] = datetime.combine(today, cinema1.show_time2)
		show[3] = datetime.combine(today, cinema1.show_time3)
		show[4] = datetime.combine(today, cinema1.show_time4)
		
		mins45 = timedelta(minutes=45)
		mins30 = timedelta(minutes=30)
		mins15 = timedelta(minutes=15)
		show[1] += mins45
		show[2] += mins45
		show[3] += mins45
		show[4] += mins45
		if(dtime < show[1]):
			s = 1
		elif(dtime < show[2]):
			s = 2
		elif(dtime < show[3]):
			s = 3
		elif(dtime < show[4]):
			s = 4
		else:
			s = 0
			self.display_message('No more shows for today. Click <a href="/"> here </a> to go back!')
			return
		
		time_diff = show[s] - mins15 - dtime
		time_in_s = time_diff.total_seconds()
		time_in_millis = time_in_s * 1000
		
		if(time_in_millis <= 0):
			time_in_millis = 1
		
		logging.debug("Show "+ str(s) + " " + str(show[s]))
		
		limit = [0,0,0,0,0,0]
		show[s] = show[s] - mins15
		limit[0] = show[s].year
		limit[1] = show[s].month
		limit[2] = show[s].day
		limit[3] = show[s].hour
		limit[4] = show[s].minute
		limit[5] = show[s].second
		show[s] = show[s] + mins15
		
		logging.debug("**************"+str(show[s].month))
		
		autosubmit = datetime.time(show[s])
		showtime = datetime.time(show[s] - mins45)
		show = s
		
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
		if(showrecord):
			logging.debug(str(showrecord.key().id()))
			types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
					'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
			notickets = 0
			for type in types:
				ticketsale =  TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord.key().id(), type).get()
				seats1[type.split('_')[0]] += ticketsale.sales
				logging.debug(type.split('_')[0] + str(seats[type.split('_')[0]]))
		film = "Film"
		reel = "Reel"
		cinema = cinema1.name
		place = cinema1.place

		
		template_values = {
				'seats1' : seats1,
				'seats' : seats,
				'limit': limit,
				'cinema_id': cinema_id,
				# 'run': run,
				'film': film,
				'reel': reel,
				# 'day': day,
				# 'date': date,
				'cinema' : cinema,
				'place' : place,
				# 'code_no' : code_no,
				# 'grade' : grade,
				'show' : show,
				'autosubmit' : autosubmit,
				'time_in_millis' : time_in_millis,
				'access' : access,
				'showtime' : showtime,
			}
		
		self.render_template('dataentry.html', template_values)
		
	@user_required
	def post(self):
		self.response.out.write('Success')
		showrecord = ShowRecord(parent=testing_key('default'))
		showrecord.cinema_id = int(self.request.get('cinema_id'))
		showrecord.show = self.request.get('show')
		showrecord.weather = self.request.get('weather')
		showrecord.remarks = self.request.get('remarks')
		
		current_user = self.auth.get_user_by_session()
		showrecord.user_nic = current_user['first_name'] + " " + current_user['last_name']
		
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		today = datetime.date(dtime)

		showrecord.date = today
		
		showrecord.put()
		
		show_id = showrecord.key().id()
		
		types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
				'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
		for type in types:
			ticketsale = TicketSale(parent=showrecord)
			ticketsale.show_record_id = show_id
			ticketsale.ticket_type = type
			ticketsale.sales = int(self.request.get(type))
			
			qResult = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type, 'basic').get()
			if(qResult):
				ticketsale.opening_number = qResult.opening
				qResult.opening += ticketsale.sales
				qResult.put()
			else:
				ticketsale.opening_number = 0
			ticketsale.put()
				
		self.redirect('/latesale')

class LateHandler(BaseHandler):
	@user_required
	def get(self):
		current_user = self.auth.get_user_by_session()
		cinema_id = current_user['cinema_id']
		logging.debug(cinema_id)
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		
		access = 'Cashier'
		if(current_user['manager']):
			access = 'Manager'
		if(current_user['admin']):
			access = 'Admin'
			
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		time = datetime.time(dtime)
		today = datetime.date(dtime)
		
		show = {}
		
		show[1] = datetime.combine(today, cinema1.show_time1)
		show[2] = datetime.combine(today, cinema1.show_time2)
		show[3] = datetime.combine(today, cinema1.show_time3)
		show[4] = datetime.combine(today, cinema1.show_time4)
		
		mins45 = timedelta(minutes=45)
		mins30 = timedelta(minutes=30)
		mins15 = timedelta(minutes=15)
		show[1] += mins45
		show[2] += mins45
		show[3] += mins45
		show[4] += mins45
		
		if(dtime < show[1]):
			s = 1
		elif(dtime < show[2]):
			s = 2
		elif(dtime < show[3]):
			s = 3
		elif(dtime < show[4]):
			s = 4
		else:
			s = 0
			self.display_message('No more shows for today. Click <a href="/"> here </a> to go back!')
			return
		
		time_diff = show[s] - dtime
		time_in_s = time_diff.total_seconds()
		time_in_millis = time_in_s * 1000
		
		if(time_in_millis < 0 ):
			time_in_millis = 0
		
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
		
		show = str(s)
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
		if(showrecord):
			logging.debug(str(showrecord.key().id()))
			types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
					'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
			notickets = 0
			for type in types:
				ticketsale =  TicketSale.gql('WHERE show_record_id=:1 AND ticket_type=:2', showrecord.key().id(), type).get()
				seats1[type.split('_')[0]] += ticketsale.sales
				logging.debug(type.split('_')[0] + str(seats[type.split('_')[0]]))
		
		film = "Film"
		reel = "Reel"
		
		cinema = cinema1.name
		place = cinema1.place
		
		template_values = {
				'seats1' : seats1,
				'seats' : seats,
				'limit': limit,
				'cinema_id': cinema_id,
				# 'run': run,
				'film': film,
				'reel': reel,
				# 'day': day,
				# 'date': date,
				'cinema' : cinema,
				'place' : place,
				# 'code_no' : code_no,
				# 'grade' : grade,
				'show' : show,
				'autosubmit' : autosubmit,
				'time_in_millis' : time_in_millis,
				'access' : access,
				'showtime' : showtime,
			}
		
		self.render_template('dataentrylate.html', template_values)	
	
	@user_required
	def post(self):
		self.response.out.write('Success')
		
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		today = datetime.date(dtime)
		show = self.request.get('show')
		s = int(show)
		cinema_id = int(self.request.get('cinema_id'))
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		#check whether the show record exists:
		logging.debug(str(show)+" "+str(today)+" "+str(cinema_id))
		
		showrecord = ShowRecord.gql('WHERE show=:1 AND date=:2 AND cinema_id=:3', show, today, cinema_id).get()
		
		logging.debug(showrecord)
		
		if not(showrecord):
			logging.debug("No Show Records Found - Creating New Record"+str(show)+" "+str(today)+" "+str(cinema_id))
			showrecord = ShowRecord(parent=testing_key('default'))
			showrecord.cinema_id = int(self.request.get('cinema_id'))
			showrecord.show = self.request.get('show')
			
		
		showrecord.weather = self.request.get('weather')
		showrecord.remarks = self.request.get('remarks')
		
		current_user = self.auth.get_user_by_session()
		showrecord.user_nic = current_user['first_name'] + " " + current_user['last_name']
		
		dtime = datetime.now()
		d = timedelta(hours=5, minutes=30)
		dtime = d + dtime
		today = datetime.date(dtime)

		showrecord.date = today
		
		showrecord.put()
		
		show_id = showrecord.key().id()
		
		types = ['box_full', 'balcony_full', 'balcony_half', 'balcony_service', 'balcony_complimentary', 'odc_full', 'odc_half', 'odc_service', 
				'odc_complimentary', 'firstclass_full', 'firstclass_half', 'firstclass_service', 'firstclass_complimentary',]
		for type in types:
			ticketsale = TicketSale(parent=showrecord)
			ticketsale.show_record_id = show_id
			ticketsale.ticket_type = type+'_late'
			ticketsale.sales = int(self.request.get(type+'_late'))
			
			qResult = Tariff.gql('WHERE cinema_id=:1 AND ticket_type=:2 AND type=:3', showrecord.cinema_id, type, 'basic').get()
			if(qResult):
				ticketsale.opening_number = qResult.opening
				qResult.opening += ticketsale.sales
				qResult.put()
			else:
				ticketsale.opening_number = 0
			ticketsale.put()
				
		self.redirect('/')