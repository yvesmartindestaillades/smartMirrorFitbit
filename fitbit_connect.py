#!/usr/bin/env python
import cherrypy
import os
import sys
import threading
import traceback
import webbrowser
import json
from urllib.parse import urlparse
from base64 import b64encode
from fitbit import Fitbit, FitbitOauth2Client
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
import datetime, time
from util import *
from cherrypy.process import servers
from firebase import firebase

def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

#######################################################################

# CANVAS STREAM CLASSES

#######################################################################


#######################################################################

class StreamData(Fitbit):
    
    def __init__(self, client_id, client_secret, access_token, refresh_token, redirect_uri='http://127.0.0.1:8080/'):
                    
        # Create a Fitbit instance with the access and refresh tokens
        super().__init__(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
        
    
    def get_hr(self, date=datetime.date.today()):
        return self.intraday_time_series('activities/heart', detail_level='1sec')
    
    def revoke_token(self):
        return self.make_request('https://api.fitbit.com/oauth2/revoke', data={'token':self.access_token}, method='POST')
        
    def refresh_hr(self):
        hr = self.get_hr(datetime.date.today())
        json.dump(hr, open('hr.json', 'w'))
        
    def get_name(self):
        if firebase.exists('name'):
            return firebase.read('name')
        return self.user_profile_get()['user']['firstName']

    def stop(self):
        self.activate_run = False
        
    def get_hr_canvas(self, date=datetime.date.today()):
        if firebase.exists('hr', date):
            return firebase.read('hr', date)
        return self.intraday_time_series('activities/heart', base_date=date, detail_level='1min')
    
    def get_sleep_canvas(self, date=datetime.date.today()):
        if firebase.exists('sleep', date):
            return firebase.read('sleep', date)
        return self.get_sleep(date)
    
    def get_devices_canvas(self):
        if firebase.exists('devices'):
            return firebase.read('devices')
        return self.get_devices()
    
    def get_activity_recent(self):
        if firebase.exists('activity'):
            return firebase.read('activity')
        url ="{0}/{1}/user/-/activities/recent.json".format(
            *self._get_common_args()
        )
        return self.make_request(url)

class OAuth2Server:
    def __init__(self, client_id, client_secret,
                 redirect_uri='http://127.0.0.1:8080/'):
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            timeout=10,
        )           
        
        # Start the server in a background thread
        self.redirect_uri = redirect_uri
        self.browser_authorize()
        profile = self.fitbit.user_profile_get()
        print('You are authorized to access data for the user: {}'.format(profile['user']['fullName']))
        
        # Save the access and refresh tokens for later use
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.fitbit.client.session.token['access_token']
        self.refresh_token = self.fitbit.client.session.token['refresh_token']
        
    def get_credentials(self):
        return self.client_id, self.client_secret
    
    def get_tokens(self):
        return self.access_token, self.refresh_token

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,1, 0)).start()

        # Same with redirect_uri hostname and port.
        urlparams = urlparse(self.redirect_uri)
        cherrypy.config.update({'server.socket_host': urlparams.hostname,
                                'server.socket_port': urlparams.port})

        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """
        Receive a Fitbit response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                self.fitbit.client.fetch_access_token(code)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()
        

