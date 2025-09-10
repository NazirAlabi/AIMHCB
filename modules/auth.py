import os
import hashlib
import logging


def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users(USER_DB_FILE):
    """Load users from file"""
    users = {}
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 5:  # Updated to handle phone number
                        username, email, name, phone, password_hash = parts
                        users[username] = {
                            'email': email,
                            'name': name,
                            'phone': phone,
                            'password_hash': password_hash
                        }
                    elif len(parts) == 4:  # Backward compatibility for existing users
                        username, email, name, password_hash = parts
                        users[username] = {
                            'email': email,
                            'name': name,
                            'phone': 'Not provided',
                            'password_hash': password_hash
                        }
    return users

def save_user(username, email, name, phone, password, USER_DB_FILE):
    """Save new user to file"""
    password_hash = hash_password(password)
    # Clean phone number (remove empty strings)
    phone = phone.strip() if phone else 'Not provided'
    try:
        if not os.path.exists(os.path.dirname(USER_DB_FILE)):
            os.makedirs(os.path.dirname(USER_DB_FILE))
        with open(USER_DB_FILE, 'a') as f:
            f.write(f"{username}|{email}|{name}|{phone}|{password_hash}\n")
    except Exception as e:
        pass

def authenticate_user(username, password, USER_DB_FILE):
    """Authenticate user"""
    users = load_users(USER_DB_FILE)
    if username in users:
        if users[username]['password_hash'] == hash_password(password):
            auth=True
            return (users[username])
    return None

def load_user_profile(username, PROFILE_DIR):
    """
    Load user's personal profile (pp) from a file
    """
    profile_file = os.path.join(PROFILE_DIR, f"{username}_profile.txt")
    if os.path.exists(profile_file):
        try:
            with open(profile_file, "r", encoding="utf-8") as f:
                profile_text = f.read()
            return profile_text
        except Exception as e:
            logging.error(f"❌ Failed to load profile for {username}: {e}")
            return ""
    else:
        return ""
    
def save_user_profile(username, profile_text, PROFILE_DIR):
    """
    Save user's personal profile (pp) to a file
    """
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    profile_file = os.path.join(PROFILE_DIR, f"{username}_profile.txt")
    try:
        with open(profile_file, "w", encoding="utf-8") as f:
            f.write(profile_text)
        return True
    except Exception as e:
        logging.error(f"❌ Failed to save profile for {username}: {e}")
        return False