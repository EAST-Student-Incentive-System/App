
from App.models import Student, Staff, User
from App.database import db
from better_profanity import profanity

profanity.load_censor_words()

def is_valid_username(username):

    username = username.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if len(username) > 20:
        return False, "Username must be 20 character or less."
    
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    
    if profanity.contains_profanity(username):
        return False, "Username contains inappropriate language."
    
    return True, None


def require_role(user_id, *roles):
    """
    Ensure the user has one of the allowed roles.
    Raises PermissionError if not.
    """
    user = db.session.get(User, user_id)
    if not user or user.role not in roles:
        raise PermissionError(f"Unauthorized: requires role {roles}")
    return user

import os
from flask import current_app
from werkzeug.utils import secure_filename
import cloudinary.uploader

def handle_image_upload(image_file):
    if not image_file or not image_file.filename:
        return None

    if os.environ.get("USE_CLOUDINARY", "false").lower() == "true":
        result = cloudinary.uploader.upload(image_file)
        return result["secure_url"]
    else:
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join(current_app.static_folder, "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image_file.save(filepath)
        return filename
