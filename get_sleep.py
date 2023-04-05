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
import datetime

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

        self.redirect_uri = redirect_uri

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()

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


class StreamData(OAuth2Server):
    
    def __init__(self, client_id, client_secret, redirect_uri='http://127.0.0.1:8080/'):
        
        super().__init__(client_id, client_secret, redirect_uri)
        
        # Start the server in a background thread
        self.browser_authorize()
        profile = self.fitbit.user_profile_get()
        print('You are authorized to access data for the user: {}'.format(profile['user']['fullName']))
        
        # Save the access and refresh tokens for later use
        self.access_token = self.fitbit.client.session.token['access_token']
        self.refresh_token = self.fitbit.client.session.token['refresh_token']
        
        # Create a FitbitOauth2Client instance with the access and refresh tokens
        self.authd_client = Fitbit(client_id, client_secret, access_token=self.access_token, refresh_token=self.refresh_token)
       
    def get_sleep(self, date=datetime.date.today()):
        return self.authd_client.get_sleep(date)
    
    def get_sleep_phases(self, date=datetime.date.today()):
        return self.authd_client.make_request('{0}/{1}/user/sleep/date/{}.json'.format(self._get_common, date), method='GET')
    
    def revoke_token(self):
        return self.authd_client.make_request('https://api.fitbit.com/oauth2/revoke', data={'token':self.access_token}, method='POST')
        

def get_sleep_data():
    client_id, client_secret = json.load(open('fitbit_keys.json')).values()

    server = OAuth2Server(
        client_id=client_id,
        client_secret=client_secret,
        )
    server.browser_authorize()


    print('TOKEN\n=====\n')
    
    for key, value in server.fitbit.client.session.token.items():
        print('{} = {}'.format(key, value))
    
    
    user_id = server.fitbit.client.session.token['user_id']

    authd_client = Fitbit(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
    return authd_client.get_sleep(datetime.date(2023,3,21))
    

def revoke_token():
    oauth_client = FitbitOauth2Client(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
    print(oauth_client.make_request('https://api.fitbit.com/oauth2/revoke', data={'token':access_token}, method='POST'))

if __name__ == '__main__':
    print(get_sleep_data())
    # revoke_token()