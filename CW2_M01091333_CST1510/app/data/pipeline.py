import pandas as pd
from pathlib import Path
from app.data.db import connect_database

#Define paths
DATA_DIR = Path("DATA")

#Function to load data into table
def load_csv_to_table(conn, csv_path, table_name):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0
    df = pd.read_csv(csv_path)
    rows_loaded = len(df)
    # Use if_exists='append' to add to existing data without deleting
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    print(f"✅ Loaded {rows_loaded} rows into '{table_name}' from {csv_path.name}")
    return rows_loaded

#Function to create and load csv into database incase no csv is present yet
def create_and_load_all_csv_data(conn):
    print("\n[--- Loading CSV Data ---]")
    total_rows = 0
    
    #Create dummy cyber_incidents.csv
    incidents_csv = DATA_DIR / "cyber_incidents.csv"
    if not incidents_csv.exists():
        pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-03', '2024-01-04'],
            'incident_type': ['Phishing', 'Malware', 'DDoS', 'Phishing', 'Malware'],
            'severity': ['High', 'Medium', 'Critical', 'High', 'Low'],
            'status': ['Open', 'Resolved', 'Open', 'Investigating', 'Resolved'],
            'description': ['Phishing email', 'Malware detected', 'DDoS attack', 'CEO fraud', 'Adware'],
            'reported_by': ['alice', 'nova', 'alice', 'alice', 'nova'] 
        }).to_csv(incidents_csv, index=False)
        print("Created dummy 'cyber_incidents.csv'")

    #Create dummy datasets_metadata.csv
    datasets_csv = DATA_DIR / "datasets_metadata.csv"
    if not datasets_csv.exists():
        pd.DataFrame({
            'dataset_name': ['Traffic Data', 'Logs', 'User PII'],
            'category': ['Network', 'System', 'Compliance'],
            'source': ['Firewall', 'Server', 'HR'],
            'last_updated': ['2024-01-01', '2024-01-02', '2024-01-05'],
            'record_count': [1000, 5000, 200],
            'file_size_mb': [50.5, 120.0, 5.0]
        }).to_csv(datasets_csv, index=False)
        print("Created dummy 'datasets_metadata.csv'")

    #Create dummy it_tickets.csv
    tickets_csv = DATA_DIR / "it_tickets.csv"
    if not tickets_csv.exists():
        pd.DataFrame({
            'ticket_id': ['T-001', 'T-002', 'T-003'],
            'priority': ['High', 'Low', 'Medium'],
            'status': ['Open', 'Closed', 'In Progress'],
            'category': ['Hardware', 'Software', 'Network'],
            'subject': ['Broken laptop', 'Can\'t login', 'Slow wifi'],
            'description': ['Screen is cracked', 'Password reset needed', 'Wifi drops connection'],
            'created_date': ['2024-01-10', '2024-01-11', '2024-01-12'],
            'resolved_date': [None, '2024-01-11', None],
            'assigned_to': ['tech_support', 'admin', 'net_admin']
        }).to_csv(tickets_csv, index=False)
        print("Created dummy 'it_tickets.csv'")

    #Deletes old data to make sure no data is currently there
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents")
    cursor.execute("DELETE FROM datasets_metadata")
    cursor.execute("DELETE FROM it_tickets")
    conn.commit()
    print("Cleared old data from domain tables.")

    total_rows += load_csv_to_table(conn, incidents_csv, "cyber_incidents")
    total_rows += load_csv_to_table(conn, datasets_csv, "datasets_metadata")
    total_rows += load_csv_to_table(conn, tickets_csv, "it_tickets")
    
    print(f"Total rows loaded from all CSVs: {total_rows}")
    return total_rows