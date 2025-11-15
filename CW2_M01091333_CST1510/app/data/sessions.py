from app.data.db import connect_database

#Function to create a session
def create_session(username, token, timestamp):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (username, token, created_at) VALUES (?, ?, ?)",(username, token, timestamp))
    conn.commit()
