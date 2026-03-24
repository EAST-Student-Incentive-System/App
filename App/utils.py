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