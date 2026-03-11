from flask import app

from .user import *
from .auth import *
from .initialize import *
from .badge import *
from .progress import *
from .event import *
from .redeemedReward import *

#test
from App.views.student_rewards import reward_student_views
app.register_blueprint(reward_student_views)