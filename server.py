from typing import Any
from flask import Flask
from config import BaseConfig
from flask import Blueprint, request



def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def register_blueprints(server):
    server_bp = Blueprint('main', __name__)
    server.register_blueprint(server_bp)


class Server(Flask):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.config.from_object(BaseConfig)

        register_blueprints(self)
        @self.route('/shutdown', methods=['POST'])
        def shutdown():
            shutdown_server()
            return 'Server shutting down...'

    def kill(self):
        # open url to kill the server
        import requests
        requests.post("http://127.0.0.1:5000/shutdown")

