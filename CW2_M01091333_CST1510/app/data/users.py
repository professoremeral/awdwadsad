from app.data.db import connect_database

#Retrieves user by their username
def get_user_by_username(username):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    #fetchone returns id, username, password_hash, role, created at
    user = cursor.fetchone()
    conn.close()
    return user

#Function to create a new user
def insert_user(username, password_hash, role='user'):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",(username, password_hash, role))
    conn.commit()