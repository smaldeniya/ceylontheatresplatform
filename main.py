from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

import logging
import os.path
import os
import webapp2
import sys

from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from pagetwo import *
from handlers import *
from hallhandlers import *
from filmhandlers import *
from assignhandlers import *
from datahandlers import *
from ticketinghandlers import *
from ticketingreservehandlers import *
from signup2 import *
from switchboardhandler import *

config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['first_name', 'last_name', 'manager', 'admin', 'cinema_id']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name='home'),
    webapp2.Route('/_ah/admin', SignupHandler, name='adminpage'),
    webapp2.Route('/signup', SignupHandler),
    webapp2.Route('/admincreate', SignupHandlerTwo),
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
      handler=VerificationHandler, name='verification'),
    webapp2.Route('/password', SetPasswordHandler),
    webapp2.Route('/login', LoginHandler, name='login'),
    webapp2.Route('/logout', LogoutHandler, name='logout'),
    webapp2.Route('/forgot', ForgotPasswordHandler, name='forgot'),
    webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated'),
	webapp2.Route('/addhall', AddHallHandler, name='addhall'),
	webapp2.Route('/addfilm', AddFilmHandler, name='addfilm'),
	webapp2.Route('/addcopies', AddCopyHandler, name='addcopies'),
	webapp2.Route('/assign', AssignHandler, name='assign'),
	webapp2.Route('/assignquery', AssignQuery, name='assignquery'),
	webapp2.Route('/dataentry', EntryHandler, name='dataentry'),
	webapp2.Route('/dailyreport', ReportHandler, name='dailyreport'),
	webapp2.Route('/tickets', TicketingHandler, name='tickets'),
	webapp2.Route('/latesale', LateHandler, name='latesale'),
	webapp2.Route('/switchboard', SwitchBoardHandler, name='switchboard'),
	webapp2.Route('/seatplan', TicketingReserveHandler, name='seatplan'),
], debug=True, config=config)

logging.getLogger().setLevel(logging.DEBUG)
