from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from App.controllers.user import User, create_user
from App.database import db

from App.models import User, Staff, Student #! Student should be added in a future update
def signUp(email, username, password):
  # Check if email already exists
  existing_email = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
  if existing_email:
    return {'error': 'Email already registered.'}
  # Check if username already exists
  existing_username = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
  if existing_username:
    return {'error': 'Username already taken.'}
  # Create new user based on email domain
  user = create_user(email, username, password)

  return {'success': True, 'user': user.get_json() }

def login(username, password): # Login function that returns JWT token upon successful authentication and the role
  result = db.session.execute(db.select(User).filter_by(username=username))
  user = result.scalar_one_or_none()
  if user and user.check_password(password):
    access_token = create_access_token(identity=user)
    return {'access_token': access_token, 'user': user.get_json(), 'role': user.role}
  return {'error': 'Invalid username or password.'}

def logout():
  # In JWT, logout is typically handled on the client side by discarding the token.
  # Optionally, you can implement token revocation on the server side if needed.
  return {'success': True, 'message': 'Logout successful. Please discard the token on client side.'}

def change_password(email, old_password, new_password):
  result = db.session.execute(db.select(User).filter_by(email=email))
  user = result.scalar_one_or_none()
  if user and user.check_password(old_password):
    user.set_password(new_password)
    db.session.commit()
    return {'success': True, 'message': 'Password changed successfully.'}
  return {'error': 'Invalid email or old password.'}

def setup_jwt(app):
  jwt = JWTManager(app)

  # Always store a string user id in the JWT identity (sub),
  # whether a User object or a raw id is passed.
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user_id = getattr(identity, "id", identity)
    return str(user_id) if user_id is not None else None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # Cast back to int primary key
    try:
      user_id = int(identity)
    except (TypeError, ValueError):
      return None
    return db.session.get(User, user_id)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          identity = get_jwt_identity()
          user_id = int(identity) if identity is not None else None
          current_user = db.session.get(User, user_id) if user_id is not None else None
          is_authenticated = current_user is not None
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)
  


  #allow email to be parsed for uwi login, let signup use create used function from user, let the create user function determine role based on email pattern, reject non UWI emails, 
