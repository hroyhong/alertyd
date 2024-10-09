from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import the routes after initializing the app
    from .routes import api
    app.register_blueprint(api)  # Register the API blueprint

    return app
