# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .badge import badge_views
from .admin import setup_admin
from .reward import reward_views
from .event import event_views
from .student_rewards import reward_student_views
from .progress import progress_views


# Add new reward_views blueprint to the views list
views = [user_views, index_views, auth_views, reward_views, badge_views, event_views, reward_student_views, progress_views] 