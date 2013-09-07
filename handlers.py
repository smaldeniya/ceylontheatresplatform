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

class BaseHandler(webapp2.RequestHandler):
  @webapp2.cached_property
  def auth(self):
    """Shortcut to access the auth instance as a property."""
    return auth.get_auth()

  @webapp2.cached_property
  def user_info(self):
    """Shortcut to access a subset of the user attributes that are stored
    in the session.

    The list of attributes to store in the session is specified in
      config['webapp2_extras.auth']['user_attributes'].
    :returns
      A dictionary with most user information
    """
    return self.auth.get_user_by_session()

  @webapp2.cached_property
  def user(self):
    """Shortcut to access the current logged in user.

    Unlike user_info, it fetches information from the persistence layer and
    returns an instance of the underlying model.

    :returns
      The instance of the user model associated to the logged in user.
    """
    u = self.user_info
    return self.user_model.get_by_id(u['user_id']) if u else None

  @webapp2.cached_property
  def user_model(self):
    """Returns the implementation of the user model.

    It is consistent with config['webapp2_extras.auth']['user_model'], if set.
    """    
    return self.auth.store.user_model

  @webapp2.cached_property
  def session(self):
      """Shortcut to access the current session."""
      return self.session_store.get_session(backend="datastore")

  def render_template(self, view_filename, params={}):
    user = self.user_info
    params['user'] = user
    path = os.path.join(os.path.dirname(__file__), 'views', view_filename)
    self.response.out.write(template.render(path, params))

  def display_message(self, message):
    """Utility function to display a template with a simple message."""
    params = {
      'message': message
    }
    self.render_template('message.html', params)

  # this is needed for webapp2 sessions to work
  def dispatch(self):
      # Get a session store for this request.
      self.session_store = sessions.get_store(request=self.request)

      try:
          # Dispatch the request.
          webapp2.RequestHandler.dispatch(self)
      finally:
          # Save all sessions.
          self.session_store.save_sessions(self.response)

class MainHandler(BaseHandler):
  @user_required
  def get(self):
	current_user = self.auth.get_user_by_session()
	admin = current_user['admin']
	if(admin):
		self.render_template('admin.html')
	else:
		cinema_id = current_user['cinema_id']
		logging.debug(cinema_id)
		cinema1 = CinemaHall.get_by_id(cinema_id, parent=testing_key('default'))
		hall_balcony=0
		hall_box=0
		if(getattr(cinema1, 'seatplan_balcony','')!=''):
			hall_balcony=1
		if(getattr(cinema1, 'seatplan_box','')!=''):
			hall_balcony=1
		values={
			'ifbalcony':hall_balcony,
			'ifbox':hall_box,
			}
		self.render_template('user.html',values)
		
class SignupHandler(BaseHandler):
  def get(self):
	#check for admin
    current_user = self.auth.get_user_by_session()
    admin = current_user['admin']

    if not(admin):
      self.redirect('/')
      return
	  
    cinemas_query = CinemaHall.all()
    cinemas = cinemas_query.fetch(10000)
	
    template_values = {'cinemas': cinemas}
    self.render_template('signup.html', template_values)

  def post(self):
	user_name = self.request.get('username')
	first_name = self.request.get('firstname')
	last_name = self.request.get('lastname')
	manager = bool(self.request.get('manager') == 'True')
	admin = False
	cinema_id = 1
	if(self.request.get('cinema')):
		cinema_id = int(self.request.get('cinema'))
	password = self.request.get('password')
	
	unique_properties = []
	user_data = self.user_model.create_user(user_name,
	unique_properties,
	  manager=manager, admin=admin, cinema_id=cinema_id,first_name=first_name, password_raw=password,
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

class ForgotPasswordHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')

    user = self.user_model.get_by_auth_id(username)
    if not user:
      logging.info('Could not find any user entry for username %s', username)
      self._serve_page(not_found=True)
      return

    user_id = user.get_id()
    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='p', user_id=user_id,
      signup_token=token, _full=True)

    sender_address = "Rajith Vidanaarachchi <rajith@yalabz.com>"
    user_address = "rajith.vidanaarachchi@gmail.com"
    subject = "Reset Password"
    body = """
Send an email to user in order to reset their password. \
          They will be able to do so by visiting <a href="{url}">{url}</a>
    """
    mail.send_mail(sender_address, user_address, subject, body)  
	
    msg = 'Contact Global Mesh to get your new password.'

    self.display_message(msg.format(url=verification_url))
  
  def _serve_page(self, not_found=False):
    username = self.request.get('username')
    params = {
      'username': username,
      'not_found': not_found
    }
    self.render_template('forgot.html', params)


class VerificationHandler(BaseHandler):
  def get(self, *args, **kwargs):
    user = None
    user_id = kwargs['user_id']
    signup_token = kwargs['signup_token']
    verification_type = kwargs['type']
    user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
      'signup')
    if not user:
      logging.info('Could not find any user with id "%s" signup token "%s"',
        user_id, signup_token)
      self.abort(404)

    if verification_type == 'v':

      self.user_model.delete_signup_token(user.get_id(), signup_token)

      if not user.verified:
        user.verified = True
        user.put()
	  
      adduser_url = 'saving more variables on /signup'
      msg = 'User email address has been verified. Click <a href="{url}">here</a> to add more users'
      self.display_message(msg.format(url=adduser_url))

      # self.display_message('User email address has been verified. Add more users at')
      return
    elif verification_type == 'p':
      # supply user to the page
      params = {
        'user': user,
        'token': signup_token
      }
      self.render_template('resetpassword.html', params)
    else:
      logging.info('verification type not supported')
      self.abort(404)

class SetPasswordHandler(BaseHandler):

  @user_required
  def post(self):
    password = self.request.get('password')
    old_token = self.request.get('t')

    if not password and password != self.request.get('confirm_password'):
      self.display_message('passwords do not match')
      return

    user = self.user
    user.set_password(password)
    user.put()

    self.user_model.delete_signup_token(user.get_id(), old_token)
    
    self.display_message('Password updated')

class LoginHandler(BaseHandler):
  
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    passes = self.request.get('passes',default_value='false')
    users = self.request.get('users',default_value='false')
    halls = self.request.get('halls',default_value='false')
    localURL = self.request.get('local',default_value='false')

    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      current_user=self.auth.get_user_by_session()
      self.session['localURL']=localURL
      self.session['users']=users
      self.session['passes']=passes
      self.session['halls']=halls
      self.redirect(self.uri_for('home'))
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      logging.info('Login failed for user %s because of %s', username, type(e))
      self._serve_page(True)

  def _serve_page(self, failed=False):
    current_user = self.auth.get_user_by_session()
    if(current_user):
	  self.redirect('/')
    username = self.request.get('username')
    params = {
      'username': username,
      'failed': failed
    }
    self.render_template('login.html', params)

class LogoutHandler(BaseHandler):
  def get(self):
    
    current_user=self.auth.get_user_by_session()
    if(self.session.get('localURL') =='false'):
      self.auth.unset_session()
      self.redirect(self.uri_for('home'))
    else:
      
      self.redirect(self.uri_for('switchboard'))
    

class AuthenticatedHandler(BaseHandler):
  @user_required
  def get(self):
    self.render_template('authenticated.html')
	
class AnotherAuthenticatedHandler(BaseHandler):
  @user_required
  def get(self):
    self.response.out.write('Hello Authenticated World')
    self.response.out.write(sys.path)