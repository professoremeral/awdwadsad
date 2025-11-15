import bcrypt
import string
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from app.data.db import DATA_DIR

# Import all necessary database functions
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.sessions import create_session
from app.data.security import get_lockout_status, record_failed_attempt, reset_lockout
from app.data.schema import create_users_table

#Function for password strength
def check_password_strength(password):
    #Flags to check if each character is present
    special = string.punctuation
    has_lower = False
    has_upper = False
    has_digit = False
    has_special = False
    
    #Length check
    if len(password) < 8:
        return "Weak"
        
    for char in password:
        if char.islower():
            has_lower = True
        elif char.isupper():
            has_upper = True
        elif char.isdigit():
            has_digit = True
        elif char in special:
            has_special = True
    
    if has_lower and has_upper and has_digit and has_special:
        if len(password) >= 12:
            return "Strong"
        else: 
            return "Medium"
    else:
        return "Weak"

#Function to check if valid username format
def validate_user(username):
    if len(username) < 3 or len(username) > 20:
        return False, 'Error: Username should be between 3 and 20 characters long.'
    for char in username:
        if not char.isalnum():
            return False, 'Error: Username can only contain letters and numbers.'
    return True, ""

#Function to check if valid password format
def validate_pass(password):
    """Function to validate password."""
    if len(password) < 6 or len(password) > 50:
        return False, 'Error: Password should be between 6 and 50 characters long.'
    return True, ""


#Check if username exists
def check_user_exists(username):
    return get_user_by_username(username) is not None

#Function to register user
def register_user(username, password, group_num):
    
    #Check if username already exists 
    if check_user_exists(username):
        return False, f'Username{username} already exists, please enter a different one.'
    
    # Hashing the password
    pass_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashpass = bcrypt.hashpw(pass_bytes, salt).decode("utf-8")
    
    #Group assignment
    if group_num == 1:
        group = "Cybersecurity Analyst"
    elif group_num == 2: 
        group = "Data Scientist"
    elif group_num == 3:
        group = "IT Administrator"
    else:
        group = "user" # Default
        
    #Storing in database
    insert_user(username, hashpass, group)
    return True, f"User: {username} is now registered."

#Function to login user
def login_user(username, password):
    
    #Check if user is locked out
    is_locked, msg = check_lockout(username)
    if is_locked:
        return False, msg

    #Check whether the username is correct
    user_data = get_user_by_username(username)
    if not user_data:
        return False, "Incorrect username or this user doesn't exist."

    #Check for password match
    stored_hash = user_data[2] # password_hash
    pass_bytes = password.encode("utf-8")
    stored_bytes = stored_hash.encode("utf-8")
    
    if bcrypt.checkpw(pass_bytes, stored_bytes):
        #If password is correct, resets whatever lockout and creates a session token
        reset_lockout(username)
        token, timestamp_str, timestamp_obj = _create_token_entry(username)
        return True, f'Successfully logged in {username}, your session token is: {token}'
    else:
        #Records attempt, if it hits 3, automatically locks out user and does not allow for retry
        record_failed_attempt(username)
        attempts, last_time = get_lockout_status(username)
        if attempts >= 3:
            return False, f"User - {username} is now locked out due to three failed attempts.\nPlease try again after 5 minutes."
        return False, "Incorrect password, please try again."

#Token creation for the session
def _create_token_entry(username):
    token = secrets.token_hex(16)
    timestamp = datetime.now()
    strtimestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    create_session(username, token, strtimestamp)
    return token, timestamp.strftime("%H:%M:%S"), timestamp

#Check if the user is currently locked out
def check_lockout(username):
    attempts, last_time = get_lockout_status(username)
    
    if attempts >= 3:
        if last_time and (datetime.now() - last_time < timedelta(minutes=5)):
            return True, f"Your account '{username}' is locked, please try again 5 minutes after you have been locked out."
        else:
            # Lockout expired, reset it
            reset_lockout(username)
            return False, ""
    return False, ""

#Function to migrate data from textfile
def migrate_users_from_file(filepath=DATA_DIR):
    print("Attempting to migrate users from text file...")
    file_path = Path(filepath)
    
    if not file_path.exists():
        print(f"This location doesn't exist. Please validate your files.")
        return

    conn = connect_database()
    create_users_table(conn) # Ensure table exists
    conn.close()
    
    migrated = 0
    skipped = 0
    
    with open(file_path, 'r') as f:
        
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            parts = line.split(',', 2)
            if len(parts) < 3:
                print(f"Skipping malformed line: {line}")
                skipped += 1
                continue  
            
            username, password_hash, role = parts   
            if not get_user_by_username(username):
                insert_user(username, password_hash, role)
                print(f"User '{username}' migrated successfully.")
                migrated += 1
            else:
                print(f"User '{username}' already exists. Skipping.")
                skipped += 1
    print(f"User migration complete. Migrated: {migrated}, Skipped: {skipped}")
    