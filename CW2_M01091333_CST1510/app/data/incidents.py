import pandas as pd
from app.data.db import connect_database

#function to create incident
def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    conn = connect_database()
    cursor = conn.cursor()
    incident_id = None
    cursor.execute("""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    incident_id = cursor.lastrowid
    return incident_id

#Function to read incidents
def get_all_incidents():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC",conn)
    return df

#Function to udpate incident
def update_incident_status(incident_id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?",(new_status, incident_id))
    conn.commit()
    rows_affected = cursor.rowcount
    return rows_affected

#Function to delete incident
def delete_incident(incident_id):
    conn = connect_database()
    cursor = conn.cursor()
    rows_affected = 0
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    return rows_affected

#Code to get incident by its type
def get_incidents_by_type_count():
    conn = connect_database()
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

#Code for high severity incidents by their status
def get_high_severity_by_status():
    conn = connect_database()
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High' OR severity = 'Critical'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df