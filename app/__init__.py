import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
        
    from . import api
    app.register_blueprint(api.bp)
    
    from . import background
    background.init_stock_check()

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    return app