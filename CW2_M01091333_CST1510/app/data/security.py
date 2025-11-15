from app.data.db import connect_database
from datetime import datetime

#Function for lockout status 
def get_lockout_status(username):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT failed_attempts, last_attempt_time FROM lockout WHERE username = ?",(username,))
    status = cursor.fetchone()
    conn.close()
    
    if status:
        last_time = datetime.strptime(status[1], "%Y-%m-%d %H:%M:%S")
        return (status[0], last_time) 
    return (0, None) #No record, so 0 attempts

#Function to increment amount of failed attempts
def record_failed_attempt(username):
    conn = connect_database()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #If record doesn't exist, creates it 
    cursor.execute("INSERT OR IGNORE INTO lockout (username, failed_attempts, last_attempt_time) VALUES (?, 0, ?)",(username, now_str))
        
    #Update the records
    cursor.execute("""
        UPDATE lockout
        SET failed_attempts = failed_attempts + 1, last_attempt_time = ?
        WHERE username = ?
        """,
        (now_str, username))
    conn.commit()

#Function to reset lockout if they get password correct or if 5 minutes has passed
def reset_lockout(username):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lockout WHERE username = ?",(username,))
    conn.commit()
