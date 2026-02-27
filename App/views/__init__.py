# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .badge import badge_views
from .admin import setup_admin
from .reward import reward_views


# Add new reward_views blueprint to the views list
views = [user_views, index_views, auth_views, reward_views] 
# blueprints must be added to this list

from App.controllers.user import user
views = [user]