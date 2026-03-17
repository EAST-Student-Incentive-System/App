from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.controllers import create_user, initialize
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models import User 

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/home', methods=['GET'])
def index_page():
    return render_template('index.html', title="Home")
    

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/about', methods=['GET'])
@jwt_required(optional=True)
def about():
    identity = get_jwt_identity()
    user = User.query.get(identity) if identity else None
    if user:
        return render_template('about.html', title="About", user=user)
    else:
        return render_template('about.html', title="About")