import os
from datetime import timedelta
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask import flash, redirect, url_for, jsonify
import cloudinary
import cloudinary.uploader
def init_cloudinary():
    if os.environ.get("USE_CLOUDINARY", "false").lower() == "true":
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET")
        )



def load_config(app, overrides):
    if os.path.exists(os.path.join('./App', 'custom_config.py')):
        app.config.from_object('App.custom_config')
    else:
        app.config.from_object('App.default_config')
    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
    app.config["SENDGRID_API_KEY"] = os.environ.get("SENDGRID_API_KEY")
    app.config["BASE_URL"] = os.environ.get("BASE_URL", "http://localhost:8080")


    init_cloudinary()
    jwt = JWTManager(app)


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        flash("Session expired, please log in again.", "warning")
        response = redirect(url_for("auth_views.login_page"))
        unset_jwt_cookies(response) # clear expired cookies
        return response
   
   


    for key in overrides:
        app.config[key] = overrides[key]
