import pandas as pd
from app.data.db import connect_database
from datetime import datetime

#Function to create a ticket
def insert_ticket(ticket_id, priority, status, category, subject, description, assigned_to=None):
    conn = connect_database()
    cursor = conn.cursor()
    new_id = None
    created_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, assigned_to))
    conn.commit()
    new_id = cursor.lastrowid
    print(f"✅ Inserted ticket '{ticket_id}' with ID: {new_id}")
    return new_id

#Read ticket
def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    return df

#Update ticket
def update_ticket_status(ticket_id, new_status, is_resolved=False):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    
    if is_resolved and new_status.lower() in ['resolved', 'closed']:
        resolved_date = datetime.now().strftime("%Y-%m-%d")
        sql = "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE ticket_id = ?"
        params = (new_status, resolved_date, ticket_id)
    else:
        sql = "UPDATE it_tickets SET status = ? WHERE ticket_id = ?"
        params = (new_status, ticket_id)
           
    cursor.execute(sql, params)
    conn.commit()
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        print(f"✅ Updated status for ticket: {ticket_id}")
    return rows_affected

#Function to delete ticket
def delete_ticket(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        print(f"✅ Deleted ticket with ID: {ticket_id}")
    return rows_affected