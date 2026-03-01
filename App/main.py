import os
from flask import Flask, render_template, request, redirect, url_for
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin


def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()

    @app.route('/reward', methods=['GET', 'POST'])
    @app.route('/reward/<int:reward_id>', methods=['GET', 'POST'])
    def edit_reward(reward_id=None):
        from App.models.reward import Reward
        from App.database import db

        reward = None
        if reward_id:
            reward = Reward.query.get(reward_id)
            if not reward:
                print(f"Reward with ID {reward_id} not found.")
                return "Reward not found", 404

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            point_cost = request.form['pointCost']
            active = 'active' in request.form

            if reward:
                # Update existing reward
                reward.name = name
                reward.description = description
                reward.pointCost = point_cost
                reward.active = active
            else:
                # Create a new reward
                reward = Reward(name=name, description=description, pointCost=point_cost, active=active)
                db.session.add(reward)

            db.session.commit()
            return redirect(url_for('rewards'))  # Redirect to the rewards list page

        return render_template('reward.html', reward=reward)

    return app